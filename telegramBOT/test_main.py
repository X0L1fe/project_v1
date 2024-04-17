import telebot
from telebot import types

token = '7114623875:AAExJMAuoMl1vSFMSt0OfntoM9-JzDRq0M4'
admin_chat_id = 843044049
user_chat_ids = {}
target_user_chat_id = None

bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start'])
def main(message):
    markup = types.InlineKeyboardMarkup()
    tutorials = types.InlineKeyboardButton("Туториалы", url="http://127.0.0.1:5000/tutorials", callback_data='tutorial_go')
    site = types.InlineKeyboardButton("Сайт", url='http://127.0.0.1:5000', callback_data='site')
    markup.row(site, tutorials)
    suppurt_user = types.InlineKeyboardButton("Поддержка", callback_data='support')
    bug_fix_button = types.InlineKeyboardButton("Проблема с сайтом", callback_data='bug_fix')
    markup.row(suppurt_user, bug_fix_button)
    bot.send_message(message.chat.id, f'Здравствуйте, {message.from_user.first_name}!\nЧем именно я Вам могу помочь?\nВыберете пункт меню.', reply_markup=markup)

@bot.callback_query_handler(func=lambda callback: True)
def callback_query(callback):
    if callback.data == 'support':
        # Проверяем, что пользователь, которому бот хочет отправить сообщение, не является ботом
        if not callback.message.from_user.is_bot:
            bot.send_message(callback.message.from_user.id, "Вы перешли в чат с поддержкой.")
            messanger(callback.message)
        else:
            bot.send_message(callback.message.from_user.id, "К сожалению, боты не могут использовать эту функцию.")
    elif callback.data == 'bug_fix':
        bot.send_message(callback.message.from_user.id, "Вы отправили проблему с сайтом.")
        bug_fix(callback.message)


@bot.message_handler(content_types=["text"])
def messanger(message):
    global target_user_chat_id

    sender_user_id = message.from_user.id
    sender_chat_id = message.chat.id
    text = message.text
    
    if sender_chat_id == admin_chat_id:
        if target_user_chat_id is not None:
            bot.reply_to(target_user_chat_id, text)
            bot.send_message(admin_chat_id, f"Сообщение успешно отправлено пользователю.")
            target_user_chat_id = None
        else:
            bot.send_message(admin_chat_id, text)
            try:
                target_user_chat_id = int(text)
                bot.send_message(admin_chat_id, f"Выбран пользователь {message.from_user.first_name}")
            except ValueError:
                bot.send_message(admin_chat_id, "Id пользователя не введён, или некорректен.")
    else:
        bot.send_message(admin_chat_id, f"<b>ID</b>: {sender_user_id}\n<b>Username:</b> {message.from_user.first_name}\n <b>Сообщение</b>: {message.text}", parse_mode='HTML')
        user_chat_ids[sender_user_id] = sender_chat_id
        if target_user_chat_id is None:
            target_user_chat_id = sender_chat_id
            bot.send_message(admin_chat_id, f"<b>Пользователь выбран.</b>", parse_mode='HTML')

@bot.message_handler(content_types=["text"], func=lambda message: message.chat.id == admin_chat_id)
def bug_fix(message):
    bot.send_message(admin_chat_id, f"<b>ID</b>: {message.from_user.id}\n<b>Username:</b> {message.from_user.first_name}\n<b>Проблема</b>: {message.text}", parse_mode='HTML')

bot.polling(non_stop=True)
