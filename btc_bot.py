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

BOT_TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

# =========================
# کوین‌ها
# =========================

SYMBOLS = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]

# =========================
# ذخیره قیمت قبلی
# =========================

price_history = {}

# =========================
# گرفتن قیمت
# =========================

def get_price(symbol):
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
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
# سیگنال‌ها
# =========================

def check_signal(symbol):
    price = get_price(symbol)

    if price is None:
        return

    if symbol in price_history:
        old_price, old_time = price_history[symbol]

        change = ((price - old_price) / old_price) * 100

        if change >= 2:
            send_telegram_message(
                f"🚀 PUMP ALERT\n\n"
                f"📊 Coin: {symbol}\n"
                f"💰 Price: {price:.2f}\n"
                f"📈 Change: {change:.2f}%"
            )

        elif change <= -2:
            send_telegram_message(
                f"📉 DUMP ALERT\n\n"
                f"📊 Coin: {symbol}\n"
                f"💰 Price: {price:.2f}\n"
                f"📉 Change: {change:.2f}%"
            )

    price_history[symbol] = (price, time.time())

# =========================
# لوپ اصلی بررسی بازار
# =========================

def price_checker():
    while True:
        try:
            for symbol in SYMBOLS:
                check_signal(symbol)

            time.sleep(10)

        except Exception as e:
            print("CHECKER ERROR:", e)
            time.sleep(5)

# =========================
# منوی تلگرام
# =========================

keyboard = [
    ["💰 قیمت بیتکوین"],
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
        "🤖 ربات سیگنال کریپتو فعال شد 🔥\n\n"
        "📊 قابلیت‌ها:\n"
        "• بررسی BTC / ETH / BNB\n"
        "• تشخیص Pump / Dump\n"
        "• آپدیت خودکار\n\n"
        "👇 از منو استفاده کن"
    )

    await update.message.reply_text(text, reply_markup=reply_markup)

# =========================
# قیمت BTC دستی
# =========================

def get_btc_price():
    return get_price("BTCUSDT")

async def price(update, context):
    btc_price = get_btc_price()

    if btc_price:
        await update.message.reply_text(
            f"💰 BTC Price:\n{btc_price:.2f} USD"
        )
    else:
        await update.message.reply_text("❌ خطا در دریافت قیمت")

# =========================
# راهنما
# =========================

async def help_command(update, context):
    await update.message.reply_text(
        "📚 راهنما:\n\n"
        "💰 قیمت بیتکوین\n"
        "نمایش قیمت BTC\n\n"
        "📊 سیستم خودکار:\n"
        "تشخیص Pump / Dump برای BTC, ETH, BNB"
    )

# =========================
# پیام‌های دکمه‌ای
# =========================

async def handle_message(update, context):
    text = update.message.text

    if text == "💰 قیمت بیتکوین":
        btc_price = get_btc_price()
        if btc_price:
            await update.message.reply_text(f"💰 {btc_price:.2f} USD")
        else:
            await update.message.reply_text("❌ خطا")

    elif text == "ℹ️ راهنما":
        await help_command(update, context)

# =========================
# ساخت ربات
# =========================

app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("price", price))
app.add_handler(CommandHandler("help", help_command))

app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
)

# =========================
# اجرای Thread بازار
# =========================

threading.Thread(
    target=price_checker,
    daemon=True
).start()

# =========================
# اجرا
# =========================

print("BOT STARTED 🚀")
app.run_polling()
