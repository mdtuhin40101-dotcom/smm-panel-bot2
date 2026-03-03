import telebot
import os
from flask import Flask
import threading
from telebot import types

# Render থেকে BOT_TOKEN নিবে
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(BOT_TOKEN)

# ========== START COMMAND ==========
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("💰 Add Balance", "📦 New Order")
    markup.row("📊 My Orders", "👤 My Account")

    bot.send_message(
        message.chat.id,
        "👋 Welcome to SMM Panel Bot!\n\nChoose an option below:",
        reply_markup=markup
    )

# ========== ADD BALANCE ==========
@bot.message_handler(func=lambda message: message.text == "💰 Add Balance")
def add_balance(message):
    bot.send_message(message.chat.id, "💳 Please contact admin to add balance.")

# ========== NEW ORDER ==========
@bot.message_handler(func=lambda message: message.text == "📦 New Order")
def new_order(message):
    bot.send_message(message.chat.id, "🛒 Send service ID and link to place order.")

# ========== MY ORDERS ==========
@bot.message_handler(func=lambda message: message.text == "📊 My Orders")
def my_orders(message):
    bot.send_message(message.chat.id, "📂 You have no orders yet.")

# ========== MY ACCOUNT ==========
@bot.message_handler(func=lambda message: message.text == "👤 My Account")
def my_account(message):
    bot.send_message(message.chat.id, "👤 Account details will appear here.")

# ========== FLASK KEEP ALIVE ==========
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host="0.0.0.0", port=10000)

threading.Thread(target=run).start()

# ========== RUN BOT ==========
bot.infinity_polling()
