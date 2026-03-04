import telebot
from telebot import types
import json
import os
import requests

TOKEN = "8469845092:AAEjppWea01-utFvBZERB-FNBAoydZT_glM"
ADMIN_ID = 7743679187

JOIN_CHANNELS = ["@smmpenel009", "@Tuhininco"]
NOTICE_CHANNEL = "@Tuhinonli"
DEPOSIT_CHANNEL = "@Tuhinonli"
ORDER_CHANNEL = "@Tuhininco"

BKASH_NUMBER = "01904155168"
MIN_DEPOSIT = 2

API_URL = "https://smmgen.com/api/v2"
API_KEY = "eadb5bf6d39da590d9820687b2edad06"

SERVICES = {
    "👁 TikTok Views": 17293,
    "❤️ TikTok Likes": 16963,
    "👥 TikTok Followers": 12854
}

bot = telebot.TeleBot(TOKEN)
DATA_FILE = "data.json"

# ================= DATABASE =================

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ================= FORCE JOIN =================

def check_join(user_id):
    for ch in JOIN_CHANNELS:
        try:
            member = bot.get_chat_member(ch, user_id)
            if member.status in ["left", "kicked"]:
                return False
        except:
            return False
    return True

def join_markup():
    markup = types.InlineKeyboardMarkup()
    for ch in JOIN_CHANNELS:
        markup.add(types.InlineKeyboardButton(
            f"📢 Join {ch}",
            url=f"https://t.me/{ch.replace('@','')}"
        ))
    markup.add(types.InlineKeyboardButton("✅ Check", callback_data="check_join"))
    return markup

@bot.callback_query_handler(func=lambda c: c.data=="check_join")
def verify_join(call):
    if check_join(call.from_user.id):
        bot.answer_callback_query(call.id,"✅ Verified")
        bot.send_message(call.message.chat.id,"Now type /start")
    else:
        bot.answer_callback_query(call.id,"❌ Join All Channels First")

# ================= START =================

@bot.message_handler(commands=["start"])
def start(message):
    user_id = str(message.chat.id)
    data = load_data()

    if not check_join(message.chat.id):
        bot.send_message(message.chat.id,"❌ আগে সব চ্যানেল জয়েন করো",reply_markup=join_markup())
        return

    if user_id not in data:
        data[user_id] = {"balance": 0,"ref_by": None}

        if len(message.text.split()) > 1:
            ref = message.text.split()[1]
            if ref in data and ref != user_id:
                data[user_id]["ref_by"] = ref
                data[ref]["balance"] += 0.050
                bot.send_message(ref,"🎉 0.050 Tk referral bonus added!")

        save_data(data)
        bot.send_message(NOTICE_CHANNEL,f"🆕 New User Joined\nID: {user_id}")

    main_menu(message.chat.id)

# ================= MAIN MENU =================

def main_menu(chat_id):
    data = load_data()
    balance = data[str(chat_id)]["balance"]

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("💰 Balance","💳 Deposit")
    markup.add("📦 Order","👥 Refer")

    bot.send_message(chat_id,f"👋 Welcome\n💰 Balance: {balance} Tk",reply_markup=markup)

# ================= BALANCE =================

@bot.message_handler(func=lambda m: m.text=="💰 Balance")
def balance(message):
    data = load_data()
    bot.send_message(message.chat.id,f"💰 Balance: {data[str(message.chat.id)]['balance']} Tk")

# ================= REFER =================

@bot.message_handler(func=lambda m: m.text=="👥 Refer")
def refer(message):
    link = f"https://t.me/{bot.get_me().username}?start={message.chat.id}"
    bot.send_message(message.chat.id,f"👥 Referral Link:\n{link}\nPer Referral = 0.050 Tk")

# ================= DEPOSIT =================

@bot.message_handler(func=lambda m: m.text=="💳 Deposit")
def deposit(message):
    bot.send_message(
        message.chat.id,
        f"💳 Send Money To\nbKash: {BKASH_NUMBER}\nMinimum: {MIN_DEPOSIT} Tk\n\nSend:\nTxnID | Amount"
    )
    bot.register_next_step_handler(message, deposit_trx)

def deposit_trx(message):
    try:
        trx, amount = message.text.split("|")
        amount = float(amount.strip())

        if amount < MIN_DEPOSIT:
            bot.send_message(message.chat.id,f"❌ Minimum Deposit is {MIN_DEPOSIT} Tk")
            return

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("✅ Approve",callback_data=f"approve_{message.chat.id}_{amount}"))

        bot.send_message(DEPOSIT_CHANNEL,
            f"💳 Deposit Request\nUser: {message.chat.id}\nTRX: {trx}\nAmount: {amount} Tk",
            reply_markup=markup)

        bot.send_message(message.chat.id,"⏳ Waiting for approval")

    except:
        bot.send_message(message.chat.id,"❌ Format:\nTxnID | Amount")

@bot.callback_query_handler(func=lambda c: c.data.startswith("approve_"))
def approve(call):
    if call.from_user.id != ADMIN_ID:
        return

    _, user_id, amount = call.data.split("_")
    data = load_data()
    data[user_id]["balance"] += float(amount)
    save_data(data)

    bot.send_message(user_id,f"✅ {amount} Tk Added")
    bot.edit_message_reply_markup(call.message.chat.id,call.message.message_id,None)

# ================= ORDER =================

@bot.message_handler(func=lambda m: m.text=="📦 Order")
def order_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("👁 TikTok Views","❤️ TikTok Likes")
    markup.add("👥 TikTok Followers","🔙 Back")
    bot.send_message(message.chat.id,"Select Service",reply_markup=markup)

@bot.message_handler(func=lambda m: m.text in SERVICES.keys())
def service_select(message):
    bot.send_message(message.chat.id,"Send:\nlink quantity\nExample:\nhttps://tiktok.com/... 1000")
    bot.register_next_step_handler(message, process_order, message.text)

def process_order(message, service_name):
    try:
        link, quantity = message.text.split()
        service_id = SERVICES[service_name]

        payload = {
            "key": API_KEY,
            "action": "add",
            "service": service_id,
            "link": link,
            "quantity": quantity
        }

        r = requests.post(API_URL, data=payload)
        result = r.json()

        if "order" in result:
            order_id = result["order"]

            db = load_data()
            db[str(message.chat.id)]["balance"] -= 1
            save_data(db)

            bot.send_message(
                ORDER_CHANNEL,
                f"📦 Order\nUser: {message.chat.id}\nService: {service_name}\nLink: {link}\nQty: {quantity}\nOrderID: {order_id}"
            )

            bot.send_message(message.chat.id,"✅ Order Submitted")

        else:
            bot.send_message(message.chat.id,"❌ API Error")

    except:
        bot.send_message(message.chat.id,"❌ Invalid Format")

@bot.message_handler(func=lambda m: m.text=="🔙 Back")
def back(message):
    main_menu(message.chat.id)

print("Bot Running...")
bot.infinity_polling()
