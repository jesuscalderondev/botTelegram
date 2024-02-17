from werkzeug.security import generate_password_hash, check_password_hash
from flask import session as cookies
from apscheduler.schedulers.background import BackgroundScheduler
import requests

programador = BackgroundScheduler()

def passwordHash(password:str):
    return generate_password_hash(password)

def passwordVerify(passHash:str, passUnHashed):
    return check_password_hash(passHash, passUnHashed)

def toJson(objetc):
    if hasattr(objetc, "__dict__"):
        json = {}
        for atributo in objetc.__dict__.keys():           
            json[atributo] = getattr(objetc, atributo)
        return json
    else:
        return {}


def obtenerHoraCita(fecha:str):
    try:
        response = requests.get(f'https://clinicamx-dev-efpc.2.us-1.fl0.io/api/consultar/horario/{fecha.replace("/", "-")}')
        try:
            hora = response.json()['horas']
            return hora
        except:
            return None
    except:
        return None
