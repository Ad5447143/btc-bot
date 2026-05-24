from telegram import (
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Update
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
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

# =========================
# ارزها (CoinGecko)
# =========================

COINS = {
    "BTCUSDT": "bitcoin",
    "ETHUSDT": "ethereum",
    "BNBUSDT": "binancecoin",
    "SOLUSDT": "solana",
    "XRPUSDT": "ripple",
    "DOGEUSDT": "dogecoin",
    "ADAUSDT": "cardano",
    "USDT": "tether"
}

# =========================
# وضعیت‌ها
# =========================

price_history = {}
user_targets = {}
last_alert = {}

# =========================
# گرفتن قیمت (بدون تحریم)
# =========================

def get_price(symbol):
    try:
        coin_id = COINS.get(symbol)
        if not coin_id:
            return None

        url = "https://api.coingecko.com/api/v3/simple/price"
        r = requests.get(
            url,
            params={"ids": coin_id, "vs_currencies": "usd"},
            timeout=10
        )
        data = r.json()

        return float(data[coin_id]["usd"])

    except Exception as e:
        print("PRICE ERROR:", e)
        return None

# =========================
# ارسال پیام تلگرام
# =========================

def send_message(text):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": text})
    except:
        pass

# =========================
# منوی انتخاب ارز
# =========================

def coin_menu():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🟡 BTC", callback_data="coin_BTCUSDT"),
            InlineKeyboardButton("🔵 ETH", callback_data="coin_ETHUSDT")
        ],
        [
            InlineKeyboardButton("🟠 BNB", callback_data="coin_BNBUSDT"),
            InlineKeyboardButton("🟢 SOL", callback_data="coin_SOLUSDT")
        ],
        [
            InlineKeyboardButton("🔴 XRP", callback_data="coin_XRPUSDT"),
            InlineKeyboardButton("⚫ DOGE", callback_data="coin_DOGEUSDT")
        ],
        [
            InlineKeyboardButton("🔷 ADA", callback_data="coin_ADAUSDT"),
            InlineKeyboardButton("⚪ USDT", callback_data="coin_USDT")
        ]
    ])

# =========================
# منوی اصلی
# =========================

main_keyboard = ReplyKeyboardMarkup(
    [
        ["💰 قیمت ارزها"],
        ["📊 سیگنال"],
        ["🎯 تارگت"]
    ],
    resize_keyboard=True
)

# =========================
# start
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 ربات سیگنال کریپتو فعال شد\n\n"
        "📊 انتخاب ارز + سیگنال اختصاصی + تارگت",
        reply_markup=main_keyboard
    )

# =========================
# گرفتن قیمت
# =========================

async def prices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "💰 قیمت ارزها:\n\n"

    for s in COINS:
        p = get_price(s)
        if p:
            text += f"{s}: {p}$\n"

    await update.message.reply_text(text)

# =========================
# منوی انتخاب ارز برای سیگنال
# =========================

async def signal_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📊 یک ارز برای سیگنال انتخاب کن 👇",
        reply_markup=coin_menu()
    )

# =========================
# تارگت
# =========================

async def target(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        symbol = context.args[0].upper()
        price = float(context.args[1])

        user_targets[symbol] = price

        await update.message.reply_text(
            f"🎯 تارگت ثبت شد\n{symbol} → {price}"
        )

    except:
        await update.message.reply_text(
            "مثال:\n/target BTCUSDT 80000"
        )

# =========================
# کلیک روی ارزها (سیگنال اختصاصی)
# =========================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data.startswith("coin_"):
        symbol = data.replace("coin_", "")

        price = get_price(symbol)

        # سیگنال ساده بر اساس حرکت فرضی (آپدیت بعدی میشه واقعی‌تر)
        old = price_history.get(symbol, price)
        change = ((price - old) / old) * 100 if old else 0

        price_history[symbol] = price

        signal = "⚪ NEUTRAL"
        if change >= 2:
            signal = "🚀 PUMP"
        elif change <= -2:
            signal = "📉 DUMP"

        text = (
            f"📊 {symbol}\n\n"
            f"💰 Price: {price}$\n"
            f"📈 Change: {change:.2f}%\n"
            f"📡 Signal: {signal}"
        )

        await query.edit_message_text(text)

# =========================
# پیام‌های متنی
# =========================

def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "💰 قیمت ارزها":
        return prices(update, context)

    if text == "📊 سیگنال":
        return signal_menu(update, context)

    if text == "🎯 تارگت":
        update.message.reply_text("مثال:\n/target BTCUSDT 80000")

# =========================
# اجرای ربات
# =========================

app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("target", target))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
app.add_handler(CallbackQueryHandler(button_handler))

print("BOT RUNNING 🚀")
app.run_polling()
