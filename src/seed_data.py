import sys
import os

# Agregamos la carpeta raíz del proyecto al sistema para que Python encuentre 'src'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.database import SessionLocal, init_db, Hospital, Especialidad, Medico, Turno
from datetime import datetime, timedelta
import random

def poblar_db():
    print("🌱 Sembrando base de datos con información de prueba...")
    
    # Inicializar tablas
    init_db()
    db = SessionLocal()
    
    # Limpieza previa (opcional, para no duplicar si corres el script varias veces)
    db.query(Turno).delete()
    db.query(Medico).delete()
    db.query(Hospital).delete()
    db.query(Especialidad).delete()
    db.commit()

    # 1. Crear Especialidades (Las que tu modelo predice)
    especialidades = [
        "CARDIOLOGÍA/CIRCULATORIO", "DERMATOLOGÍA", "ENDOCRINOLOGÍA/NUTRICIÓN", "GASTROENTEROLOGÍA/DIGESTIVO", 
        "GINECOLOGÍA/OBSTETRICIA", "INFECCIOSAS/PARASITARIAS", "MEDICINA GENERAL", "NEUROLOGÍA",
        "ODONTOLOGÍA", "OFTALMOLOGÍA/ORL", "ONCOLOGÍA (TUMORES)", "PEDIATRÍA", "PSIQUIATRÍA/MENTAL",
        "RESPIRATORIO/NEUMOLOGÍA", "SANGRE/INMUNOLOGÍA", "TRAUMATOLOGÍA/MUSCULAR", "URGENCIAS/TRAUMA",
        "UROLOGÍA/RENAL"
    ]
    
    # Diccionario para guardar referencias
    db_esps = {}
    
    # Verificar si ya existen para no duplicar
    for esp in especialidades:
        existe = db.query(Especialidad).filter_by(nombre=esp).first()
        if not existe:
            e = Especialidad(nombre=esp)
            db.add(e)
            db.commit()
            db.refresh(e)
            db_esps[esp] = e
        else:
            db_esps[esp] = existe

    # 2. Crear Hospitales (Ecuador)
    lista_hospitales = [
        {"nombre": "Hospital IESS Quito Sur", "tipo": "Hospital de Especialidades", "direccion": "Sur"},
        {"nombre": "Hospital Eugenio Espejo", "tipo": "Hospital General", "direccion": "Centro"},
        {"nombre": "Centro de Salud Carapungo", "tipo": "Centro de Salud Tipo C", "direccion": "Norte"},
        {"nombre": "Dispensario El Batán", "tipo": "Centro de Salud Tipo A", "direccion": "Norte"}
    ]
    
    db_hospitales = []
    for h_data in lista_hospitales:
        existe = db.query(Hospital).filter_by(nombre=h_data["nombre"]).first()
        if not existe:
            h = Hospital(**h_data)
            db.add(h)
            db.commit()
            db.refresh(h)
            db_hospitales.append(h)
        else:
            db_hospitales.append(existe)

    # 3. Crear Médicos y Turnos
    # Generar turnos para los próximos 3 días
    count_turnos = 0
    for hosp in db_hospitales:
        for esp_name, esp_obj in db_esps.items():
            
            # Lógica realista: Los dispensarios pequeños no tienen Neurocirujanos
            if hosp.tipo == "Centro de Salud Tipo A" and esp_name in ["NEUROLOGÍA", "CARDIOLOGÍA/CIRCULATORIO", "TRAUMATOLOGÍA/MUSCULAR"]:
                continue
                
            # Crear médico si no existe
            nombre_medico = f"Dr. {esp_name[:3].title()} - {hosp.nombre.split()[0]} {hosp.nombre.split()[-1]}"
            medico = db.query(Medico).filter_by(nombre=nombre_medico).first()
            
            if not medico:
                medico = Medico(nombre=nombre_medico, hospital=hosp, especialidad=esp_obj)
                db.add(medico)
                db.commit()
                db.refresh(medico)
            
            # Crear 5 turnos por médico (Horarios aleatorios)
            for _ in range(5):
                # Turno entre mañana y pasado mañana, horario laboral (8am - 4pm)
                dias_futuro = random.randint(0, 2)
                hora_dia = random.randint(8, 16)
                minuto = random.choice([0, 30])
                
                fecha_turno = datetime.now().replace(minute=minuto, second=0, microsecond=0) + timedelta(days=dias_futuro, hours=hora_dia - datetime.now().hour)
                
                # Solo crear si es futuro
                if fecha_turno > datetime.now():
                    turno = Turno(medico=medico, fecha_hora=fecha_turno)
                    db.add(turno)
                    count_turnos += 1
    
    db.commit()
    print(f"✅ Base de datos poblada con éxito: {len(db_hospitales)} hospitales y {count_turnos} turnos creados.")

if __name__ == "__main__":
    poblar_db()