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
# تنظیمات
# =========================

BOT_TOKEN = "8995261480:AAFi0H9lQyC8i3od5SjeyStlhwtdpWpCmj0"
CHAT_ID = "369031827"

SYMBOLS = [
    "BTCUSDT",
    "ETHUSDT",
    "BNBUSDT",
    "SOLUSDT",
    "XRPUSDT",
    "ADAUSDT",
    "DOGEUSDT",
    "USDTUSDT"
]

# =========================
# تنظیمات سیگنال
# =========================

THRESHOLD_PERCENT = 2.0          # درصد حرکت
COOLDOWN_SECONDS = 60            # جلوگیری از اسپم

price_history = {}
last_alert_time = {}

# =========================
# گرفتن قیمت
# =========================

def get_price(symbol):
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        data = requests.get(url, timeout=10).json()
        return float(data["price"])
    except:
        return None

# =========================
# تلگرام
# =========================

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})

# =========================
# بررسی سیگنال
# =========================

def check_signal(symbol):
    price = get_price(symbol)
    if price is None:
        return

    now = time.time()

    # ذخیره اولیه
    if symbol not in price_history:
        price_history[symbol] = (price, now)
        return

    old_price, old_time = price_history[symbol]

    change = ((price - old_price) / old_price) * 100

    # cooldown
    if symbol in last_alert_time:
        if now - last_alert_time[symbol] < COOLDOWN_SECONDS:
            price_history[symbol] = (price, now)
            return

    signal = None

    if change >= THRESHOLD_PERCENT:
        signal = f"🚀 PUMP {symbol}"
    elif change <= -THRESHOLD_PERCENT:
        signal = f"📉 DUMP {symbol}"

    if signal:
        send_telegram_message(
            f"{signal}\n\n"
            f"💰 Price: {price:.4f}\n"
            f"📊 Change: {change:.2f}%"
        )
        last_alert_time[symbol] = now

    price_history[symbol] = (price, now)

# =========================
# اسکنر بازار
# =========================

def price_checker():
    while True:
        for symbol in SYMBOLS:
            check_signal(symbol)

        time.sleep(10)

# =========================
# تلگرام UI
# =========================

keyboard = [
    ["💰 قیمت BTC"],
    ["ℹ️ راهنما"]
]

reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# =========================
# start
# =========================

async def start(update, context):
    await update.message.reply_text(
        "🤖 ربات سیگنال فعال شد\n\n"
        "📊 BTC / ETH / BNB / SOL / XRP / ADA / DOGE\n"
        "🚀 Pump / Dump detection فعال است",
        reply_markup=reply_markup
    )

# =========================
# قیمت BTC
# =========================

async def price(update, context):
    price = get_price("BTCUSDT")
    await update.message.reply_text(f"💰 BTC: {price}")

# =========================
# راهنما
# =========================

async def help_command(update, context):
    await update.message.reply_text(
        "📚 راهنما:\n\n"
        "📊 ربات سیگنال خودکار\n"
        "🚀 تشخیص Pump / Dump\n"
        "⏱ هر 10 ثانیه اسکن"
    )

# =========================
# دکمه‌ها
# =========================

async def handle_message(update, context):
    text = update.message.text

    if text == "💰 قیمت BTC":
        price = get_price("BTCUSDT")
        await update.message.reply_text(f"💰 BTC: {price}")

    elif text == "ℹ️ راهنما":
        await help_command(update, context)

# =========================
# اجرا ربات
# =========================

app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("price", price))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

threading.Thread(target=price_checker, daemon=True).start()

print("BOT RUNNING 🚀")
app.run_polling()
