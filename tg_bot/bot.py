import json
from io import BytesIO

import telebot
from telebot import types
import requests

API_TOKEN = '6710651165:AAH-55n4WNu0-JBqGHQMdJ0mFJGwb_mvM44'
bot = telebot.TeleBot(API_TOKEN)

# Endpoint for your DRF API
API_ENDPOINT = 'http://127.0.0.1:8000/api/users/register/'
API_ENDPOINT_PROFILE = 'http://127.0.0.1:8000/api/users/profile/'
API_URL = 'http://127.0.0.1:8000/api/products/products/'

# User data storage
user_data = {}


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Welcome to the registration bot!\nUse /register to start the registration process.")


@bot.message_handler(commands=['register'])
def register(message):
    msg = bot.send_message(message.chat.id, "Enter your full name:")
    bot.register_next_step_handler(msg, process_full_name_step)


def process_full_name_step(message):
    try:
        chat_id = message.chat.id
        full_name = message.text
        user_data[chat_id] = {'full_name': full_name}

        msg = bot.send_message(chat_id, 'Enter your phone number:')
        bot.register_next_step_handler(msg, process_phone_number_step)
    except Exception as e:
        bot.reply_to(message, 'An error occurred')


def process_phone_number_step(message):
    try:
        chat_id = message.chat.id
        phone_number = message.text
        user_data[chat_id]['phone_number'] = phone_number

        msg = bot.send_message(chat_id, 'Enter your city:')
        bot.register_next_step_handler(msg, process_city_step)
    except Exception as e:
        bot.reply_to(message, 'An error occurred')


def process_city_step(message):
    try:
        chat_id = message.chat.id
        city = message.text
        user_data[chat_id]['city'] = city

        msg = bot.send_message(chat_id, 'Enter your age:')
        bot.register_next_step_handler(msg, process_age_step)
    except Exception as e:
        bot.reply_to(message, 'An error occurred')


def process_age_step(message):
    try:
        chat_id = message.chat.id
        age = message.text

        # Validate if age is a number
        if not age.isdigit() or int(age) <= 0:
            msg = bot.send_message(chat_id, "Please enter a valid age (number greater than 0):")
            bot.register_next_step_handler(msg, process_age_step)
            return

        user_data[chat_id]['age'] = age
        user_data[chat_id]['telegram_id'] = message.from_user.id

        # Finally, register the user
        register_user(chat_id)
    except Exception as e:
        bot.reply_to(message, 'An error occurred')


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
            bot.send_message(chat_id, "You have been registered successfully!")
        else:
            bot.send_message(chat_id, f"Registration failed: {response.text}")
    else:
        bot.send_message(chat_id, "An error occurred during registration")


@bot.message_handler(commands=['profile'])
def handle_profile(message):
    user_telegram_id = message.from_user.id
    url = f'http://127.0.0.1:8000/api/users/profile/{user_telegram_id}/'
    response = requests.get(url)

    if response.status_code == 200:
        profile_data = response.json()
        profile_info = f"Full Name: {profile_data['full_name']}\n"
        profile_info += f"City: {profile_data['city']}\n"
        profile_info += f"Age: {profile_data['age']}\n"
        profile_info += f"Discount: {profile_data['discount']} RUB\n"
        profile_info += f"Referral code: {profile_data['referral_code']} \n"
        bot.send_message(message.chat.id, profile_info)
    else:
        bot.send_message(message.chat.id, "Failed to retrieve profile information.")


@bot.message_handler(commands=['apple'])
def send_apple_products(message):
    response = requests.get(API_URL)
    if response.status_code == 200:
        products = response.json()
        for product in products:
            if product['category']['name'] == 'Apple':
                media_group = []
                # Добавление изображений в медиа группу
                for image_info in product['images']:
                    image_url = image_info['image']
                    photo = requests.get(image_url).content
                    media = types.InputMediaPhoto(photo)
                    media_group.append(media)

                # Отправка текстового сообщения

                # Отправка медиа группы
                if media_group:
                    bot.send_media_group(message.chat.id, media_group)
                # Текстовое сообщение с описанием товара
                product_text = f"{product['name']}\n"
                product_text += f"{product['description']}\n"
                product_text += f"Цена: {product['price']} руб.\n"
                bot.send_message(message.chat.id, product_text, parse_mode='Markdown')


    else:
        bot.send_message(message.chat.id, 'Извините, произошла ошибка при получении данных.')


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


bot.polling(none_stop=True)
