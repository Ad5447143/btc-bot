from tradingview_ta import TA_Handler, Interval
from telegram import ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters
)

import requests
import threading
import time

# ------------------------
# تنظیمات ربات
# ------------------------

BOT_TOKEN = "8995261480:AAFi0H9lQyC8i3od5SjeyStlhwtdpWpCmj0"
CHAT_ID = "369031827"

# ------------------------
# تارگت اولیه
# ------------------------

TARGET_PRICE = 77000.00

# ------------------------
# وضعیت آلارم
# ------------------------

alert_sent = False

# ------------------------
# گرفتن قیمت BTC
# ------------------------

def get_btc_price():
    try:
        url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"

        response = requests.get(url)

        data = response.json()

        price = float(data["price"])

        return price

    except Exception as e:
        print("ERROR:", e)
        return None

# ------------------------
# بررسی قیمت
# ------------------------

def price_checker():
    global alert_sent
    global TARGET_PRICE

    while True:
        price = get_btc_price()

        if price:
            print(f"BTC 5m Price = {price:.2f} USDT")

            if price >= TARGET_PRICE and not alert_sent:

                message = (
                    f"🚨 BTC رسید به تارگت\n\n"
                    f"💰 Price: {price:.2f} USD\n"
                    f"🎯 Target: {TARGET_PRICE:.2f}"
                )

                send_telegram_message(message)

                alert_sent = True

            if price < TARGET_PRICE:
                alert_sent = False

        time.sleep(120)

# ------------------------
# ارسال پیام تلگرام
# ------------------------

def send_telegram_message(text):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": text
    }

    try:
        requests.post(url, data=data)

    except Exception as e:
        print("Telegram Error:", e)

# ------------------------
# منوی تلگرام
# ------------------------

keyboard = [
    ["/price", "/target"],
    ["/help"]
]

reply_markup = ReplyKeyboardMarkup(
    keyboard,
    resize_keyboard=True
)

# ------------------------
# start
# ------------------------

async def start(update, context):

    text = (
        "🤖 ربات BTC فعال شد\n\n"
        "دستورات:\n"
        "/price → قیمت فعلی\n"
        "/target 77000 → تنظیم تارگت\n"
        "/help → راهنما"
    )

    await update.message.reply_text(
        text,
        reply_markup=reply_markup
    )

# ------------------------
# help
# ------------------------

async def help_command(update, context):

    text = (
        "📌 دستورات ربات:\n\n"
        "/price\n"
        "نمایش قیمت فعلی BTC\n\n"
        "/target 77000\n"
        "تنظیم تارگت جدید"
    )

    await update.message.reply_text(text)

# ------------------------
# price
# ------------------------

async def price(update, context):

    btc_price = get_btc_price()

    if btc_price:

        text = (
            f"💰 BTC Price:\n"
            f"{btc_price:.2f} USD"
        )

        await update.message.reply_text(text)

# ------------------------
# target
# ------------------------

async def target(update, context):

    global TARGET_PRICE

    try:

        TARGET_PRICE = float(context.args[0])

        text = (
            f"🎯 تارگت روی "
            f"{TARGET_PRICE:.2f} تنظیم شد"
        )

        await update.message.reply_text(text)

    except:

        await update.message.reply_text(
            "مثال صحیح:\n/target 77000"
        )

# ------------------------
# ساخت اپ
# ------------------------

app = Application.builder().token(BOT_TOKEN).build()

# ------------------------
# هندلرها
# ------------------------

app.add_handler(CommandHandler("start", start))

app.add_handler(CommandHandler("help", help_command))

app.add_handler(CommandHandler("price", price))

app.add_handler(CommandHandler("target", target))

# ------------------------
# اجرای Thread
# ------------------------

threading.Thread(target=price_checker).start()

print("BOT STARTED")

# ------------------------
# اجرای ربات
# ------------------------

app.run_polling()
