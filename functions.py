import requests

def obtenerHoraCita(fecha:str):
    try:
        rutaHost = 'https://clinicamx-dev-efpc.2.us-1.fl0.io'
        rutaLocal = 'http://127.0.0.1:8080'
        response = requests.get(f'{rutaLocal}/api/consultar/horario/{fecha.replace("/", "-")}')
        try:
            hora = response.json()['horas']
            return hora
        except Exception as e:
            print("Error en el primero")
            print(e)
            return None
    except Exception as e:
        print("Error en el segundo")
        print(e)
        return None
