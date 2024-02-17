from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler, CallbackContext
from dotenv import load_dotenv
from os import getenv
from datetime import datetime, date, time

from database import *
from functions import *
load_dotenv()

userBot = getenv('userbot')
token = getenv('token')

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
    agenda = session.query(DiaTrabajo).filter(DiaTrabajo.fecha >= datetime.now(), DiaTrabajo.laborable == True).order_by(DiaTrabajo.fecha.asc()).limit(6)
    agend2 = session.query(DiaTrabajo).all()
    print(agend2)
    if len(agenda) == 0:
        keyboard = []

        for dia in agenda:
            keyboard.append([InlineKeyboardButton(f"🗓️ {dia.fecha.date()}", callback_data=f"{dia.fecha.date()}")])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Por favor, selecciona una fecha para tu cita:", reply_markup=reply_markup)
    else:
        await update.message.reply_text("No hay agenda disponible por el momento, te invitamos a intentar más tarde")

motivos = ["Paciente sano", "Crónico", "Embarazo", "Puerpera", "Salud ginecológica", "Consulta general", "Nutricional"]


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text=f"Has seleccionado: {query.data}")

    try:
        nuevoTurno = session.query(Turno).filter(Turno.idTelegram == update.message.chat_id).order_by(Turno.id.desc()).first()
    except:
        nuevoTurno = Turno(fecha, None, "Sin definir", "Sin definir", "Sin localidad", "Sin definir", "Sin definir", "Sin definir")

    try:
        fecha = datetime.strptime(query.data, "%Y-%m-%d")
        
        nuevoTurno.idTelegram = update.message.chat_id

        horasJson = obtenerHoraCita(query.data)

        keyboard = []

        for hora in horasJson:
            keyboard.append([InlineKeyboardButton(f"🗓️ {hora}", callback_data=f"{hora}")])

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text("Por favor, selecciona una hora para tu cita:", reply_markup=reply_markup)
    except:
        try:
            hora = datetime.strptime(query.data, "%H:%M").time()
            nuevoTurno.hora = hora

            keyboard = [
                [InlineKeyboardButton("Paciente sano", "Paciente sano")],
                [InlineKeyboardButton("Crónico", "Crónico")],
                [InlineKeyboardButton("Embarazo", "Embarazo")],
                [InlineKeyboardButton("Puerpera", "Puerpera")],
                [InlineKeyboardButton("Salud ginecológica", "Salud ginecológica")],
                [InlineKeyboardButton("Consulta general", "Consulta general")],
                [InlineKeyboardButton("Nutricional", "Nutricional")]
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text("Seleccione el motivo:", reply_markup=reply_markup)
        except:
            if query.data in motivos:

                nuevoTurno.motivo = query.data
                keyboard = [
                    [InlineKeyboardButton("Sí", "Primera vez"), InlineKeyboardButton("No", "Subsecuente")]
                ]

                reply_markup = InlineKeyboardMarkup(keyboard)

                await update.message.reply_text("¿Primera vez?", reply_markup=reply_markup)
            
            elif query.data in ["Primera vez", "Subsecuente"]:

                await update.message.reply_text("A continuación copie el mensaje de abajo y reemplaze los campos con la información solicitada.\nRecomendación: No eliminar el encabezado (Datos del paciente)")
                await update.message.reply_text("""
Datos del paciente
------------------
Nombre completo: Juanito Perez
Fecha de nacimiento: 2024/6/17
""")

    finally:
        try:
            session.add(nuevoTurno)
            session.commit()
        except:
            await update.message.reply_text("⚠️ Ha ocurrido un error a la hora de registrar tu cita.\nRecomendamos agendar ua nueva cita y brindar la información de manera correcta")
            session.rollback()
        


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays info on how to use the bot."""
    await update.message.reply_text("Use /start to test this bot.")

async def iniciar(update:Update, context: ContextTypes):
    try:
        nombre = update.message.chat.first_name
    except:
        nombre = "Bienvenido"
    await update.message.reply_text(f"¡Hola, {nombre}! soy CliBot, ¿En qué puedo ayudarte?")




def procesarTexto(text:str, context:ContextTypes, update:Update):

    textoPlano = text.lower()

    if 'hola' in textoPlano:
        return 'Hola, ¿Cómo estás?'
    elif 'adios' in textoPlano:
        return 'Hasta luego'
    
    if 'datos del paciente' in textoPlano:
        registro = registrarCita(textoPlano, update.message.chat.first_name)
        """if registro['operacion'] == True:
            return f"✅ Su cita fue aprobada con código C1-{registro['turno']}, para la fecha {registro['fecha']} a las {registro['hora']}"
        return f"❌ La cita no pudo ser asignada, {registro['mensaje']}"
    else:
        return 'Disculpa, no te entiendo'"""
        return "LLegamos a este punto"
    

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
    await update.message.reply_text('Ha ocurrido un error a la hora de generar tu cita')


if __name__ == '__main__':
    app = Application.builder().token(token).build()
    Base.metadata.create_all(engine)
    app.add_handler(CommandHandler('start', iniciar))
    app.add_handler(CommandHandler('agendar', agendar))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT, verificarProcedencia))
    app.add_error_handler(error)

    print('Iniciado')
    app.run_polling(allowed_updates=Update.ALL_TYPES)