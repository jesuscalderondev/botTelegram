from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler, CallbackContext
from dotenv import load_dotenv
from os import getenv
from datetime import datetime, date, time, timedelta
from sqlalchemy import desc, asc
from database import *
from functions import *
import os

load_dotenv()
userBot = os.environ['USER_BOT']
token = os.environ['TOKEN']
app = Application.builder().token(token).build()

def registrarCita(texto:str, usuario:str) -> Boolean:
    parametros = texto.split(':')
    print(parametros)
    #paciente = parametros[1].split('\n')[0].title()
    #fecha = parametros[2].split('\n')[0].replace(" ", "")
    
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a message with three inline buttons attached."""
    keyboard = [
        [
            InlineKeyboardButton("Option 1", callback_data="1"),
            InlineKeyboardButton("Option 2", callback_data="2"),
        ],
        [InlineKeyboardButton("Option 3", callback_data="3")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Please choose:", reply_markup=reply_markup)

async def agendar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    agenda = session.query(DiaTrabajo).filter(DiaTrabajo.fecha >  datetime.now() - timedelta(days=1), DiaTrabajo.laborable == True).order_by(desc(DiaTrabajo.id)).limit(6)
    update.message.from_user.id
    try:
        keyboard = []

        for dia in agenda:
            keyboard.append([InlineKeyboardButton(f"🗓️ {dia.fecha}", callback_data=f"{dia.fecha}")])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Por favor, selecciona una fecha para tu cita:", reply_markup=reply_markup)
    except Exception as e:
        print(e)
        await update.message.reply_text("No hay agenda disponible por el momento, te invitamos a intentar más tarde")

motivos = ["Paciente sano", "Crónico", "Embarazo", "Puerpera", "Salud ginecológica", "Consulta general", "Nutricional"]


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text=f"Has seleccionado: {query.data}")

    nuevoTurno = session.query(Turno).filter(Turno.idTelegram == str(query.message.chat.id), Turno.paciente == "Sin definir").order_by(Turno.id.desc()).first()

    if nuevoTurno == None:
        nuevoTurno = Turno(query.data, None, "Sin definir", "Sin definir", "Sin localidad", "Sin definir", "Sin definir", None)
        nuevoTurno.idTelegram = str(query.message.chat.id)
    try:
        nuevoTurno.fecha = datetime.strptime(query.data, '%Y-%m-%d')
        try:
            session.add(nuevoTurno)
            session.commit()
            horasJson = obtenerHoraCita(query.data)
            keyboard = []

            for hora in horasJson:
                keyboard.append([InlineKeyboardButton(f"🗓️ {hora}", callback_data=f"{hora}")])

            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.message.reply_text("Por favor, selecciona una hora para tu cita:", reply_markup=reply_markup)
        except Exception as e:
            print(e, 1)
            await update.callback_query.message.reply_text("⚠️ Ha ocurrido un error a la hora de registrar tu cita.\nRecomendamos agendar ua nueva cita y brindar la información de manera correcta")
            session.rollback()
            session.delete(nuevoTurno)
            session.commit()
    except:
        try:
            nuevoTurno.hora = datetime.strptime(query.data, "%H:%M").time()
            try:
                session.add(nuevoTurno)
                session.commit()
                keyboard = [
                    [InlineKeyboardButton("Paciente sano", callback_data="Paciente sano")],
                    [InlineKeyboardButton("Crónico", callback_data="Crónico")],
                    [InlineKeyboardButton("Embarazo", callback_data="Embarazo")],
                    [InlineKeyboardButton("Puerpera", callback_data="Puerpera")],
                    [InlineKeyboardButton("Salud ginecológica", callback_data="Salud ginecológica")],
                    [InlineKeyboardButton("Consulta general", callback_data="Consulta general")],
                    [InlineKeyboardButton("Nutricional", callback_data="Nutricional")]
                ]

                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.message.reply_text("Seleccione el motivo:", reply_markup=reply_markup)
            except Exception as e:
                print(e, 2)
                await update.callback_query.message.reply_text("⚠️ Ha ocurrido un error a la hora de registrar tu cita.\nRecomendamos agendar ua nueva cita y brindar la información de manera correcta")
                session.rollback()
                session.delete(nuevoTurno)
                session.commit()

            
        except:
            if query.data in motivos:
                nuevoTurno.motivo = query.data
                try:
                    session.add(nuevoTurno)
                    session.commit()
                    keyboard = [
                        [InlineKeyboardButton("Sí", callback_data="Primera vez"), InlineKeyboardButton("No", callback_data="Subsecuente")]
                    ]

                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await query.message.reply_text("¿Primera vez?", reply_markup=reply_markup)
                except Exception as e:
                    print(e, 3)
                    await update.callback_query.message.reply_text("⚠️ Ha ocurrido un error a la hora de registrar tu cita.\nRecomendamos agendar ua nueva cita y brindar la información de manera correcta")
                    session.rollback()
                    session.delete(nuevoTurno)
                    session.commit()
            
            elif query.data in ["Primera vez", "Subsecuente"]:
                nuevoTurno.veces = query.data
                try:
                    session.add(nuevoTurno)
                    session.commit()
                except Exception as e:
                    print(e, 4)
                    await update.callback_query.message.reply_text("⚠️ Ha ocurrido un error a la hora de registrar tu cita.\nRecomendamos agendar ua nueva cita y brindar la información de manera correcta")
                    session.rollback()
                    session.delete(nuevoTurno)
                    session.commit()

                await query.message.reply_text("A continuación copie el mensaje de abajo y reemplaze los campos con la información solicitada.\nRecomendación: No eliminar el encabezado (Datos del paciente)")
                await query.message.reply_text("""
Datos del paciente
------------------
Nombre completo: Juanito Perez
Fecha de nacimiento: 2024/6/17
""")
        

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays info on how to use the app."""
    await update.message.reply_text("Use /start to test this app.")

async def iniciar(update:Update, context: ContextTypes):
    try:
        nombre = update.message.chat.first_name
    except:
        nombre = "Bienvenido"
    await update.message.reply_text(f"¡Hola, {nombre}! soy CliBot, ¿En qué puedo ayudarte?")


async def obtenerCodigo(update:Update, context:ContextTypes):
    await update.message.reply_text(f"Tu código para ser registrado en el sistema es el siguiente: {update.message.chat.id}")


def procesarTexto(text:str, context:ContextTypes, update:Update):

    textoPlano = text.lower()

    if 'hola' in textoPlano:
        return 'Hola, ¿Cómo estás?'
    elif 'adios' in textoPlano:
        return 'Hasta luego'
    
    if 'datos del paciente' in textoPlano:
        try:
            parametros = textoPlano.split(": ")
            nuevoTurno = session.query(Turno).filter(Turno.idTelegram == str(update.message.chat.id)).order_by(Turno.id.desc()).first()
            voluntario = session.query(Voluntario).filter(Voluntario.telegramId == str(update.message.chat.id)).first()
            print(voluntario, '******************************************************************************')
            if voluntario == None:
                return f"❌ La cita no pudo ser asignada, dado que usted no es un usuario autorizado, para poder hacerlo, debe comunicarse con el encargado de registros de voluntarios"
            nuevoTurno.deriva = voluntario.nombreCompleto
            nuevoTurno.localidad = voluntario.localidad
            nuevoTurno.paciente = parametros[1].split("\n")[0].title()
            nuevoTurno.fechaNacimiento = formatearFecha(parametros[2].split("\n")[0])
            session.add(nuevoTurno)
            session.commit()
            return f"✅ Su cita fue aprobada con código C1-{nuevoTurno.id}, para la fecha {nuevoTurno.fecha} a las {nuevoTurno.hora}"
        except Exception as e:
            return f"❌ La cita no pudo ser asignada, {e}"
    else:
        return 'Disculpa, no te entiendo'
    

async def verificarProcedencia(update:Update, context: ContextTypes):
    tipoMensaje = update.message.chat.type
    texto = update.message.text

    if tipoMensaje == 'group':
        if texto.startswith(userBot):
            nuevoMensaje = texto.replace(userBot, '')
            respuesta = procesarTexto(nuevoMensaje, context, update)
        else:
            return
    else:
        print(update.message.chat.first_name)
        respuesta = procesarTexto(texto, context, update)

    await update.message.reply_text(respuesta)

async def error(update:Update, context: ContextTypes):
    print(context.error)
    message = f'{context.error}\nHa ocurrido un error a la hora de generar tu cita'
    try:
        await update.message.reply_text(message)
    except:
        pass


if __name__ == '__main__':
    print('Iniciando...')
    app.add_handler(CommandHandler('start', iniciar))
    app.add_handler(CommandHandler('agendar', agendar))
    app.add_handler(CommandHandler('obtenercodigo', obtenerCodigo))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT, verificarProcedencia))
    app.add_error_handler(error)

    print('Iniciado')
    app.run_polling(allowed_updates=Update.ALL_TYPES)