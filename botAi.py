from telegram import *
from telegram.ext import *

updater = Updater
dispatcher = updater.dispatcher

def startCommand (update: Update, context: CallbackContext) :
    buttons = [[KeyboardButton("Random Image")], [KeyboardButton( "Random Person")]]
    context.bot.send_message(chat_id=update .effective_chat.id, text="WeIcome to my bot !",
                             reply_markup=ReplyKeyboardMarkup(buttons))

dispatcher.add_handler(CommandHandler("start ",startCommand) )
updater.start_polling()
