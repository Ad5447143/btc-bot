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

from tradingview_ta import TA_Handler, Interval
import asyncio
import threading
import time

# =========================
# 🔑 TOKEN
# =========================

BOT_TOKEN = "8995261480:AAFi0H9lQyC8i3od5SjeyStlhwtdpWpCmj0"

# =========================
# 💎 COINS
# =========================

COINS = {
    "🟡 BTC": ("BINANCE", "BTCUSDT"),
    "🔵 ETH": ("BINANCE", "ETHUSDT"),
    "🟠 BNB": ("BINANCE", "BNBUSDT"),
    "🟢 SOL": ("BINANCE", "SOLUSDT"),
    "🔴 XRP": ("BINANCE", "XRPUSDT"),
    "⚫ DOGE": ("BINANCE", "DOGEUSDT"),
    "🟣 ADA": ("BINANCE", "ADAUSDT"),
    "🔶 TRX": ("BINANCE", "TRXUSDT"),
    "💎 ZEC": ("BINANCE", "ZECUSDT"),
    "🔥 HYPE": ("MEXC", "HYPEUSDT"),
    "🧠 UB": ("MEXC", "UBUSDT"),
    "🥇 GOLD": ("OANDA", "XAUUSD"),
    "🥈 SILVER": ("OANDA", "XAGUSD"),
    "💵 USDT": ("CRYPTOCAP", "USDT")
}

# =========================
# ⏱ TIMEFRAMES
# =========================

TIMEFRAMES = {
    "5m": Interval.INTERVAL_5_MINUTES,
    "15m": Interval.INTERVAL_15_MINUTES,
    "4h": Interval.INTERVAL_4_HOURS,
    "1d": Interval.INTERVAL_1_DAY
}

# =========================
# 📦 STORAGE
# =========================

user_targets = {}
rsi_targets = {}
ema_cache = {}
divergence_cache = {}

# =========================
# 🎛 MENU
# =========================

main_keyboard = ReplyKeyboardMarkup(
    [
        ["🚀 شروع ربات"],
        ["💰 قیمت 💰", "📊 سیگنال 📊"],
        ["📈 RSI 📈", "🎯 RSI TARGET 🎯"],
        ["📦 VOLUME 📦", "💧 LIQUIDITY 💧"],
        ["⚡ EMA CROSS ⚡", "🎯 TARGET PRICE 🎯"]
    ],
    resize_keyboard=True
)

# =========================
# 🔎 ANALYSIS
# =========================

def get_analysis(symbol, interval=Interval.INTERVAL_15_MINUTES):

    try:
        exchange, tv_symbol = COINS[symbol]

        screener = "crypto"
        if exchange == "OANDA":
            screener = "forex"

        handler = TA_Handler(
            symbol=tv_symbol,
            screener=screener,
            exchange=exchange,
            interval=interval
        )

        return handler.get_analysis()

    except:
        return None

# =========================
# 💰 PRICE
# =========================

def get_price(symbol):
    analysis = get_analysis(symbol)
    if analysis:
        return analysis.indicators.get("close")
    return None

# =========================
# 🔔 ALERT SYSTEM
# =========================

def send_multi_alert(app, text):

    try:
        for i in range(3):
            asyncio.run(
                app.bot.send_message(
                    chat_id="369031827",
                    text=f"{text}\n\n🔔 Alert {i+1}"
                )
            )
            time.sleep(2)

    except:
        pass

# =========================
# 🧭 MENU BUILDER
# =========================

def coin_menu(prefix):

    buttons = []
    row = []

    for icon_symbol in COINS.keys():

        row.append(
            InlineKeyboardButton(
                icon_symbol,
                callback_data=f"{prefix}_{icon_symbol}"
            )
        )

        if len(row) == 2:
            buttons.append(row)
            row = []

    if row:
        buttons.append(row)

    return InlineKeyboardMarkup(buttons)

def timeframe_menu(prefix, symbol):

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⚡5m", callback_data=f"{prefix}_{symbol}_5m"),
            InlineKeyboardButton("🔥15m", callback_data=f"{prefix}_{symbol}_15m")
        ],
        [
            InlineKeyboardButton("🌊4h", callback_data=f"{prefix}_{symbol}_4h"),
            InlineKeyboardButton("🌙1D", callback_data=f"{prefix}_{symbol}_1d")
        ]
    ])

# =========================
# 🚀 START
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "🤖 ربات حرفه‌ای فعال شد 🚀\n\n"
        "💰 قیمت\n📊 سیگنال\n📈 RSI\n🎯 RSI TARGET\n⚡ EMA CROSS\n📦 VOLUME\n💧 LIQUIDITY",
        reply_markup=main_keyboard
    )

# =========================
# 🎯 TARGET PRICE
# =========================

async def target(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:
        symbol = context.args[0]
        price = float(context.args[1])

        user_targets[symbol] = price

        await update.message.reply_text(
            f"🎯 Target Set\n💎 {symbol} → {price}"
        )

    except:
        await update.message.reply_text("مثال: /target BTCUSDT 70000")

# =========================
# 📊 HANDLER
# =========================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    data = query.data

    # RSI
    if data.startswith("rsi_"):

        symbol = data.split("_")[1]
        tf = data.split("_")[2]

        analysis = get_analysis(symbol, TIMEFRAMES[tf])
        rsi = analysis.indicators["RSI"]

        status = "⚪"
        if rsi >= 70:
            status = "🔴 Overbought"
        elif rsi <= 30:
            status = "🟢 Oversold"

        await query.edit_message_text(
            f"📈 RSI {symbol}\n⏱ {tf}\n\n📊 RSI: {rsi:.2f}\n{status}"
        )

# =========================
# 🧠 EMA CROSS
# =========================

def ema_checker(app):

    while True:

        try:

            for symbol in COINS.keys():

                analysis = get_analysis(symbol)

                ema20 = analysis.indicators.get("EMA20")
                ema50 = analysis.indicators.get("EMA50")

                if not ema20 or not ema50:
                    continue

                state = ema20 > ema50
                old = ema_cache.get(symbol)

                if old is not None:

                    if state and not old:
                        send_multi_alert(app, f"🟢 GOLDEN CROSS 💎 {symbol}")

                    elif not state and old:
                        send_multi_alert(app, f"🔴 DEATH CROSS 💎 {symbol}")

                ema_cache[symbol] = state

            time.sleep(60)

        except:
            time.sleep(60)

# =========================
# 📉 RSI DIVERGENCE
# =========================

def divergence_checker(app):

    while True:

        try:

            for symbol in COINS.keys():

                analysis = get_analysis(symbol, Interval.INTERVAL_4_HOURS)

                rsi = analysis.indicators.get("RSI")
                price = analysis.indicators.get("close")

                key = symbol

                old = divergence_cache.get(key)

                if old:

                    if price > old["price"] and rsi < old["rsi"]:
                        send_multi_alert(app, f"🔴 Bearish Divergence 💎 {symbol}")

                    if price < old["price"] and rsi > old["rsi"]:
                        send_multi_alert(app, f"🟢 Bullish Divergence 💎 {symbol}")

                divergence_cache[key] = {"price": price, "rsi": rsi}

            time.sleep(180)

        except:
            time.sleep(180)

# =========================
# 💬 TEXT HANDLER
# =========================

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text

    if text == "🚀 شروع ربات":
        await start(update, context)

    elif text == "📈 RSI 📈":
        await update.message.reply_text("انتخاب ارز:", reply_markup=coin_menu("rsi"))

    elif text == "🎯 RSI TARGET 🎯":
        await update.message.reply_text("انتخاب ارز:", reply_markup=coin_menu("rsitarget"))

    elif text == "📊 سیگنال 📊":
        await update.message.reply_text("انتخاب ارز:", reply_markup=coin_menu("signal"))

    elif text == "💰 قیمت 💰":
        await update.message.reply_text("انتخاب ارز:", reply_markup=coin_menu("price"))

# =========================
# ▶ RUN
# =========================

app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("target", target))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
app.add_handler(CallbackQueryHandler(button_handler))

threading.Thread(target=ema_checker, args=(app,), daemon=True).start()
threading.Thread(target=divergence_checker, args=(app,), daemon=True).start()

print("BOT RUNNING 🚀")

app.run_polling(drop_pending_updates=True)
