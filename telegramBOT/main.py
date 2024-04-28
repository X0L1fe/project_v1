import telebot

from telebot import types

import webbrowser

token = '7114623875:AAExJMAuoMl1vSFMSt0OfntoM9-JzDRq0M4'

admin_chat_id = 843044049
user_chat_ids = {}# Словарь для хранения динамических chat_id пользователей
target_user_chat_id = None # Переменная для хранения chat_id пользователя

bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start'])
def main(message):
    markup = types.InlineKeyboardMarkup()
    tutorials = types.InlineKeyboardButton("Туториалы", url="http://127.0.0.1:5000/helper")
    site = types.InlineKeyboardButton("Сайт", url='http://127.0.0.1:5000')
    markup.row(site, tutorials)
    suppurt_user = types.InlineKeyboardButton("Поддержка", callback_data='support')#кнопка поддержки
    markup.row(suppurt_user)
    bot.send_message(message.chat.id, f'Здравствуйте, {message.from_user.first_name} !\nЧем именно я Вам могу помочь?\n Выберете пункт меню.', reply_markup=markup)

@bot.callback_query_handler(func=lambda callback: True)
def callback_query(callback):
    if callback.data == 'tutorial_go':
        webbrowser.open('http://127.0.0.1:5000/tutorials')
    elif callback.data =='site':
        webbrowser.open('http://127.0.0.1:5000')
    elif callback.data =='support':
        messanger(callback.message)


@bot.message_handler(content_types=["text"])
def messanger(message):
    global target_user_chat_id

    sender_chat_id = message.chat.id
    text = message.text

    # Если отправитель - администратор
    if sender_chat_id == admin_chat_id:
        # Если у администратора уже выбран конкретный пользователь, то отправляем сообщение этому пользователю
        if target_user_chat_id is not None:
            bot.send_message(target_user_chat_id, text)
            bot.send_message(admin_chat_id, f"Сообщение успешно отправлено пользователю.")
            # Сбрасываем target_user_chat_id, чтобы не отправлять сообщения другим пользователям
            target_user_chat_id = None
        else:
            # Если конкретный пользователь не выбран, то  сообщение отправлено администратором для выбора пользователя
            bot.send_message(admin_chat_id, text)
            try:
                # Пробуем преобразовать введенный текст в число
                target_user_chat_id = int(text)
                bot.send_message(admin_chat_id, f"Выбран пользователь {message.from_user.first_name}")
            except ValueError:
                bot.send_message(admin_chat_id, "Id пользователя не введён, или некорректен.")

    else:
        bot.send_message(admin_chat_id, f"<b>ID</b>: {message.from_user.id}\n<b>Username:</b> {message.from_user.first_name}\n <b>Сообщение</b>: {message.text}", parse_mode='HTML')
        # Добавляем динамические chat_id в словарь
        if sender_chat_id not in user_chat_ids.values():
            user_chat_ids[message.from_user.id] = sender_chat_id

        # Сохраняем chat_id пользователя, которому администратор хочет отправить сообщение
        if target_user_chat_id is None:
            target_user_chat_id = sender_chat_id
            bot.send_message(admin_chat_id, f"<b>Пользователь выбран.</b>", parse_mode='HTML')


bot.polling(non_stop=True)