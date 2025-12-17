from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
import os

# --- CONFIGURACIÓN --- 
# 'sqlite:///./citas_medicas.db'.
DATABASE_URL = "postgresql://postgres:Ax3!-1709@localhost/triaje_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- MODELOS (TABLAS) ---

class Hospital(Base):
    __tablename__ = "hospitales"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    tipo = Column(String) # 'Tercer Nivel', 'General', 'Centro de Salud'
    direccion = Column(String)
    latitud = Column(String) # Para calcular cercanía futuro
    longitud = Column(String)

class Especialidad(Base):
    __tablename__ = "especialidades"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True) # Ej: CARDIOLOGÍA, TRAUMATOLOGÍA

class Medico(Base):
    __tablename__ = "medicos"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    hospital_id = Column(Integer, ForeignKey("hospitales.id"))
    especialidad_id = Column(Integer, ForeignKey("especialidades.id"))
    
    hospital = relationship("Hospital")
    especialidad = relationship("Especialidad")

class Turno(Base):
    __tablename__ = "turnos"
    id = Column(Integer, primary_key=True, index=True)
    medico_id = Column(Integer, ForeignKey("medicos.id"))
    fecha_hora = Column(DateTime)
    disponible = Column(Boolean, default=True)
    
    medico = relationship("Medico")

# Crear tablas
def init_db():
    Base.metadata.create_all(bind=engine)