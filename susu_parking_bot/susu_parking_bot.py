import telebot
from telebot import types

# Вставьте ваш токен бота здесь
bot = telebot.TeleBot('6817205700:AAHNTW6icsiEs9um5DYZhNSTR49vdzc-cOw')
lang = True  # True - Русский, False - English
photo_types = {"ru_ann": "📸Фото",
               "en_ann": "📸Send annotated photo",
               "ru_box": "🟩Боксы",
               "en_box": "🟩Send boxes photo",
               "ru_ic": "🅿Иконки",
               "en_ic": "🅿Send icons photo"}
types_to_photo = {value: key for key, value in photo_types.items()}


@bot.message_handler(commands=['start'])
def start(message):
    print('start')
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(
        text='Unlock · IT-комьюнити',
        url='https://vk.com/unlockit.space')
    markup.add(btn1)

    menu = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    c1 = types.KeyboardButton('Начальное приветствие' if lang else 'Welcome')  # Замена /start
    c2 = types.KeyboardButton('Показать парковку' if lang else 'Show parking')  # Замена /parking
    c3 = types.KeyboardButton('Изменить язык' if lang else 'Change language')  # Замена /lang
    menu.add(c1, c2, c3)

    bot.send_message(message.from_user.id,
                     '👋Приветствую! Данный бот создан благодаря "А поныть?" от Unlock. Бот покажет вам свободные '
                     'места на парковке ГУК ЮУрГУ.' if lang else "👋Greetings! This bot was created thanks to 'And "
                                                                 "whine?' from Unlock. The bot will show you the "
                                                                 "available parking spaces at the SUSU.",
                     reply_markup=markup)

    bot.send_message(
        message.chat.id,
        "Выберите действие" if lang else 'Choose action',
        reply_markup=menu
    )


# Команда для выбора языка и установки меню
@bot.message_handler(commands=['parking'])
def parking(message):
    print('parking')
    # Создаем меню с кнопками
    start_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    annotated = types.KeyboardButton(
        photo_types['ru_ann'] if lang else photo_types['en_ann'])  # Кнопка для отправки размеченного фото
    parking_bboxes = types.KeyboardButton(
        photo_types['ru_box'] if lang else photo_types['en_box'])  # Кнопка для отправки размеченного фото
    parking_icons = types.KeyboardButton(
        photo_types['ru_ic'] if lang else photo_types['en_ic'])  # Кнопка для отправки размеченного фото
    start_markup.add(annotated, parking_bboxes, parking_icons)  # Добавляем кнопку для отправки фото в меню
    bot.send_message(
        message.chat.id,
        "Выберите тип" if lang else "Choose type",
        reply_markup=start_markup
    )


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
    print('lang')
    global lang
    if message.text == "🇷🇺 Русский":
        bot.send_message(message.chat.id, "Вы выбрали русский язык. Привет!")
        lang = True
    elif message.text == "🇬🇧 English":
        lang = False
        bot.send_message(message.chat.id, "You chose English. Hello!")


# Обработка кнопок в меню
@bot.message_handler(
    func=lambda message: message.text in ["Начальное приветствие", "Показать парковку", "Изменить язык", "Welcome",
                                          "Show parking", "Change Language"])
def handle_menu_buttons(message):
    if (message.text == "Начальное приветствие") or (message.text == "Welcome"):
        start(message)  # вызов команды /start
    elif (message.text == "Показать парковку") or (message.text == "Show parking"):
        parking(message)  # вызов команды /parking
    elif (message.text == "Изменить язык") or (message.text == "Change language"):
        choose_lang(message)  # вызов команды /lang


# Обработка отправки фото по кнопке в меню
@bot.message_handler(func=lambda message: message.text in photo_types.values())
def send_photo(message):
    print("send_photo")
    # Указываем путь к файлу изображения
    annotated_image = '../result_images/annotated_frame.jpg'
    parking_boxes = '../result_images/parking_boxes.jpg'
    parking_lots = '../result_images/parking_lots.jpg'
    orig_image = '../result_images/frame.jpg'

    type_image = types_to_photo[message.text].split('_')[1]

    if type_image == 'ann':
        image = annotated_image
    elif type_image == 'box':
        image = parking_boxes
    elif type_image == 'ic':
        image = parking_lots
    else:
        image = orig_image

    try:
        with open(image, 'rb') as photo:
            bot.send_photo(message.chat.id, photo)
    except FileNotFoundError:
        bot.send_message(message.chat.id,
                         "Извините, файл не найден. Пожалуйста, убедитесь, что он существует." if lang else 'Sorry. '
                                                                                                            'File is '
                                                                                                            'not found')


# Запуск бота
print("Бот запущен")
bot.polling()
