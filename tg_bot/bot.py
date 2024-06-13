import json
from io import BytesIO

import telebot
from telebot import types
import requests

API_TOKEN = 'Токен'
bot = telebot.TeleBot(API_TOKEN)

# Endpoint for your DRF API
API_ENDPOINT = 'http://127.0.0.1:8000/api/users/register/'
API_ENDPOINT_PROFILE = 'http://127.0.0.1:8000/api/users/profile/'
API_URL = 'http://127.0.0.1:8000/api/products/'
API_ENDPOINT_ADD_TO_CART = 'http://127.0.0.1:8000/api/products/cart/add/'
API_ENDPOINT_REMOVE_FROM_CART = 'http://127.0.0.1:8000/api/products/cart/remove/'
API_ENDPOINT_CART = 'http://127.0.0.1:8000/api/products/cart/'
API_ENDPOINT_PRODUCT = 'http://127.0.0.1:8000/api/products/products/'
API_ENDPOINT_CREATE_TICKET = 'http://127.0.0.1:8000/api/support/tickets/'
MANAGER_USERNAME = 'hjhvlk'
# User data storage
user_data = {}


def show_main_menu(chat_id, registered=True):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    if registered:
        markup.add('👤 Профиль', '🛒 Корзина', '📦 Каталог', '🔧 Служба поддержки', '✉️ Отзывы')
    else:
        markup.add('📝 Регистрация')
    bot.send_message(chat_id, "Выберите опцию:", reply_markup=markup)


def is_user_registered(telegram_id):
    """ Проверяет, зарегистрирован ли пользователь в системе. """
    response = requests.get(f'{API_ENDPOINT_PROFILE}{telegram_id}/')
    return response.status_code == 200


@bot.message_handler(func=lambda message: message.text == 'В главное меню')
def handle_main_menu(message):
    # Здесь можно добавить логику для показа главного меню
    show_main_menu(message.chat.id, registered=True)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    user_telegram_id = message.from_user.id
    response = requests.get(f'{API_ENDPOINT_PROFILE}{user_telegram_id}/')
    if response.status_code == 200:
        show_main_menu(message.chat.id, registered=True)
    else:
        show_main_menu(message.chat.id, registered=False)


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.text == '📝 Регистрация':
        register(message)
        return
    if not is_user_registered(message.from_user.id):
        # Если пользователь не зарегистрирован
        bot.send_message(message.chat.id, "🔒 Для доступа к функциям бота необходима регистрация.")
        show_main_menu(message.chat.id, registered=False)
        return  # Прерываем выполнение функции
    if message.text == '👤 Профиль':
        handle_profile(message)
    elif message.text == '🛒 Корзина':
        view_cart(message)
    elif message.text == '📦 Каталог':
        catalog(message)  # Пример. Меняйте в зависимости от вашей логики
    elif message.text == '🔧 Служба поддержки':
        handle_support(message)
    elif message.text == '✉️ Отзывы':
        # Обработка запроса на отзывы
        pass
    elif message.text == '✅ Оформить заказ':
        handle_order_confirmation(message)
    elif message.text == '🏠 В главное меню':
        handle_main_menu(message)


def register(message):
    msg = bot.send_message(message.chat.id, "Введите ФИО:")
    bot.register_next_step_handler(msg, process_full_name_step)


def process_full_name_step(message):
    try:
        chat_id = message.chat.id
        full_name = message.text
        user_data[chat_id] = {'full_name': full_name}

        msg = bot.send_message(chat_id, 'Введите номер телефона:')
        bot.register_next_step_handler(msg, process_phone_number_step)
    except Exception as e:
        bot.reply_to(message, 'Произошла ошибка!')


def process_phone_number_step(message):
    try:
        chat_id = message.chat.id
        phone_number = message.text
        user_data[chat_id]['phone_number'] = phone_number

        msg = bot.send_message(chat_id, 'Напишите Ваш город:')
        bot.register_next_step_handler(msg, process_city_step)
    except Exception as e:
        bot.reply_to(message, 'Произошла ошибка!')


def process_city_step(message):
    try:
        chat_id = message.chat.id
        city = message.text
        user_data[chat_id]['city'] = city

        msg = bot.send_message(chat_id, 'Напишите Ваш возраст:')
        bot.register_next_step_handler(msg, process_age_step)
    except Exception as e:
        bot.reply_to(message, 'Произошла ошибка!')


def process_age_step(message):
    try:
        chat_id = message.chat.id
        age = message.text

        # Validate if age is a number
        if not age.isdigit() or int(age) <= 0:
            msg = bot.send_message(chat_id, "Пожалуйста, введите действительный возраст (число больше 0).:")
            bot.register_next_step_handler(msg, process_age_step)
            return

        user_data[chat_id]['age'] = age
        user_data[chat_id]['telegram_id'] = message.from_user.id

        # Finally, register the user
        register_user(chat_id)
    except Exception as e:
        bot.reply_to(message, 'Произошла ошибка!')


def register_user(chat_id):
    data = user_data.get(chat_id)
    if data:
        # Modify payload as needed
        payload = {
            "user": {
                "username": str(data['telegram_id']),  # Using telegram_id as username
                "email": "",  # You can also collect email from the user
                "password": "defaultpassword"  # Set a default or random password
            },
            "telegram_id": data['telegram_id'],
            "phone_number": data['phone_number'],
            "full_name": data['full_name'],
            "city": data['city'],
            "age": data['age']
        }

        response = requests.post(API_ENDPOINT, json=payload)
        if response.status_code == 201:
            bot.send_message(chat_id, "Вы успешно зарегистрировались!")
            show_main_menu(chat_id, registered=True)
        else:
            bot.send_message(chat_id, "Ошибка регистрации(")
    else:
        bot.send_message(chat_id, "Во время регистрации произошла ошибка!")


def handle_profile(message):
    user_telegram_id = message.from_user.id
    url = f'http://127.0.0.1:8000/api/users/profile/{user_telegram_id}/'
    response = requests.get(url)

    if response.status_code == 200:
        profile_data = response.json()
        profile_info = f"*👤 {profile_data['full_name']}*\n\n"
        profile_info += f"*🏙️ Город:* {profile_data['city']}\n"
        profile_info += f"*🎂 Возраст:* {profile_data['age']}\n"
        profile_info += f"*💰 Скидка:* {profile_data['discount']} RUB\n"
        profile_info += f"*🔑 Реферальный код:* `{profile_data['referral_code']}`\n"
        bot.send_message(message.chat.id, profile_info, parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, "Не удалось получить информацию о профиле.")


@bot.message_handler(commands=['referral'])
def handle_referral(message):
    msg = bot.send_message(message.chat.id, "Please enter the referral code:")
    bot.register_next_step_handler(msg, process_referral_code, message.from_user.id)


def process_referral_code(message, user_telegram_id):
    referral_code = message.text
    url = 'http://127.0.0.1:8000/api/users/referral/'
    data = {
        'telegram_id': user_telegram_id,
        'referral_code': referral_code
    }
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    response = requests.post(url, data=json.dumps(data), headers=headers)

    if response.status_code == 200:
        bot.send_message(message.chat.id, "Referral code applied successfully. You've earned a discount!")
    else:
        bot.send_message(message.chat.id, "Failed to apply referral code. Please check the code and try again.")


@bot.callback_query_handler(func=lambda call: call.data.startswith('addtocart:'))
def add_to_cart_callback(call):
    product_id = call.data.split(':')[1]
    telegram_id = call.from_user.id

    payload = {
        'telegram_id': telegram_id,
        'product_id': product_id,
        'quantity': 1  # Значение по умолчанию, можно настроить ввод количества от пользователя
    }
    response = requests.post(API_ENDPOINT_ADD_TO_CART, json=payload)

    if response.status_code == 201:
        bot.answer_callback_query(call.id, "Товар добавлен в корзину.")
    else:
        bot.answer_callback_query(call.id, "Не удалось добавить товар в корзину.", show_alert=True)


def process_remove_from_cart_step(message, user_telegram_id):
    cart_item_id = message.text
    payload = {'cart_item_id': cart_item_id}
    url = f"{API_ENDPOINT_REMOVE_FROM_CART}{user_telegram_id}/"
    response = requests.delete(url, json=payload)
    if response.status_code == 204:
        bot.reply_to(message, "Товар удален из корзины.")
    else:
        bot.reply_to(message, "Не удалось удалить товар из корзины.")


@bot.message_handler(func=lambda message: message.text == 'Каталог')
def catalog(message):
    # Запрос категорий с API
    response = requests.get(API_URL + 'categories/')
    if response.status_code == 200:
        categories = response.json()
        markup = types.InlineKeyboardMarkup()
        for category in categories:
            callback_data = f"category:{category['id']}"
            markup.add(types.InlineKeyboardButton(category['name'], callback_data=callback_data))
        bot.send_message(message.chat.id, 'Выберите категорию:', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Ошибка при загрузке категорий.')


@bot.callback_query_handler(func=lambda call: call.data.startswith('category:'))
def category_callback(call):
    category_id = call.data.split(':')[1]
    request_url = API_URL + f'products/?category_id={category_id}'
    response = requests.get(request_url)
    if response.status_code == 200:
        products = response.json()
        if products:
            markup = types.InlineKeyboardMarkup()
            for product in products:
                # Добавление смайликов для улучшения восприятия
                button_text = f"🔸 {product['name']} - {product['price']} руб."
                callback_data = f"product:{product['id']}"
                markup.add(types.InlineKeyboardButton(button_text, callback_data=callback_data))
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text='🛍 Выберите товар:',
                                  reply_markup=markup)
        else:
            bot.send_message(call.message.chat.id, '🚫 В этой категории нет товаров.')
    else:
        bot.send_message(call.message.chat.id,
                         f'⚠️ Ошибка при загрузке товаров.')


@bot.callback_query_handler(func=lambda call: call.data.startswith('product:'))
def product_callback(call):
    product_id = call.data.split(':')[1]
    # Запрос подробной информации о товаре с API
    response = requests.get(API_ENDPOINT_PRODUCT + f'{product_id}/')
    if response.status_code == 200:
        product = response.json()

        # Сборка медиа-группы для отправки изображений
        media_group = []
        for image_info in product['images']:
            image_url = image_info['image']
            photo = requests.get(image_url).content
            media = types.InputMediaPhoto(photo)
            media_group.append(media)

        # Отправка медиа-группы
        if media_group:
            bot.send_media_group(call.message.chat.id, media_group)

        # Текстовое сообщение с описанием товара
        product_text = f"🔹 {product['name']}\n💰 Цена: {product['price']} руб.\n{product['description']}"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('🛒 Добавить в корзину', callback_data=f'addtocart:{product_id}'))
        bot.send_message(call.message.chat.id, text=product_text, reply_markup=markup)
    else:
        bot.send_message(call.message.chat.id, '⚠️ Ошибка при загрузке информации о товаре.')


def view_cart(message):
    telegram_id = message.from_user.id
    response = requests.get(f"{API_ENDPOINT_CART}{telegram_id}/")

    if response.status_code == 200:
        cart_data = response.json()
        items = cart_data.get('items', [])
        if items:
            for item in items:
                product_id = item['product']
                product_response = requests.get(f"{API_ENDPOINT_PRODUCT}{product_id}/")
                if product_response.status_code == 200:
                    product_details = product_response.json()
                    product_info = f"{product_details['name']} - {item['quantity']} шт. по {product_details['price']} руб."
                    markup = types.InlineKeyboardMarkup()
                    markup.add(types.InlineKeyboardButton("Удалить", callback_data=f"removefromcart:{item['id']}"))
                    bot.send_message(message.chat.id, product_info, reply_markup=markup)
            # После вывода всех товаров добавляем кнопки действий
            markup_actions = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
            order_button = types.KeyboardButton('✅ Оформить заказ')
            delete_all_button = types.KeyboardButton('🗑 Удалить все')
            main_menu_button = types.KeyboardButton('🏠 В главное меню')

            markup_actions.add(order_button, delete_all_button, main_menu_button)
            bot.send_message(message.chat.id, "Что вы хотите сделать дальше?", reply_markup=markup_actions)

        else:
            bot.send_message(message.chat.id, "Ваша корзина пуста.")
    else:
        bot.send_message(message.chat.id, "Не удалось получить информацию о корзине.")


@bot.callback_query_handler(func=lambda call: call.data.startswith('removefromcart:'))
def remove_from_cart_callback(call):
    cart_item_id = call.data.split(':')[1]
    telegram_id = call.from_user.id
    payload = {'cart_item_id': cart_item_id}
    url = f"{API_ENDPOINT_REMOVE_FROM_CART}{telegram_id}/"
    response = requests.delete(url, json=payload)
    if response.status_code == 204:
        bot.answer_callback_query(call.id, "Товар удален из корзины.")
        view_cart(call.message)
    else:
        bot.answer_callback_query(call.id, "Не удалось удалить товар из корзины.", show_alert=True)


def handle_order_confirmation(message):
    telegram_id = message.from_user.id
    response = requests.get(f"http://127.0.0.1:8000/api/products/cart/{telegram_id}/")

    if response.status_code == 200:
        cart_data = response.json()
        items = cart_data.get('items', [])
        if items:
            order_details = "🛍 *Состав вашего заказа:*\n\n"
            total_sum = 0
            for item in items:
                product_response = requests.get(f"http://127.0.0.1:8000/api/products/products/{item['product']}/")
                if product_response.status_code == 200:
                    product_details = product_response.json()
                    order_details += f"```🔹 {product_details['name']} - {item['quantity']} шт. по {product_details['price']} руб.\n"
                    total_sum += item['quantity'] * float(product_details['price'])
            order_details += f"\n💰 *Общая сумма:* {total_sum} руб.\n```"
            order_manger = "\n👩‍💼 _Скопируйте содержимое заказа и отправьте в личном сообщении нашему менеджеру._"

            # Создание инлайн-кнопки для связи с менеджером
            markup = types.InlineKeyboardMarkup()
            contact_manager_button = types.InlineKeyboardButton(
                text="📞 Связаться с менеджером",
                url=f"https://t.me/{MANAGER_USERNAME}"
            )
            markup.add(contact_manager_button)

            # Отправка сообщения пользователю с деталями заказа и кнопкой
            bot.send_message(message.chat.id, order_details, parse_mode='Markdown')
            bot.send_message(message.chat.id, order_manger, reply_markup=markup, parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id, "🚫 Ваша корзина пуста.")
    else:
        bot.send_message(message.chat.id, "⚠️ Произошла ошибка при получении данных о корзине.")


@bot.callback_query_handler(func=lambda call: call.data == 'removeallfromcart')
def remove_all_from_cart_callback(call):
    telegram_id = call.from_user.id
    # Здесь логика для удаления всех товаров из корзины
    # Например, запрос к API для удаления всех товаров
    # response = requests.delete(API_ENDPOINT_REMOVE_ALL_FROM_CART, json={'telegram_id': telegram_id})
    # if response.status_code == 204:
    bot.answer_callback_query(call.id, "Все товары удалены из корзины.")
    # else:
    #     bot.answer_callback_query(call.id, "Не удалось очистить корзину.", show_alert=True)


def create_ticket_in_drf(telegram_id, title, content):
    user_response = requests.get(f'http://127.0.0.1:8000/api/users/profile/{telegram_id}/')
    if user_response.status_code == 200:
        user_data = user_response.json()
        user_id = user_data['id']  # Извлекаем ID пользователя
        print()
        ticket_data = {
            'title': title,
            'content': content,
            'status': 'open',
            'user': user_id
        }
        print(ticket_data)
        headers = {'Content-Type': 'application/json'}
        response = requests.post('http://127.0.0.1:8000/api/support/tickets/', json=ticket_data, headers=headers)
        return response.status_code == 201

    else:
        return False


def handle_support(message):
    chat_id = message.chat.id
    msg = bot.send_message(chat_id, "Опишите вашу проблему:")
    bot.register_next_step_handler(msg, process_support_message, chat_id)


def process_support_message(message, chat_id):
    telegram_id = message.from_user.id
    content = message.text
    title = "Запрос в службу поддержки"

    if create_ticket_in_drf(telegram_id, title, content):
        bot.send_message(chat_id, "Ваш запрос отправлен в службу поддержки.")
        notify_admin_about_ticket(telegram_id, title, content)  # Отправляем уведомление администратору
    else:
        bot.send_message(chat_id, "Произошла ошибка при отправке запроса.")



ADMIN_CHAT_ID = '576113936'  # ID чата администратора в Telegram

def notify_admin_about_ticket(telegram_id, title, content):
    admin_message = f"Новое обращение в поддержку:\n\nОт: {telegram_id}\nЗаголовок: {title}\nСодержание: {content}"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Ответить', callback_data=f'reply:{telegram_id}'))
    bot.send_message(ADMIN_CHAT_ID, admin_message, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('reply:'))
def handle_reply_callback(call):
    ticket_id = call.data.split(':')[1]
    # Сохраняем ID тикета для последующего ответа
    user_data[call.from_user.id] = {'replying_to': ticket_id}
    bot.send_message(call.from_user.id, "Введите ваш ответ на обращение:")


def get_user_id_by_telegram_id(telegram_id):
    response = requests.get(f'http://127.0.0.1:8000/api/users/profile/{telegram_id}/')
    if response.status_code == 200:
        user_data = response.json()
        return user_data['user']['id']
    else:
        return None


@bot.message_handler(func=lambda message: 'replying_to' in user_data.get(message.from_user.id, {}))
def handle_admin_response(message):
    ticket_id = user_data[message.from_user.id]['replying_to']
    response_content = message.text
    user_id = get_user_id_by_telegram_id(message.from_user.id)  # Получаем ID пользователя-администратора

    # Проверяем, найден ли пользователь
    if user_id is None:
        bot.send_message(message.chat.id, "Ошибка: профиль пользователя не найден.")
        return

    # Отправка ответа в вашу систему поддержки через API
    response = requests.post(
        'http://127.0.0.1:8000/api/support/responses/',
        headers={'Content-Type': 'application/json'},
        json={'content': response_content, 'ticket': ticket_id, 'user': user_id}
    )
    if response.status_code == 201:
        bot.send_message(message.chat.id, "Ваш ответ был отправлен.")
    else:
        bot.send_message(message.chat.id, "Произошла ошибка при отправке ответа.")

    del user_data[message.from_user.id]['replying_to']  # Удаляем информацию о текущем ответе


bot.polling(none_stop=True)
