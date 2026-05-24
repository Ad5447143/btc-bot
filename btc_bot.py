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
import winsound
from win10toast import ToastNotifier

# -------------------------
# تنظیمات تلگرام
# -------------------------

BOT_TOKEN = "8995261480:AAFi0H9lQyC8i3od5SjeyStlhwtdpWpCmj0"

CHAT_ID = "369031827"

# -------------------------
# تارگت اولیه
# -------------------------

TARGET_PRICE = 77000.00

# -------------------------
# نوتیفیکیشن ویندوز
# -------------------------

toaster = ToastNotifier()

# -------------------------
# اتصال TradingView
# -------------------------

btc = TA_Handler(
    symbol="BTCUSDT",
    screener="crypto",
    exchange="BINANCE",

    # تایم فریم 5 دقیقه
    interval=Interval.INTERVAL_5_MINUTES
)

# -------------------------
# ارسال پیام تلگرام
# -------------------------

def send_message(text):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": text
    }

    requests.post(url, data=data)

# -------------------------
# دستور /start
# -------------------------

async def start(update, context):

    keyboard = [
        ["📈 قیمت BTC"],
        ["🎯 تنظیم تارگت"]
    ]

    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )

    await update.message.reply_text(
        "✅ ربات فعال شد",
        reply_markup=reply_markup
    )

# -------------------------
# دستور /set
# -------------------------

async def set_target(update, context):

    global TARGET_PRICE

    try:

        TARGET_PRICE = float(context.args[0])

        await update.message.reply_text(
            f"✅ تارگت جدید تنظیم شد:\n{TARGET_PRICE:.2f} USDT"
        )

    except:

        await update.message.reply_text(
            "❌ مثال:\n/set 77000"
        )

# -------------------------
# دستور /price
# -------------------------

async def current_price(update, context):

    try:

        analysis = btc.get_analysis()

        price = analysis.indicators["close"]

        await update.message.reply_text(
            f"💰 قیمت فعلی BTC:\n{price:.2f} USDT"
        )

    except Exception as e:

        await update.message.reply_text(
            f"ERROR: {e}"
        )

# -------------------------
# دکمه های منو
# -------------------------

async def handle_message(update, context):

    text = update.message.text

    # قیمت BTC
    if text == "📈 قیمت BTC":

        try:

            analysis = btc.get_analysis()

            price = analysis.indicators["close"]

            await update.message.reply_text(
                f"💰 قیمت BTC:\n{price:.2f} USDT"
            )

        except Exception as e:

            await update.message.reply_text(
                f"ERROR: {e}"
            )

    # تنظیم تارگت
    elif text == "🎯 تنظیم تارگت":

        await update.message.reply_text(
            "عدد را اینطوری بفرست:\n/set 77000"
        )

# -------------------------
# حلقه بررسی قیمت
# -------------------------

alert_sent = False

def price_checker():

    global alert_sent

    while True:

        try:

            analysis = btc.get_analysis()

            price = analysis.indicators["close"]

            print(f"BTC 5m Price = {price:.2f} USDT")

            # اگر به تارگت رسید
            if price >= TARGET_PRICE and not alert_sent:

                text = f"🚨 BTC رسید به {price:.2f} USDT"

                # پیام تلگرام
                send_message(text)

                # صدای هشدار
                for i in range(3):
                    winsound.Beep(3000, 1000)

                # نوتیف ویندوز
                toaster.show_toast(
                    "BTC ALERT",
                    text,
                    duration=10
                )

                print("ALERT SENT")

                alert_sent = True

            # اگر دوباره پایین آمد
            if price < TARGET_PRICE:

                alert_sent = False

            # هر 2 دقیقه آپدیت
            time.sleep(120)

        except Exception as e:

            print("ERROR:", e)

            # اگر ریت لیمیت شد
            if "429" in str(e):

                print("WAITING 5 MINUTES")

                time.sleep(300)

            else:

                time.sleep(60)

# -------------------------
# اجرای ربات
# -------------------------

app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("set", set_target))
app.add_handler(CommandHandler("price", current_price))

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_message
    )
)

# اجرای چکر قیمت
threading.Thread(target=price_checker).start()

print("BOT STARTED")

app.run_polling() 