from telebot import TeleBot
from helpers import consultas
from bin.configs import TOKEN_BOT_LIBERA
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

user_data = {}

def main():
    bot = TeleBot(TOKEN_BOT_LIBERA)

    @bot.message_handler(commands=['iniciar'])
    def start(message: Message):
        chat_id = message.chat.id
        global orcamento, loja, chatid_solicitante, matricula_solicitante
        texto, orcamento, loja, chatid_solicitante, matricula_solicitante = consultas.consultarPendente()

        if texto == False:
            bot.send_message(chat_id, "Sem orçamentos pendentes!")
            return

        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Confirmar", callback_data="confirmar"))
        markup.add(InlineKeyboardButton("Negar", callback_data="negar"))
        
        message = bot.send_message(chat_id, texto, reply_markup=markup)
        
        if chat_id not in user_data:
            user_data[chat_id] = {}
        
        user_data[chat_id]['message_id'] = message.message_id
        user_data[chat_id]['state'] = 'awaiting_confirmation'

    @bot.callback_query_handler(func=lambda call: True)
    def handle_query(call):
        chat_id = call.message.chat.id
        message_id = user_data[chat_id]['message_id']

        if call.data == "confirmar":
            bot.edit_message_reply_markup(chat_id, message_id, reply_markup=None)
            status = True
            autorizacao = 'A'
            texto = consultas.atualizarDadosAprovacao(status, orcamento, loja, chatid_solicitante, matricula_solicitante, autorizacao)
            bot.send_message(chat_id, texto)
            consultas.enviarConfirmacao(texto, chatid_solicitante)
        elif call.data == "negar":
            bot.edit_message_reply_markup(chat_id, message_id, reply_markup=None)

    bot.infinity_polling()

if __name__ == "__main__":
    main()
