import telebot
import requests
import json
import os
from flask import Flask
import threading
from telebot import types

# ========= CONFIG =========
BOT_TOKEN = "8469845092:AAEjppWea01-utFvBZERB-FNBAoydZT_glM"
API_KEY = "eadb5bf6d39da590d9820687b2edad06"
API_URL = "https://smmgen.com/api/v2"

MAIN_CHANNEL = "@smmpenel009"
JOIN_DEPOSIT_CHANNEL = "@Tuhinonli"
ORDER_CHANNEL = "@Tuhininco"

CHANNELS = [MAIN_CHANNEL]
# ==========================

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# ========= USER DATABASE =========

def load_users():
    if not os.path.exists("users.json"):
        return {}
    with open("users.json", "r") as f:
        return json.load(f)

def save_users(data):
    with open("users.json", "w") as f:
        json.dump(data, f, indent=4)

users = load_users()

# ========= FORCE JOIN =========

def check_join(user_id):
    for channel in CHANNELS:
        try:
            member = bot.get_chat_member(channel, user_id)
            if member.status not in ["member", "administrator", "creator"]:
                return False
        except:
            return False
    return True

def join_button():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(
        "📢 Join Channel",
        url=f"https://t.me/{MAIN_CHANNEL.replace('@','')}"
    ))
    return markup

# ========= START =========

@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.chat.id)

    if not check_join(message.chat.id):
        bot.send_message(
            message.chat.id,
            "❌ আগে চ্যানেল জয়েন করো",
            reply_markup=join_button()
        )
        return

    if user_id not in users:
        users[user_id] = {"balance": 0}
        save_users(users)

        bot.send_message(
            JOIN_DEPOSIT_CHANNEL,
            f"👤 New User Joined\nUser ID: {user_id}"
        )

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("💰 Add Balance")
    markup.row("📦 New Order")
    markup.row("👤 My Account")

    bot.send_message(
        message.chat.id,
        "✅ Welcome to SMM Panel Bot",
        reply_markup=markup
    )

# ========= ACCOUNT =========

@bot.message_handler(func=lambda m: m.text == "👤 My Account")
def account(message):
    if not check_join(message.chat.id):
        bot.send_message(message.chat.id, "❌ আগে চ্যানেল জয়েন করো",
                         reply_markup=join_button())
        return

    user_id = str(message.chat.id)
    balance = users.get(user_id, {}).get("balance", 0)

    bot.send_message(message.chat.id, f"💰 Balance: {balance} ৳")

# ========= DEPOSIT =========

@bot.message_handler(func=lambda m: m.text == "💰 Add Balance")
def deposit_instruction(message):
    if not check_join(message.chat.id):
        bot.send_message(message.chat.id, "❌ আগে চ্যানেল জয়েন করো",
                         reply_markup=join_button())
        return

    bot.send_message(message.chat.id,
                     "Send payment like:\nTxnID | Amount")

@bot.message_handler(func=lambda m: "|" in m.text and m.text.count("|") == 1)
def handle_deposit(message):
    try:
        txn, amount = message.text.split("|")
        txn = txn.strip()
        amount = int(amount.strip())
        user_id = str(message.chat.id)

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(
            "✅ Approve",
            callback_data=f"approve_{user_id}_{amount}"
        ))

        bot.send_message(
            JOIN_DEPOSIT_CHANNEL,
            f"💳 Deposit Request\nUser: {user_id}\nTxnID: {txn}\nAmount: {amount}",
            reply_markup=markup
        )

        bot.send_message(user_id, "⏳ Deposit request sent!")

    except:
        bot.send_message(message.chat.id,
                         "❌ Format Wrong!\nUse:\nTxnID | Amount")

@bot.callback_query_handler(func=lambda call: call.data.startswith("approve_"))
def approve_deposit(call):
    _, user_id, amount = call.data.split("_")
    amount = int(amount)

    if user_id not in users:
        users[user_id] = {"balance": 0}

    users[user_id]["balance"] += amount
    save_users(users)

    bot.send_message(user_id,
                     f"💰 {amount} ৳ Added Successfully!")

    bot.edit_message_text(
        f"✅ Deposit Approved\nUser: {user_id}\nAmount: {amount}",
        call.message.chat.id,
        call.message.message_id
    )

    bot.answer_callback_query(call.id)

# ========= ORDER =========

@bot.message_handler(func=lambda m: m.text == "📦 New Order")
def order_instruction(message):
    if not check_join(message.chat.id):
        bot.send_message(message.chat.id, "❌ আগে চ্যানেল জয়েন করো",
                         reply_markup=join_button())
        return

    bot.send_message(message.chat.id,
                     "Send order like:\nServiceID | Link | Quantity")

@bot.message_handler(func=lambda m: m.text.count("|") == 2)
def process_order(message):
    try:
        service, link, quantity = message.text.split("|")
        service = service.strip()
        link = link.strip()
        quantity = int(quantity.strip())

        user_id = str(message.chat.id)

        price = quantity * 1

        if users[user_id]["balance"] < price:
            bot.send_message(message.chat.id,
                             "❌ Not enough balance!")
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

            bot.send_message(
                ORDER_CHANNEL,
                f"📦 New Order\nUser: {user_id}\nService: {service}\nQty: {quantity}\nOrderID: {order_id}"
            )

            bot.send_message(message.chat.id,
                             f"✅ Order Successful!\nOrder ID: {order_id}")
        else:
            bot.send_message(message.chat.id,
                             f"❌ Panel Error:\n{response}")

    except:
        bot.send_message(message.chat.id,
                         "❌ Format Wrong!\nUse:\nServiceID | Link | Quantity")

# ========= FLASK =========

@app.route('/')
def home():
    return "Bot Running"

def run():
    app.run(host="0.0.0.0", port=10000)

threading.Thread(target=run).start()

print("Bot Started Successfully")
bot.infinity_polling()
