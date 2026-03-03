import telebot
import requests
from flask import Flask
import threading

BOT_TOKEN = "8469845092:AAEjppWea01-utFvBZERB-FNBAoydZT_glM"
API_KEY = "eadb5bf6d39da590d9820687b2edad06"
ADMIN_ID = 7743679187
API_URL = "https://smmgen.com/api/v2"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

users = {}

# ================= START =================

@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.chat.id)

    if user_id not in users:
        users[user_id] = {"balance": 0}

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("💰 Add Balance", "📦 New Order")
    markup.row("👤 My Account")

    bot.send_message(message.chat.id,
                     "✅ Welcome to SMM Panel Bot",
                     reply_markup=markup)

# ================= ACCOUNT =================

@bot.message_handler(func=lambda m: m.text == "👤 My Account")
def account(message):
    user = users.get(str(message.chat.id))
    bot.send_message(message.chat.id,
                     f"💰 Balance: {user['balance']} ৳")

# ================= ADD BALANCE =================

@bot.message_handler(func=lambda m: m.text == "💰 Add Balance")
def add_balance(message):
    bot.send_message(message.chat.id,
                     "Send payment like:\nTxnID | Amount")

# ================= NEW ORDER =================

@bot.message_handler(func=lambda m: m.text == "📦 New Order")
def new_order(message):
    bot.send_message(message.chat.id,
                     "Send order like:\nServiceID | Link | Quantity")

@bot.message_handler(func=lambda m: "|" in m.text)
def process_order(message):
    user_id = str(message.chat.id)

    try:
        service, link, quantity = message.text.split("|")
        quantity = int(quantity.strip())

        price = quantity * 1

        if users[user_id]["balance"] < price:
            bot.send_message(message.chat.id, "❌ Not enough balance!")
            return

        payload = {
            "key": API_KEY,
            "action": "add",
            "service": service.strip(),
            "link": link.strip(),
            "quantity": quantity
        }

        response = requests.post(API_URL, data=payload).json()

        if "order" in response:
            order_id = response["order"]
            users[user_id]["balance"] -= price

            bot.send_message(message.chat.id,
                             f"✅ Order Successful!\nOrder ID: {order_id}")
        else:
            bot.send_message(message.chat.id,
                             f"❌ Panel Error:\n{response}")

    except:
        bot.send_message(message.chat.id,
                         "❌ Wrong format!\nUse:\nServiceID | Link | Quantity")

# ================= FLASK =================

@app.route('/')
def home():
    return "Bot Running"

def run():
    app.run(host="0.0.0.0", port=10000)

threading.Thread(target=run).start()

print("Bot Started...")
bot.infinity_polling()
