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

import ccxt
import pandas as pd
import ta
import asyncio
import threading
import time

# =====================================
# 🔑 TOKEN
# =====================================

BOT_TOKEN = "8995261480:AAFi0H9lQyC8i3od5SjeyStlhwtdpWpCmj0"

CHAT_ID = "369031827"

# =====================================
# 📡 BINANCE
# =====================================

exchange = ccxt.binance({
    "enableRateLimit": True,
    "timeout": 30000,
    "options": {
        "defaultType": "spot"
    }
})

# =====================================
# 💎 COINS
# =====================================

COINS = [
    "BTC/USDT",
    "ETH/USDT",
    "BNB/USDT",
    "SOL/USDT",
    "XRP/USDT",
    "DOGE/USDT",
    "ADA/USDT",
    "TRX/USDT",
    "ZEC/USDT"
]

# =====================================
# ⏰ TIMEFRAMES
# =====================================

TIMEFRAMES = {
    "5m": "5m",
    "15m": "15m",
    "4h": "4h",
    "1d": "1d"
}

# =====================================
# 📦 STORAGE
# =====================================

ema_cache = {}
targets = {}

# =====================================
# 🎛 MENU
# =====================================

main_keyboard = ReplyKeyboardMarkup(
    [
        ["🚀 شروع ربات"],
        ["💰 قیمت", "📊 سیگنال"],
        ["📈 RSI", "⚡ EMA CROSS"],
        ["🎯 تارگت"]
    ],
    resize_keyboard=True
)

# =====================================
# 📥 GET DATA
# =====================================

def get_ohlcv(symbol, timeframe):

    for attempt in range(3):

        try:

            bars = exchange.fetch_ohlcv(
                symbol,
                timeframe=timeframe,
                limit=200
            )

            df = pd.DataFrame(
                bars,
                columns=[
                    "time",
                    "open",
                    "high",
                    "low",
                    "close",
                    "volume"
                ]
            )

            return df

        except Exception as e:

            print(f"FETCH ERROR {symbol}: ", e)

            time.sleep(3)

    return None

# =====================================
# 📊 ANALYSIS
# =====================================

def analyze(symbol, timeframe):

    try:

        df = get_ohlcv(symbol, timeframe)

        if df is None:
            return None

        # EMA

        df["ema20"] = ta.trend.ema_indicator(
            df["close"],
            window=20
        )

        df["ema50"] = ta.trend.ema_indicator(
            df["close"],
            window=50
        )

        # RSI

        df["rsi"] = ta.momentum.RSIIndicator(
            df["close"],
            window=14
        ).rsi()

        last = df.iloc[-1]

        return {
            "price": last["close"],
            "ema20": last["ema20"],
            "ema50": last["ema50"],
            "rsi": last["rsi"],
            "volume": last["volume"]
        }

    except Exception as e:

        print("ANALYZE ERROR:", e)

        return None

# =====================================
# 🔔 ALERT
# =====================================

async def send_alert(app, text):

    try:

        await app.bot.send_message(
            chat_id=CHAT_ID,
            text=text
        )

    except Exception as e:

        print("ALERT ERROR:", e)

# =====================================
# 🧭 COIN MENU
# =====================================

def coin_menu(prefix):

    buttons = []

    row = []

    for coin in COINS:

        row.append(
            InlineKeyboardButton(
                coin,
                callback_data=f"{prefix}_{coin}"
            )
        )

        if len(row) == 2:

            buttons.append(row)

            row = []

    if row:
        buttons.append(row)

    return InlineKeyboardMarkup(buttons)

# =====================================
# ⏱ TIMEFRAME MENU
# =====================================

def timeframe_menu(prefix, symbol):

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "⚡5m",
                callback_data=f"{prefix}_{symbol}_5m"
            ),

            InlineKeyboardButton(
                "🔥15m",
                callback_data=f"{prefix}_{symbol}_15m"
            )
        ],

        [
            InlineKeyboardButton(
                "🌊4H",
                callback_data=f"{prefix}_{symbol}_4h"
            ),

            InlineKeyboardButton(
                "🌙1D",
                callback_data=f"{prefix}_{symbol}_1d"
            )
        ]
    ])

# =====================================
# 🚀 START
# =====================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "🤖 ربات حرفه‌ای کریپتو فعال شد 🚀",
        reply_markup=main_keyboard
    )

# =====================================
# 🎯 TARGET
# =====================================

async def target(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:

        symbol = context.args[0]

        price = float(context.args[1])

        targets[symbol] = price

        await update.message.reply_text(
            f"🎯 تارگت ثبت شد\n\n{symbol} → {price}"
        )

    except:

        await update.message.reply_text(
            "مثال:\n/target BTC/USDT 120000"
        )

# =====================================
# 🔘 BUTTON HANDLER
# =====================================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    data = query.data

    # PRICE

    if data.startswith("price_"):

        symbol = data.replace("price_", "")

        result = analyze(symbol, "15m")

        if result is None:

            await query.edit_message_text(
                "❌ خطا در دریافت دیتا"
            )

            return

        text = (
            f"💰 PRICE\n\n"
            f"💎 {symbol}\n\n"
            f"📌 {result['price']}"
        )

        await query.edit_message_text(text)

    # RSI MENU

    elif (
        data.startswith("rsi_")
        and "_5m" not in data
        and "_15m" not in data
        and "_4h" not in data
        and "_1d" not in data
    ):

        symbol = data.replace("rsi_", "")

        await query.edit_message_text(
            f"📈 RSI {symbol}",
            reply_markup=timeframe_menu("rsi", symbol)
        )

    # RSI RESULT

    elif data.startswith("rsi_"):

        parts = data.split("_")

        symbol = parts[1]

        tf = parts[2]

        result = analyze(symbol, tf)

        if result is None:

            await query.edit_message_text(
                "❌ خطا در دریافت دیتا"
            )

            return

        rsi = result["rsi"]

        status = "⚪ خنثی"

        if rsi >= 70:
            status = "🔴 اشباع خرید"

        elif rsi <= 30:
            status = "🟢 اشباع فروش"

        text = (
            f"📈 RSI ANALYSIS\n\n"
            f"💎 {symbol}\n"
            f"⏰ {tf}\n\n"
            f"📊 RSI: {rsi:.2f}\n\n"
            f"{status}"
        )

        await query.edit_message_text(text)

# =====================================
# ⚡ EMA CROSS
# =====================================

def ema_cross_checker(app):

    while True:

        try:

            for symbol in COINS:

                result = analyze(symbol, "15m")

                if result is None:
                    continue

                ema20 = result["ema20"]

                ema50 = result["ema50"]

                current = ema20 > ema50

                old = ema_cache.get(symbol)

                if old is not None:

                    if current and not old:

                        asyncio.run(
                            send_alert(
                                app,
                                f"🟢 GOLDEN CROSS\n\n"
                                f"{symbol}"
                            )
                        )

                    elif not current and old:

                        asyncio.run(
                            send_alert(
                                app,
                                f"🔴 DEATH CROSS\n\n"
                                f"{symbol}"
                            )
                        )

                ema_cache[symbol] = current

            time.sleep(60)

        except Exception as e:

            print("EMA ERROR:", e)

            time.sleep(60)

# =====================================
# ❤️ KEEP ALIVE
# =====================================

def keep_alive():

    while True:

        print("BOT STILL RUNNING 🚀")

        time.sleep(300)

# =====================================
# 💬 TEXT HANDLER
# =====================================

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text

    if text == "🚀 شروع ربات":

        await start(update, context)

    elif text == "💰 قیمت":

        await update.message.reply_text(
            "💰 انتخاب ارز:",
            reply_markup=coin_menu("price")
        )

    elif text == "📈 RSI":

        await update.message.reply_text(
            "📈 انتخاب ارز:",
            reply_markup=coin_menu("rsi")
        )

# =====================================
# ▶ RUN
# =====================================

app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))

app.add_handler(CommandHandler("target", target))

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        text_handler
    )
)

app.add_handler(
    CallbackQueryHandler(button_handler)
)

threading.Thread(
    target=ema_cross_checker,
    args=(app,),
    daemon=True
).start()

threading.Thread(
    target=keep_alive,
    daemon=True
).start()

print("BOT RUNNING 🚀")

asyncio.set_event_loop(asyncio.new_event_loop())

while True:

    try:

        app.run_polling(
            drop_pending_updates=True
        )

    except Exception as e:

        print("MAIN ERROR:", e)

        time.sleep(10)
