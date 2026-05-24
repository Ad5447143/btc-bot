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

# =========================
# تنظیمات
# =========================

BOT_TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "369031827"

# =========================
# ارزها
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

price_history = {}
user_targets = {}

# =========================
# قیمت
# =========================

def get_price(symbol):
    try:
        coin_id = COINS.get(symbol)
        if not coin_id:
            return None

        r = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": coin_id, "vs_currencies": "usd"},
            timeout=10
        )
        data = r.json()

        return float(data[coin_id]["usd"])

    except:
        return None

# =========================
# UI
# =========================

def coin_menu():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("BTC", callback_data="coin_BTCUSDT"),
            InlineKeyboardButton("ETH", callback_data="coin_ETHUSDT")
        ],
        [
            InlineKeyboardButton("BNB", callback_data="coin_BNBUSDT"),
            InlineKeyboardButton("SOL", callback_data="coin_SOLUSDT")
        ],
        [
            InlineKeyboardButton("XRP", callback_data="coin_XRPUSDT"),
            InlineKeyboardButton("DOGE", callback_data="coin_DOGEUSDT")
        ],
        [
            InlineKeyboardButton("ADA", callback_data="coin_ADAUSDT"),
            InlineKeyboardButton("USDT", callback_data="coin_USDT")
        ]
    ])

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
        "🤖 ربات فعال شد\n\n"
        "📊 سیگنال + قیمت + تارگت",
        reply_markup=main_keyboard
    )

# =========================
# قیمت‌ها
# =========================

async def prices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "💰 قیمت‌ها:\n\n"

    for s in COINS:
        p = get_price(s)
        if p:
            text += f"{s}: {p}$\n"

    await update.message.reply_text(text)

# =========================
# منوی سیگنال
# =========================

async def signal_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📊 انتخاب ارز:", reply_markup=coin_menu())

# =========================
# تارگت
# =========================

async def target(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        symbol = context.args[0].upper()
        price = float(context.args[1])

        user_targets[symbol] = price

        await update.message.reply_text(f"🎯 تارگت ثبت شد: {symbol} → {price}")

    except:
        await update.message.reply_text("مثال:\n/target BTCUSDT 80000")

# =========================
# سیگنال
# =========================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    symbol = query.data.replace("coin_", "")

    price = get_price(symbol)
    if not price:
        await query.edit_message_text("❌ قیمت دریافت نشد")
        return

    old = price_history.get(symbol, price)
    change = ((price - old) / old) * 100 if old else 0
    price_history[symbol] = price

    if change >= 2:
        signal = "🚀 PUMP"
    elif change <= -2:
        signal = "📉 DUMP"
    else:
        signal = "⚪ NEUTRAL"

    await query.edit_message_text(
        f"📊 {symbol}\n\n"
        f"💰 Price: {price}$\n"
        f"📈 Change: {change:.2f}%\n"
        f"📡 Signal: {signal}"
    )

# =========================
# دکمه‌ها
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
# اجرا
# =========================

app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("target", target))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
app.add_handler(CallbackQueryHandler(button_handler))

print("BOT RUNNING 🚀")

if __name__ == "__main__":
    app.run_polling(drop_pending_updates=True)
