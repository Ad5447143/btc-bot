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

# =========================
# تنظیمات ربات
# =========================

BOT_TOKEN = "توکن_واقعی_ربات_تو"

CHAT_ID = "369031827"

# =========================
# تارگت اولیه
# =========================

TARGET_PRICE = 77000.00

# =========================
# وضعیت هشدار
# =========================

alert_sent = False

# =========================
# گرفتن قیمت BTC
# =========================

def get_btc_price():

    try:

        url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"

        response = requests.get(url, timeout=10)

        data = response.json()

        return float(data["price"])

    except Exception as e:

        print("PRICE ERROR:", e)

        return None

# =========================
# ارسال پیام تلگرام
# =========================

def send_telegram_message(text):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": text
    }

    try:

        requests.post(url, data=data)

    except Exception as e:

        print("TELEGRAM ERROR:", e)

# =========================
# چک کردن قیمت
# =========================

def price_checker():

    global alert_sent
    global TARGET_PRICE

    while True:

        try:

            price = get_btc_price()

            if price:

                print(f"BTC Price = {price:.2f} USD")

                # ----------------

                if price >= TARGET_PRICE and not alert_sent:

                    message = (
                        f"🚨 هشدار بیتکوین\n\n"
                        f"💰 قیمت فعلی: {price:.2f} USD\n"
                        f"🎯 تارگت: {TARGET_PRICE:.2f}"
                    )

                    send_telegram_message(message)

                    alert_sent = True

                # ----------------

                if price < TARGET_PRICE:

                    alert_sent = False

            time.sleep(120)

        except Exception as e:

            print("CHECKER ERROR:", e)

            time.sleep(60)

# =========================
# منوی فارسی
# =========================

keyboard = [
    ["💰 قیمت بیتکوین"],
    ["🎯 تنظیم تارگت"],
    ["ℹ️ راهنما"]
]

reply_markup = ReplyKeyboardMarkup(
    keyboard,
    resize_keyboard=True
)

# =========================
# start
# =========================

async def start(update, context):

    text = (
        "🤖 سلام!\n"
        "به ربات هشدار بیتکوین خوش اومدی 🔥\n\n"
        "📌 امکانات:\n"
        "• قیمت لحظه‌ای BTC\n"
        "• هشدار رسیدن به تارگت\n"
        "• آپدیت خودکار هر 2 دقیقه\n\n"
        "👇 از منوی زیر استفاده کن"
    )

    await update.message.reply_text(
        text,
        reply_markup=reply_markup
    )

# =========================
# قیمت
# =========================

async def price(update, context):

    try:

        btc_price = get_btc_price()

        if btc_price:

            await update.message.reply_text(
                f"💰 قیمت بیتکوین:\n\n"
                f"{btc_price:.2f} USD"
            )

        else:

            await update.message.reply_text(
                "❌ دریافت قیمت ناموفق بود"
            )

    except Exception as e:

        await update.message.reply_text(
            f"ERROR:\n{e}"
        )

# =========================
# تنظیم تارگت
# =========================

async def target(update, context):

    global TARGET_PRICE

    try:

        TARGET_PRICE = float(context.args[0])

        await update.message.reply_text(
            f"🎯 تارگت روی "
            f"{TARGET_PRICE:.2f} تنظیم شد"
        )

    except:

        await update.message.reply_text(
            "❌ مثال صحیح:\n"
            "/target 77000"
        )

# =========================
# راهنما
# =========================

async def help_command(update, context):

    text = (
        "📚 راهنمای ربات\n\n"
        "💰 قیمت بیتکوین\n"
        "نمایش قیمت لحظه‌ای BTC\n\n"
        "🎯 تنظیم تارگت\n"
        "مثال:\n"
        "/target 77000"
    )

    await update.message.reply_text(text)

# =========================
# دکمه‌ها
# =========================

async def handle_message(update, context):

    text = update.message.text

    # --------------------

    if text == "💰 قیمت بیتکوین":

        btc_price = get_btc_price()

        if btc_price:

            await update.message.reply_text(
                f"💰 قیمت فعلی بیتکوین:\n\n"
                f"{btc_price:.2f} USD"
            )

        else:

            await update.message.reply_text(
                "❌ خطا در دریافت قیمت"
            )

    # --------------------

    elif text == "🎯 تنظیم تارگت":

        await update.message.reply_text(
            "📌 مثال:\n"
            "/target 77000"
        )

    # --------------------

    elif text == "ℹ️ راهنما":

        await update.message.reply_text(
            "📚 راهنمای ربات\n\n"
            "💰 قیمت بیتکوین\n"
            "نمایش قیمت لحظه‌ای\n\n"
            "🎯 تنظیم تارگت\n"
            "مثال:\n"
            "/target 77000"
        )

# =========================
# ساخت اپ
# =========================

app = Application.builder().token(BOT_TOKEN).build()

# =========================
# هندلرها
# =========================

app.add_handler(CommandHandler("start", start))

app.add_handler(CommandHandler("price", price))

app.add_handler(CommandHandler("target", target))

app.add_handler(CommandHandler("help", help_command))

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_message
    )
)

# =========================
# اجرای Thread
# =========================

threading.Thread(
    target=price_checker,
    daemon=True
).start()

# =========================
# اجرای ربات
# =========================

print("BOT STARTED")

app.run_polling()
