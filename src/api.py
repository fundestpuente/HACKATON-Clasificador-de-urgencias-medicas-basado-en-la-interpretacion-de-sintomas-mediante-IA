from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from src.database import SessionLocal, init_db
from src.predict import load_artifacts, predict_single
from src.manchester import calcular_prioridad
from src.scheduler import buscar_mejor_turno

app = FastAPI(title="API TrIAje 593 (SVM Version)")

# --- INICIALIZACIÓN ---
# 1. Crear tablas en la DB si no existen
init_db()

# 2. Cargar el modelo SVM y el Encoder (Artefactos) al arrancar la API
print("⏳ Iniciando API y cargando modelo SVM...")
try:
    model, le = load_artifacts()
    print("✅ Modelo SVM cargado en memoria.")
except Exception as e:
    print(f"❌ Error cargando modelo: {e}")
    # En producción esto debería detener la app, pero para pruebas lo dejamos pasar
    model, le = None, None

# Dependencia para obtener la sesión de DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Modelo de entrada (Lo que envía el usuario)
class SintomasRequest(BaseModel):
    texto: str

@app.post("/triaje/agendar")
def procesar_caso(request: SintomasRequest, db: Session = Depends(get_db)):
    if not model:
        raise HTTPException(status_code=500, detail="El modelo IA no está cargado.")

    # 1. Predicción IA (Usando tu SVM existente)
    # predict_single devuelve: (especialidad, confianza, texto_limpio)
    especialidad, confianza, _ = predict_single(request.texto, model, le)
    
    # 2. Cálculo Manchester (Reglas de gravedad)
    triaje = calcular_prioridad(request.texto)
    
    # 3. Agendamiento Automático (Lógica de DB)
    # Busca turno según la especialidad predicha y el nivel de gravedad
    turno, es_vital = buscar_mejor_turno(db, especialidad, triaje['nivel'])
    
    # Construir respuesta JSON
    respuesta = {
        "analisis_ia": {
            "especialidad_detectada": especialidad,
            "nivel_confianza": f"{confianza:.2%}",
            "modelo": "SVM Híbrido"
        },
        "triaje_prioridad": {
            "nivel": triaje['nivel'],
            "descripcion": triaje['nombre'],
            "color": triaje['color']
        },
        "agendamiento": None
    }
    
    if turno:
        # Reservar el turno (cambiar disponible a False)
        turno.disponible = False
        db.commit()
        
        respuesta["agendamiento"] = {
            "estado": "CITA CONFIRMADA",
            "centro_medico": turno.medico.hospital.nombre,
            "direccion": turno.medico.hospital.direccion,
            "tipo_atencion": "EMERGENCIA VITAL" if es_vital else "Consulta Prioritaria",
            "medico": turno.medico.nombre,
            "fecha": turno.fecha_hora.strftime("%Y-%m-%d"),
            "hora": turno.fecha_hora.strftime("%H:%M")
        }
    else:
        # Fallback si no hay médicos en la base de datos para esa especialidad
        respuesta["agendamiento"] = {
            "estado": "SIN DISPONIBILIDAD AUTOMÁTICA",
            "accion": "Acudir a triaje físico inmediatamente" if triaje['nivel'] <= 3 else "Intentar agendamiento manual"
        }
        
    return respuesta