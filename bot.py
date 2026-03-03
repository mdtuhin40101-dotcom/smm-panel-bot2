import telebot
import os
import json
import requests
from flask import Flask
import threading
from telebot import types

# ================== CONFIG ==================

BOT_TOKEN = os.getenv("8469845092:AAFTXc1IfoH4NKupnGp0WxQSgbvTIo42oW0")
ADMIN_ID = 7743679187

API_URL = "https://smmgen.com/api/v2"
API_KEY = "eadb5bf6d39da590d9820687b2edad06"

CHANNELS = [
    "@smmpenel009",
    "@Tuhinonli",
    "@Tuhininco"
]

ORDER_CHANNEL = "@Tuhinonli"
JOIN_NOTIFY_CHANNEL = "@Tuhininco"

bot = telebot.TeleBot(BOT_TOKEN)

# ================== DATABASE ==================

def load_users():
    try:
        with open("users.json", "r") as f:
            return json.load(f)
    except:
        return {}

def save_users(data):
    with open("users.json", "w") as f:
        json.dump(data, f)

users = load_users()

# ================== FORCE JOIN ==================

def check_join(user_id):
    for channel in CHANNELS:
        try:
            member = bot.get_chat_member(channel, user_id)
            if member.status not in ["member", "administrator", "creator"]:
                return False
        except:
            return False
    return True

# ================== START ==================

@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.chat.id)

    if not check_join(message.chat.id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Join Main", url="https://t.me/smmpenel009"))
        markup.add(types.InlineKeyboardButton("Join Order", url="https://t.me/Tuhinonli"))
        markup.add(types.InlineKeyboardButton("Join Community", url="https://t.me/Tuhininco"))

        bot.send_message(message.chat.id,
                         "⚠️ Join all channels first!",
                         reply_markup=markup)
        return

    if user_id not in users:
        users[user_id] = {"balance": 0}
        save_users(users)
        bot.send_message(JOIN_NOTIFY_CHANNEL, f"👤 New User Joined\nUser ID: {user_id}")

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("💰 Add Balance", "📦 New Order")
    markup.row("👤 My Account")

    bot.send_message(message.chat.id, "✅ Access Granted!", reply_markup=markup)

# ================== ACCOUNT ==================

@bot.message_handler(func=lambda m: m.text == "👤 My Account")
def account(message):
    user = users.get(str(message.chat.id))
    bot.send_message(message.chat.id, f"💰 Balance: {user['balance']} ৳")

# ================== ADD BALANCE ==================

@bot.message_handler(func=lambda m: m.text == "💰 Add Balance")
def add_balance(message):
    bot.send_message(message.chat.id,
                     "Send TxnID and Amount like:\nTxnID | Amount")

@bot.message_handler(func=lambda m: "|" in m.text)
def handle_payment(message):
    user_id = message.chat.id
    try:
        txn, amount = message.text.split("|")
        txn = txn.strip()
        amount = int(amount.strip())

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Approve",
                    callback_data=f"approve_{user_id}_{amount}"))

        bot.send_message(ADMIN_ID,
                         f"💳 Payment Request\nUser: {user_id}\nTxn: {txn}\nAmount: {amount}",
                         reply_markup=markup)

        bot.send_message(user_id, "⏳ Waiting for admin approval")

    except:
        pass

@bot.callback_query_handler(func=lambda call: call.data.startswith("approve_"))
def approve(call):
    _, user_id, amount = call.data.split("_")
    user_id = str(user_id)
    amount = int(amount)

    if user_id not in users:
        users[user_id] = {"balance": 0}

    users[user_id]["balance"] += amount
    save_users(users)

    bot.send_message(user_id, f"💰 {amount} ৳ Added Successfully!")
    bot.answer_callback_query(call.id, "Approved")

# ================== NEW ORDER ==================

@bot.message_handler(func=lambda m: m.text == "📦 New Order")
def new_order(message):
    bot.send_message(message.chat.id,
                     "Send order like:\nServiceID | Link | Quantity")
    bot.register_next_step_handler(message, process_order)

def process_order(message):
    user_id = str(message.chat.id)

    try:
        parts = message.text.split("|")

        if len(parts) != 3:
            bot.send_message(message.chat.id,
                             "❌ Wrong format!\nUse:\nServiceID | Link | Quantity")
            return

        service = parts[0].strip()
        link = parts[1].strip()
        quantity = parts[2].strip()

        price = int(quantity) * 1

        if users[user_id]["balance"] < price:
            bot.send_message(message.chat.id, "❌ Not enough balance!")
            return

        payload = {
            "key": API_KEY,
            "action": "add",
            "service": service,
            "link": link,
            "quantity": quantity
        }

        response = requests.post(API_URL, data=payload).json()

        if "order" in response:
            order_id = response["order"]

            users[user_id]["balance"] -= price
            save_users(users)

            bot.send_message(ORDER_CHANNEL,
                             f"📦 New Order\nUser: {user_id}\nService: {service}\nQuantity: {quantity}\nPanel Order ID: {order_id}")

            bot.send_message(message.chat.id,
                             f"✅ Order Successful!\nOrder ID: {order_id}")
        else:
            bot.send_message(message.chat.id,
                             f"❌ Panel Error:\n{response}")

    except Exception as e:
        bot.send_message(message.chat.id,
                         f"❌ Error:\n{str(e)}")

# ================== FLASK ==================

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Running"

def run():
    app.run(host="0.0.0.0", port=10000)

threading.Thread(target=run).start()

bot.infinity_polling()        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Approve",
                    callback_data=f"approve_{user_id}_{amount}"))

        bot.send_message(ADMIN_ID,
                         f"💳 Payment Request\nUser: {user_id}\nTxn: {txn}\nAmount: {amount}",
                         reply_markup=markup)

        bot.send_message(user_id, "⏳ Waiting for admin approval")

    except:
        pass

@bot.callback_query_handler(func=lambda call: call.data.startswith("approve_"))
def approve(call):
    _, user_id, amount = call.data.split("_")
    user_id = str(user_id)
    amount = int(amount)

    if user_id not in users:
        users[user_id] = {"balance": 0}

    users[user_id]["balance"] += amount
    save_users(users)

    bot.send_message(user_id, f"💰 {amount} ৳ Added Successfully!")
    bot.answer_callback_query(call.id, "Approved")

# ================== NEW ORDER ==================

@bot.message_handler(func=lambda m: m.text == "📦 New Order")
def new_order(message):
    bot.send_message(message.chat.id,
                     "Send order like:\nServiceID | Link | Quantity")
    bot.register_next_step_handler(message, process_order)

def process_order(message):
    user_id = str(message.chat.id)

    try:
        service, link, quantity = message.text.split("|")
        service = service.strip()
        link = link.strip()
        quantity = quantity.strip()

        price = int(quantity) * 1

        if users[user_id]["balance"] < price:
            bot.send_message(message.chat.id, "❌ Not enough balance!")
            return

        payload = {
            "key": API_KEY,
            "action": "add",
            "service": service,
            "link": link,
            "quantity": quantity
        }

        response = requests.post(API_URL, data=payload).json()

        if "order" in response:
            order_id = response["order"]

            users[user_id]["balance"] -= price
            save_users(users)

            bot.send_message(ORDER_CHANNEL,
                             f"📦 New Order\nUser: {user_id}\nService: {service}\nQuantity: {quantity}\nPanel Order ID: {order_id}")

            bot.send_message(message.chat.id,
                             f"✅ Order Successful!\nOrder ID: {order_id}")
        else:
            bot.send_message(message.chat.id,
                             f"❌ Panel Error:\n{response}")

    except Exception as e:
        bot.send_message(message.chat.id,
                         f"❌ Error:\n{str(e)}")

# ================== FLASK ==================

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Running"

def run():
    app.run(host="0.0.0.0", port=10000)

threading.Thread(target=run).start()

bot.infinity_polling()
