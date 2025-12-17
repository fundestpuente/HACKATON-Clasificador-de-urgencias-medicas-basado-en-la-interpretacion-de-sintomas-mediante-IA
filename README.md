# 🏥 TrIAje 593: Sistema de Clasificación y Agendamiento Médico Inteligente

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-green)
![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-336791)
![Status](https://img.shields.io/badge/Status-Hackathon_Ready-orange)

**TrIAje 593** es una plataforma integral de **e-Health** diseñada para optimizar los servicios de urgencias en Ecuador (IESS/MSP). Utiliza Inteligencia Artificial para interpretar síntomas (incluso con modismos locales), clasificar la gravedad del paciente y **agendar automáticamente citas médicas** en la red de salud pública, reduciendo la saturación hospitalaria.

---

## 🚀 Características Principales

### 1. 🧠 IA con Adaptación Cultural
* **NLP Híbrido:** Modelo SVM optimizado con TF-IDF capaz de interpretar descripciones clínicas complejas.
* **Diccionario de Modismos:** Entiende jerga ecuatoriana (ej: *"me duele la boca del estómago"*, *"tengo chuchaqui"*) y la traduce a terminología médica estándar antes del análisis.

### 2. 🗓️ Agendamiento Automatizado (End-to-End)
* **Gestión de Turnos Real:** Conexión a base de datos **PostgreSQL** para consultar disponibilidad de médicos en tiempo real.
* **Lógica de Derivación:** Asigna el centro de salud correcto según la gravedad:
    * 🔴 **Emergencia:** Hospital de Especialidades (Turno inmediato/Shock Room).
    * 🟢 **Consulta General:** Centro de Salud Tipo A/B (Cita programada).

### 3. 🎙️ Accesibilidad por Voz
* **Entrada Multimodal:** Permite a los pacientes dictar sus síntomas mediante voz.
* **Speech-to-Text:** Transcripción automática para facilitar el uso a personas con dificultades de escritura o en zonas rurales.

### 4. 🚨 Triaje Manchester Digital
* Implementación automatizada del **Protocolo de Manchester**.
* Clasifica al paciente en 5 niveles de urgencia (Rojo a Azul) basándose en palabras clave de riesgo vital (*Red Flags*).

---

## 🏗️ Arquitectura del Sistema

El proyecto sigue una arquitectura de microservicios moderna:

```mermaid
graph LR
A["Usuario (Voz/Texto)"] -- Frontend --> B(Streamlit App)
B -- HTTP Requests --> C{FastAPI Backend}
C -- Predicción --> D["Modelo IA (SVM)"]
C -- SQL Queries --> E["(PostgreSQL DB)"]
E -- Disponibilidad --> C
C -- JSON Response --> B
```

---

## 📂 Estructura del Proyecto

El proyecto sigue una arquitectura modular para facilitar la escalabilidad y el mantenimiento:

```text
SIC-Clasificador-Urgencias/
├── app/                   # Frontend (Interfaz de Usuario)
│   ├── app.py             # Aplicación principal Streamlit
│   └── templates/         # Componentes HTML/CSS para UI avanzada
│
├── data/                           # Almacenamiento de datos
│   ├── raw/                        # Datos crudos (CodiEsp, MTSamples original)
│   └── processed/                  # Datos limpios y unificados listos para el modelo
│   └── external/                   # Graficos para reportes estadisticos, etc
│
├── models/                         # Artefactos del modelo
│   ├── modelo_triaje_svm.pickle    # El cerebro (Pipeline entrenado)
│   └── label_encoder_final.pickle  # Diccionario de traducción (Número -> Especialidad)
│
├── notebooks/                      # Laboratorio de experimentación
│   ├── 1.0-obtencion-datos.ipynb   # Descarga, traducción y unificación
│   ├── 2.0-preprocesamiento.ipynb  # Limpieza NLP y codificación
│   └── 3.0-entrenamiento.ipynb     # Entrenamiento, evaluación y análisis de errores
│
├── src/                   # Backend y Lógica de Negocio
│   ├── api.py             # API REST (FastAPI) - Cerebro del sistema
│   ├── database.py        # Modelos ORM (SQLAlchemy)
│   ├── scheduler.py       # Algoritmo de asignación de citas
│   ├── manchester.py      # Lógica de triaje y gravedad
│   ├── voice_recognition.py # Módulo de transcripción de audio
│   └── train.py           # Script de entrenamiento del modelo
│
├── requirements.txt                # Dependencias del proyecto
└── README.md                       # Documentación
```
---
## 📝 Creditos
### Desarrolladorres:
- Axel Steven Anzules V.
- Stefany Michelle Perachimba P.
- Mateo Steven Mosquera A.
- Cristian Stiven Pusda H.

---

## Datos: 
Basado en el corpus CodiEsp (Plan de Impulso de las Tecnologías del Lenguaje) y MTSamples.

---

## 🛠️ Instalación y Despliegue
Sigue estos pasos para levantar el sistema completo en tu máquina local:

### Prerrequisitos:
- Python 3.8+ 
- PostgreSQL instalado y corriendo.

#### 1. Configuración del Entorno:
   ```aiignore
   # Clonar repositorio
   git clone https://github.com/fundestpuente/HACKATON-Clasificador-de-urgencias-medicas-basado-en-la-interpretacion-de-sintomas-mediante-IA
   cd HACKATON-Clasificador-de-urgencias-medicas-basado-en-la-interpretacion-de-sintomas-mediante-IA
   
   # Crear entorno virtual
   python -m venv venv
   - En Windows:
   venv\Scripts\activate

   - En Mac/Linux:
   source venv/bin/activate
   
   # Instalar dependencias
   pip install -r requirements.txt
   python -m spacy download es_core_news_sm
   ```
#### 2. Configuración de Base de Datos**
   1. Crea una base de datos en Postgres llamada "triaje_db".
   2. Configura tus credenciales en src/database.py:
      ```
      DATABASE_URL = "postgresql://usuario:password@localhost/triaje_db"
      ```
   3. Poblar datos de prueba: Ejecuta el script para crear hospitales, médicos y turnos ficticios.
      ```
      python src/seed_data.py
      ```
#### 3. Descargar el modelo de lenguaje (Spacy)
- Terminal 1: Backend (API)
    ```aiignore
    uvicorn src.api:app --reload
    # La API correrá en [http://127.0.0.1:8000](http://127.0.0.1:8000)
    ```
- Terminal 2: Frontend (App)
    ```aiignore
    streamlit run app/app.py
    # La App se abrirá en http://localhost:8501
    ```
---
## 🧪 Cómo Probar la Demo
### Escenario 1: Emergencia Vital
1. **Entrada:** "Mi abuelo se cayó, no responde y tiene un sangrado fuerte en la cabeza."
2. **Resultado Esperado:**
   - _Diagnóstico:_ Traumatología / Neurología. 
   - _Triaje:_ 🔴 Nivel 1 (Emergencia). 
   - _Acción:_ Reserva inmediata en Hospital de Especialidades.

### Escenario 2: Consulta General con Modismos
1. **Entrada (Voz o Texto):** "Me duele la boca del estómago y estoy con cursos desde ayer."
2. **Resultado Esperado:**
   - _Interpretación:_ Epigastralgia + Diarrea. 
   - _Diagnóstico:_ Gastroenterología. 
   - _Triaje:_ 🟡 Nivel 3 (Urgente) o 🟢 Nivel 4. 
   - _Acción:_ Propuesta de cita en Centro de Salud Tipo C.
---
## 📊 Tecnologías Utilizadas
- **Lenguaje:** Python 
- **Machine Learning:** Scikit-learn (SVM), Spacy (NLP), TF-IDF. 
- **Web Framework:** Streamlit (UI), HTML/CSS Custom Components. 
- **API Framework:** FastAPI, Pydantic. 
- **Base de Datos:** PostgreSQL, SQLAlchemy. 
- **Audio:** SpeechRecognition, PyAudio.
---
_Este proyecto es un prototipo funcional diseñado con fines académicos y de demostración tecnológica._