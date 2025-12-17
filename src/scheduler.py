from sqlalchemy.orm import Session
from src.database import Turno, Medico, Hospital, Especialidad
from datetime import datetime

def buscar_mejor_turno(db: Session, especialidad_predicha: str, nivel_manchester: int):
    """
    Algoritmo de asignación de citas basado en prioridad médica.
    """
    
    # 1. Determinar el Tipo de Hospital requerido según Manchester
    if nivel_manchester <= 2:
        # ROJO/NARANJA: Necesita Hospital de Especialidades/Tercer Nivel (Shock Room)
        tipos_hospital = ["Hospital de Especialidades", "Hospital General"]
        urgencia_vital = True
    elif nivel_manchester == 3:
        # AMARILLO: Hospital General o Centro Tipo C
        tipos_hospital = ["Hospital General", "Centro de Salud Tipo C"]
        urgencia_vital = False
    else:
        # VERDE/AZUL: Primer Nivel (Dispensarios)
        tipos_hospital = ["Centro de Salud Tipo A", "Centro de Salud Tipo B", "Dispensario"]
        urgencia_vital = False

    # 2. Filtrar turnos disponibles
    # Buscamos: 
    # - Especialidad correcta
    # - Hospital del tipo adecuado (Según Manchester)
    # - Que esté disponible
    # - Ordenado por fecha (lo más pronto posible)
    
    consulta = (
        db.query(Turno)
        .join(Medico)
        .join(Hospital)
        .join(Especialidad)
        .filter(Turno.disponible == True)
        .filter(Especialidad.nombre == especialidad_predicha)
        .filter(Hospital.tipo.in_(tipos_hospital))
        .filter(Turno.fecha_hora >= datetime.now())
        .order_by(Turno.fecha_hora.asc()) # El más próximo primero
    )
    
    mejor_turno = consulta.first()
    
    if not mejor_turno:
        # Fallback: Si no hay en el nivel correcto, buscar en cualquier nivel superior
        # (Mejor que lo atiendan en un hospital grande a que no lo atiendan)
        consulta_backup = (
            db.query(Turno)
            .join(Medico)
            .join(Especialidad)
            .filter(Turno.disponible == True)
            .filter(Especialidad.nombre == especialidad_predicha)
            .filter(Turno.fecha_hora >= datetime.now())
            .order_by(Turno.fecha_hora.asc())
        )
        mejor_turno = consulta_backup.first()

    return mejor_turno, urgencia_vital