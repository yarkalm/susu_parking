import telebot
from telebot import types

# Вставьте ваш токен бота здесь
bot = telebot.TeleBot('6817205700:AAHHmBIoMGUumUC2UoZVTYjWIZXMmpZradQ')
lang = True  # True - Русский, False - English


# Команда для выбора языка и установки меню
@bot.message_handler(commands=['start'])
def send_welcome(message):
    # Создаем меню с кнопками
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    annotated = types.KeyboardButton("Отправить размеченное фото" if lang else "Send annotated photo")  # Кнопка для отправки размеченного фото
    parking_bboxes = types.KeyboardButton("Отправить фото мест" if lang else "Send boxes photo")  # Кнопка для отправки размеченного фото
    parking_icons = types.KeyboardButton("Отправить иконки" if lang else "Send icons photo")  # Кнопка для отправки размеченного фото
    markup.add(annotated, parking_bboxes, parking_icons)  # Добавляем кнопку для отправки фото в меню


@bot.message_handler(commands=['lang'])
def choose_lang(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    rus = types.KeyboardButton("🇷🇺 Русский")
    eng = types.KeyboardButton("🇬🇧 English")
    markup.add(rus, eng)
    bot.send_message(
        message.chat.id,
        "🇷🇺 Выберите язык / 🇬🇧 Choose your language",
        reply_markup=markup
    )


# Обработка выбора языка
@bot.message_handler(func=lambda message: message.text in ["🇷🇺 Русский", "🇬🇧 English"])
def handle_language_choice(message):
    if message.text == "🇷🇺 Русский":
        bot.send_message(message.chat.id, "Вы выбрали русский язык. Привет!")
        lang = True
    elif message.text == "🇬🇧 English":
        lang = False
        bot.send_message(message.chat.id, "You chose English. Hello!")


# Обработка отправки фото по кнопке в меню
@bot.message_handler(func=lambda message: message.text == "Отправить фото")
def send_photo(message):
    # Указываем путь к файлу изображения
    image_path = '../result_images/annotated_frame.jpg'

    with open(image_path, 'rb') as photo:
        bot.send_photo(message.chat.id, photo)
    # except FileNotFoundError:
    #     bot.send_message(message.chat.id, "Извините, файл не найден. Пожалуйста, убедитесь, что он существует.")


# Обработка любых других сообщений
@bot.message_handler(func=lambda message: True)
def handle_unexpected(message):
    bot.send_message(message.chat.id, "I don't understand. Please use the provided buttons.")


# Запуск бота
print("Бот запущен")
bot.polling(none_stop=True, interval=0)
