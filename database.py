from sqlalchemy import Column, Integer, String, Float, Date, Time, Boolean, ForeignKey
from sqlalchemy import or_, and_
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy import create_engine
from os import getenv
from dotenv import load_dotenv
from datetime import date, time, datetime
import psycopg2

from functions import passwordHash

database = f'postgresql://fl0user:SjVQIKkY24oD@ep-black-snow-a5xfghmv.us-east-2.aws.neon.fl0.io:5432/database?sslmode=require'
#database = 'sqlite:///database.db'
engine = create_engine(database)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()


class Usuario(Base):
    __tablename__ = 'Usuarios'
    id = Column(Integer, primary_key=True)
    nombreCompleto = Column(String(225),nullable=False)
    nombreUsuario = Column(String(20), nullable=False, unique=True)
    clave = Column(String(225), nullable=False)
    cargo = Column(String(55), nullable=False)

    def __init__(self, nombreCompleto, nombreUsuario, clave, cargo):
        self.nombreCompleto = nombreCompleto
        self.nombreUsuario = nombreUsuario
        self.clave = passwordHash(clave)
        self.cargo = cargo

class Voluntario(Base):
    __tablename__ = 'voluntarios'
    id = Column(Integer, primary_key=True)
    nombreCompleto = Column(String(300),nullable=False)
    localidad = Column(String(100), nullable=False)
    telegramId = Column(String(50), nullable=False)
    

    def __init__(self, nombreCompleto, localidad, telegramId):
        self.nombreCompleto = nombreCompleto
        self.localidad = localidad
        self.telegramId = telegramId
        
    def __str__(self):
        return self.nombreCompleto
    
        
        
class Turno(Base):
    __tablename__ = 'turnos'
    id = Column(Integer, primary_key=True)
    fecha = Column(Date, nullable=False)
    hora = Column(Time, nullable=True)
    motivo = Column(String, nullable=False)
    paciente = Column(String(225), nullable=False)
    edad = Column(Integer, nullable=True)
    localidad = Column(String, nullable=False)
    deriva = Column(String(225), nullable=False)
    veces = Column(String(30), nullable=False)
    asiste = Column(String(20), nullable=False)
    condicion = Column(String(25), nullable=False)
    fechaNacimiento = Column(Date, nullable=True)
    idTelegram = Column(String(125), nullable=True)

    def __init__(self, fecha, hora, motivo, paciente, localidad, veces, deriva, fechaNacimiento):
        self.fecha = datetime.strptime(fecha, "%Y-%m-%d")
        try:
            self.hora = datetime.strptime(hora, "%H:%M").time()
        except:
            self.hora = hora
        self.motivo = motivo
        self.paciente = paciente
        try:
            self.fechaNacimiento = datetime.strptime(fechaNacimiento, "%Y-%m-%d")
        except:
            self.fechaNacimiento = fechaNacimiento
        try:
            self.edad = self.calcularEdad()
        except:
            self.edad = None
        self.localidad = localidad
        self.veces = veces
        self.deriva = deriva
        self.asiste = 'Pendiente'
        self.condicion = 'Agendado'

    def calcularEdad(self):
        diferencia = datetime.today() - self.fechaNacimiento
        edad = diferencia.days / 365.25
        return round(edad)
        
class DiaTrabajo(Base):
    __tablename__ = 'diaTrabjo'
    id = Column(Integer, primary_key=True)
    fecha = Column(Date, nullable=False, unique=True)
    intervalo = Column(Integer, nullable=False)
    inicio = Column(Time, nullable=False)
    fin = Column(Time, nullable=False)
    laborable = Column(Boolean, default=True)

    def __init__(self, fecha, intervalo, inicio, fin):
        self.fecha = datetime.strptime(fecha, "%Y-%m-%d")
        self.intervalo = intervalo
        self.inicio = datetime.strptime(inicio, "%H:%M").time()
        self.fin = datetime.strptime(fin, "%H:%M").time()


class Video(Base):
    __tablename__ = 'videos'
    id = Column(Integer, primary_key=True)
    fecha = Column(Date, nullable=False, unique=False)
    titulo = Column(String(15), nullable=False)
    ruta = Column(String(200), nullable=False, unique=True)

    def __init__(self, fecha, titulo, ruta):
        self.fecha = fecha
        self.titulo = titulo
        self.ruta = ruta