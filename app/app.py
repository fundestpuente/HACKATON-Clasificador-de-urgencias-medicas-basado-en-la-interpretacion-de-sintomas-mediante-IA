import streamlit as st
import numpy as np
import pickle
import os
import sys
import time
import requests
from pathlib import Path
from audio_recorder_streamlit import audio_recorder

# --- CONFIGURACIÓN DE RUTAS ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src import config
from src.data_utils import limpiar_texto_medico
from src.manchester import calcular_prioridad
from src.derivacion import calcular_derivacion
from src.voice_recognition import transcribe_audio, append_text

# --- CONFIGURACIÓN DE API (Backend de Citas) ---
API_URL = "http://127.0.0.1:8000/triaje/agendar"

# --- FUNCIONES AUXILIARES DE TEMPLATES ---
TEMPLATES_DIR = Path(__file__).parent / "templates"
ASSETS_DIR = Path(__file__).parent / "assets"


def load_template(filename: str) -> str:
    """Carga un template HTML/CSS."""
    try:
        with open(TEMPLATES_DIR / filename, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"<!-- Template {filename} no encontrado -->"


def load_css() -> str:
    """Carga los estilos CSS."""
    content = load_template('styles.css')
    if content:
        return f"<style>\n{content}\n</style>"
    return ""

def limpiar_texto():
    st.session_state.input_text_area = ""
    st.session_state.texto_completo = ""


# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="TrIAje 593",
    page_icon="assets/favicon.ico",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cargar estilos visuales
st.markdown(load_css(), unsafe_allow_html=True)


# --- CARGA DE MODELOS LOCALES ---
@st.cache_resource
def load_models():
    try:
        if not os.path.exists(config.MODEL_SVM_PATH) or not os.path.exists(config.LABEL_ENCODER_PATH):
            return None, None

        with open(config.MODEL_SVM_PATH, 'rb') as f:
            model = pickle.load(f)

        with open(config.LABEL_ENCODER_PATH, 'rb') as f:
            le = pickle.load(f)

        return model, le
    except Exception as e:
        st.error(f"Error técnico: {e}")
        return None, None


model, le = load_models()

# --- SIDEBAR (BARRA LATERAL) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3063/3063176.png", width=80)
    st.image(str(ASSETS_DIR / "logo.png"), width=100)
    st.title("Bienvenido")
    st.caption("Sistema de Clasificación Médica")
    st.divider()

    st.info("**Instrucciones:**\nDescribe los síntomas del paciente con el mayor detalle posible para obtener una predicción precisa.")

    st.divider()

    # Estado del sistema
    st.markdown("### 📡 Estado del Sistema")
    try:
        # Hacemos un ping rápido a la raíz o docs para ver si vive
        r = requests.get("http://127.0.0.1:8000/docs", timeout=2)
        if r.status_code == 200 and model:
            st.success("● Sistema En Línea")
    except:
        st.error("● Sistema Desconectado")

# --- PANEL PRINCIPAL ---
col_header, col_logo = st.columns([3, 1])
with col_header:
    st.title("Asistente de Triaje Inteligente")
    st.markdown("""
    **Diagnóstico IA + Gestión Automática de Turnos (IESS/MSP)**
    _Describa los síntomas o use el micrófono para agendar una cita automáticamente._
    """)

# Si no hay modelo, detenemos la app visualmente
if not model:
    st.warning(
        "⚠️ **Atención:** Debes entrenar el modelo antes de usar la app. Ejecuta `python src/train.py` en tu terminal.")
    st.stop()

# Área de entrada
col_input, col_help = st.columns([3, 2])
with col_input:
    # Estado para el texto
    if 'input_text_area' not in st.session_state:
        st.session_state.texto_completo = ""

    # Label con micrófono integrado
    col_label, col_mic = st.columns([10, 1])
    with col_label:
        st.markdown("#### 📝 Ingreso de sintomas.")
    with col_mic:
        # Componente de grabación de audio compacto
        audio_bytes = audio_recorder(
            text="",
            recording_color="#e74c3c",
            neutral_color="#3498db",
            icon_name="microphone",
            icon_size="2x"
        )
    # Procesar el audio cuando esté disponible
    # Inicializar variable para rastrear el último audio procesado
    if 'ultimo_audio_procesado' not in st.session_state:
        st.session_state.ultimo_audio_procesado = None
    # Procesar solo si hay audio Y es diferente al último procesado
    if audio_bytes and audio_bytes != st.session_state.ultimo_audio_procesado:
        # Guardamos este audio como procesado para que no se repita en el rerun
        st.session_state.ultimo_audio_procesado = audio_bytes

        with st.spinner("🔄 Transcribiendo audio..."):
            success, texto_transcrito, error_msg = transcribe_audio(audio_bytes)

            if success:
                # 1. Calculamos el nuevo texto completo
                nuevo_texto = append_text(
                    st.session_state.input_text_area,
                    texto_transcrito
                )

                # 2. Actualizamos la variable de almacenamiento
                st.session_state.input_text_area = nuevo_texto

                st.success(f"✅ Transcrito correctamente")
                time.sleep(0.5)
                st.rerun()

            else:
                if "no se pudo entender" in error_msg.lower():
                    st.warning(f"⚠️ {error_msg}")
                else:
                    st.error(f"❌ {error_msg}")

    texto_input = st.text_area(
        label="Descripción del caso",
        placeholder="Ej: Paciente presenta dolor precordial, sudoración fría y dificultad para respirar...",
        height=150,
        key="input_text_area",
        label_visibility="collapsed"
    )

    # Actualizar el estado si se edita manualmente
    st.session_state.texto_completo = texto_input

    #  Botones de acción
    col_btn_1, col_btn_2 = st.columns([2, 4])
    with col_btn_1:
        analizar_btn = st.button("🔍 Analizar", type="primary", use_container_width=True)
    with col_btn_2:
        st.button("🗑️ Limpiar", type="secondary", use_container_width=True, on_click=limpiar_texto)

with col_help:
    st.markdown("#### ❓ ¿Cómo describir los síntomas?")
    st.markdown("""
    - Sé lo más detallado posible
    - Incluye duración, intensidad y factores asociados

    **Ejemplos:**
    - "Dolor abdominal intenso desde hace 2 horas, náuseas y vómitos"
    - "Fiebre alta de 39°C, tos seca y dificultad para respirar"
    """)

    st.info("💡 **Tip**: Puedes combinar dictado y escritura. El audio se convierte a texto que puedes editar.")

# --- LÓGICA PRINCIPAL ---
if analizar_btn and texto_input:
    if len(texto_input) < 5:
        st.warning("⚠️ La descripción es muy corta. Por favor detalla más los síntomas.")
    else:
        # Barra de progreso visual
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            # 1. Procesamiento Local (Para Gráficos y UX inmediata)
            status_text.text("🧹 Procesando lenguaje natural...")
            progress_bar.progress(20)
            texto_limpio = limpiar_texto_medico(texto_input)

            # Calculamos probabilidades locales para el gráfico
            pred_probs = model.predict_proba([texto_limpio])[0]
            max_idx = np.argmax(pred_probs)
            confidence = pred_probs[max_idx]
            especialidad_pred = le.inverse_transform([max_idx])[0]

            # 2. Llamada a la API (Para Agendamiento Real)
            status_text.text("Connecting to Hospital Database...")
            progress_bar.progress(50)

            payload = {"texto": texto_input}
            start_time = time.time()

            # --- PETICIÓN HTTP ---
            response = requests.post(API_URL, json=payload, timeout=10)
            # ---------------------

            progress_bar.progress(100)
            status_text.empty()
            progress_bar.empty()

            if response.status_code == 200:
                data = response.json()

                # Extraer datos de la API
                ia_data = data.get("analisis_ia", {})
                triaje_data = data.get("triaje_prioridad", {})
                cita_data = data.get("agendamiento", {})

                # Mapeo de datos para visualización
                especialidad_pred = ia_data.get("especialidad_detectada", "Desconocido")
                confianza_str = ia_data.get("nivel_confianza", "0%")

                # --- SECCIÓN 1: RESULTADOS CLÍNICOS ---
                st.divider()
                st.subheader("📋 Resultados del Análisis")

                col_res1, col_res_3 = st.columns([2, 2])

                with col_res1:
                    # Tarjeta de Diagnóstico
                    if confidence > 0.8:
                        st.success(f"### {especialidad_pred}")
                        st.caption("Nivel de certeza: Alto")
                    elif confidence > 0.5:
                        st.warning(f"### {especialidad_pred}")
                        st.caption("Nivel de certeza: Medio (Revisar)")
                    else:
                        st.error(f"### {especialidad_pred}")
                        st.caption("Nivel de certeza: Bajo (Requiere valoración humana)")

                with col_res_3:
                    triaje = calcular_prioridad(texto_input)

                    template = load_template("triaje_card.html")
                    html = template.format(
                        nivel=triaje['nivel'],
                        nombre=triaje['nombre'],
                        color=triaje['color'],
                        tiempo=triaje['tiempo']
                    )
                    st.markdown(html, unsafe_allow_html=True)

                # --- SECCIÓN 2: TICKET DE AGENDAMIENTO (FUSIÓN CLAVE) ---
                st.divider()
                derivacion = calcular_derivacion(triaje['nivel'], especialidad_pred)
                st.subheader("🗓️ Gestión Automática de Citas")

                if cita_data and "centro_medico" in cita_data:
                    # Diseño de Ticket Profesional
                    with st.container(border=True):
                        col_ticket_icon, col_ticket_info = st.columns([1, 5])

                        with col_ticket_icon:
                            # Icono centrado
                            st.markdown("<div style='text-align:center; font-size: 60px; padding-top: 20px;'>🏥</div>",
                                        unsafe_allow_html=True)

                        with col_ticket_info:
                            st.markdown(f"### {cita_data.get('centro_medico')}")
                            st.markdown(f"**📍 Dirección:** {cita_data.get('direccion')}")
                            st.markdown(f"**👨‍⚕️ Especialista:** {cita_data.get('medico')}")

                            c1, c2, c3 = st.columns([1.3, 0.75, 2])
                            c1.metric("Fecha", cita_data.get('fecha'))
                            c2.metric("Hora", cita_data.get('hora'))
                            c3.metric("Estado", cita_data.get('estado'))

                            tipo_atencion = cita_data.get("tipo_atencion", "")
                            if "EMERGENCIA" in tipo_atencion:
                                st.error(f"⚠️ **PRIORIDAD:** {tipo_atencion}")
                            else:
                                st.success(f"✅ **TIPO:** {tipo_atencion}")
                else:
                    # Fallback si no hay cita
                    st.warning(
                        f"⚠️ {cita_data.get('accion', 'No se pudo agendar automáticamente. Acuda a ventanilla.')}")

            else:
                st.error(f"Error en el servidor API (Status: {response.status_code})")
                st.code(response.text)

        except requests.exceptions.ConnectionError:
            st.error("❌ No se pudo conectar con la API de Agendamiento.")
        except Exception as e:
            st.error(f"Error inesperado: {e}")

elif analizar_btn and not texto_input:
    st.error("❌ Por favor ingrese el texto o use el micrófono.")