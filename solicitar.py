from datetime import datetime
from telebot import TeleBot
from bin.configs import TOKEN_BOT_SOLICITA
from helpers import consultas
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

user_data = {}

def main():
    bot = TeleBot(TOKEN_BOT_SOLICITA)

    @bot.message_handler(commands=['iniciar'])
    def start(message: Message):
        data_iniciar = str((datetime.now().strftime("%d-%m-%Y")))
        hora_iniciar = str((datetime.now().strftime("%H:%M:%S")))
        user_id = message.from_user.id
        user_text = message.text
        user_name = message.from_user.username
        chat_id = message.chat.id

        print(f"Usuário: {user_name} (ID: {user_id}) - Iniciou o chat no dia {data_iniciar} às {hora_iniciar} - Digitou: '{user_text}'\n")

        user_data[chat_id] = {'state': 'asking_for_orcamento'}
        bot.send_message(chat_id, "Qual o número do orçamento?")

    @bot.message_handler(func=lambda msg: True)
    def recebeInfo(message: Message):
        data_iniciar = str((datetime.now().strftime("%d-%m-%Y")))
        hora_iniciar = str((datetime.now().strftime("%H:%M:%S")))
        user_id = message.from_user.id
        user_name = message.from_user.username
        chat_id = message.chat.id

        if chat_id in user_data:
            state = user_data[chat_id]['state']

            if state == 'asking_for_orcamento':
                orcamento = message.text
                user_data[chat_id]['numero_orcamento'] = orcamento
                user_data[chat_id]['state'] = 'asking_for_matricula'
                bot.send_message(chat_id, "Qual a sua matrícula?")

            elif state == 'asking_for_matricula':
                matricula = message.text
                user_data[chat_id]['numero_matricula'] = matricula

                orcamento = user_data[chat_id]['numero_orcamento']
                matricula = user_data[chat_id]['numero_matricula']

                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton("Confirmar", callback_data="confirmar"))
                markup.add(InlineKeyboardButton("Negar", callback_data="negar"))

                print(f"Usuário: {user_name} (ID: {user_id}) - preencheu as seguintes informações, orçamento: {orcamento} - matrícula: {matricula} no dia {data_iniciar} às {hora_iniciar}\n")

                bot.send_message(chat_id, f"Dados recebidos:\nOrçamento: {orcamento}\nMatrícula: {matricula}\nDeseja enviar?", reply_markup=markup)
                user_data[chat_id]['state'] = 'awaiting_confirmation'

    @bot.callback_query_handler(func=lambda call: True)
    def handle_query(call):
        user_id = call.from_user.id
        chat_id = call.message.chat.id
        message_id = call.message.message_id
        user_name = call.from_user.username
        data_iniciar = str((datetime.now().strftime("%d-%m-%Y")))
        hora_iniciar = str((datetime.now().strftime("%H:%M:%S")))

        if chat_id in user_data and user_data[chat_id]['state'] == 'awaiting_confirmation':
            orcamento = user_data[chat_id]['numero_orcamento']
            matricula = user_data[chat_id]['numero_matricula']
            bot.edit_message_reply_markup(chat_id, message_id, reply_markup=None)

            if call.data == "confirmar":
                nome, loja = consultas.dadosUsuario(matricula)
                consultas.inserirDados(nome, matricula, loja, orcamento, data_iniciar, hora_iniciar, chat_id)

                bot.send_message(chat_id, "Informações confirmadas e enviadas.\nClique aqui --> /iniciar para outra solicitação.")
                print(f"Usuário: {user_name} (ID: {user_id}) - enviou as informações, orçamento: {orcamento} - loja: {loja} - matrícula: {matricula} às {hora_iniciar}\n")
                user_data.pop(chat_id, None)
            elif call.data == "negar":
                bot.send_message(chat_id, "Envio negado.")
                print(f"Usuário: {user_name} (ID: {user_id}) - negou o envio.\nClique aqui --> /iniciar para outra solicitação.")
                user_data.pop(chat_id, None)

    bot.infinity_polling()

if __name__ == "__main__":
    main()
