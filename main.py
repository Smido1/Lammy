from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from dotenv import load_dotenv
from flask import Flask
import telebot
import os

load_dotenv()
TOKEN = os.getenv("TOKEN")
URL = os.getenv("URL")
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start_game'])
def send_game(message):
    markup = InlineKeyboardMarkup()
    web_app_url = URL
    markup.add(InlineKeyboardButton("Тест", web_app=WebAppInfo(url=web_app_url)))
    bot.send_message(message.chat.id, "Нажмите на кнопку ниже, чтобы запустить:", reply_markup=markup)


bot.infinity_polling()
