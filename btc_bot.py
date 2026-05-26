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
import requests

# =========================================
# TOKEN
# =========================================

BOT_TOKEN = "8995261480:AAFi0H9lQyC8i3od5SjeyStlhwtdpWpCmj0"

CHAT_ID = "369031827"

# =========================================
# EXCHANGES
# =========================================

binance = ccxt.binance({
    "enableRateLimit": True,
    "timeout": 30000,
    "options": {
        "defaultType": "spot"
    }
})

kucoin = ccxt.kucoin({
    "enableRateLimit": True,
    "timeout": 30000
})

bybit = ccxt.bybit({
    "enableRateLimit": True,
    "timeout": 30000
})

# =========================================
# COINS
# =========================================

COINS = {
    "🟡 BTC": "BTC/USDT",
    "🔵 ETH": "ETH/USDT",
    "🟠 BNB": "BNB/USDT",
    "🟢 SOL": "SOL/USDT",
    "🔴 XRP": "XRP/USDT",
    "⚫ DOGE": "DOGE/USDT",
    "🟣 ADA": "ADA/USDT",
    "⚡ TRX": "TRX/USDT",
    "☠️ ZEC": "ZEC/USDT"
}

# =========================================
# TIMEFRAMES
# =========================================

TIMEFRAMES = {
    "5m": "5m",
    "15m": "15m",
    "4h": "4h",
    "1d": "1d"
}

# =========================================
# STORAGE
# =========================================

ema_cache = {}
targets = {}

# =========================================
# MENU
# =========================================

main_keyboard = ReplyKeyboardMarkup(
    [
        ["🚀 شروع ربات"],
        ["💰 قیمت", "📊 سیگنال"],
        ["📈 RSI", "⚡ EMA CROSS"],
        ["🎯 تارگت"]
    ],
    resize_keyboard=True
)

# =========================================
# COINGECKO PRICE
# =========================================

def get_coingecko_price(symbol):

    try:

        ids = {
            "BTC/USDT": "bitcoin",
            "ETH/USDT": "ethereum",
            "BNB/USDT": "binancecoin",
            "SOL/USDT": "solana",
            "XRP/USDT": "ripple",
            "DOGE/USDT": "dogecoin",
            "ADA/USDT": "cardano",
            "TRX/USDT": "tron",
            "ZEC/USDT": "zcash"
        }

        coin_id = ids.get(symbol)

        if not coin_id:
            return None

        url = "https://api.coingecko.com/api/v3/simple/price"

        r = requests.get(
            url,
            params={
                "ids": coin_id,
                "vs_currencies": "usd"
            },
            timeout=10
        )

        data = r.json()

        return data[coin_id]["usd"]

    except Exception as e:

        print("COINGECKO ERROR:", e)

        return None

# =========================================
# FETCH OHLCV
# =========================================

def get_ohlcv(symbol, timeframe):

    # =========================
    # BINANCE
    # =========================

    try:

        bars = binance.fetch_ohlcv(
            symbol,
            timeframe=timeframe,
            limit=120
        )

        time.sleep(0.2)

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

        print("BINANCE FAIL:", e)

    # =========================
    # BYBIT
    # =========================

    try:

        bars = bybit.fetch_ohlcv(
            symbol,
            timeframe=timeframe,
            limit=120
        )

        time.sleep(0.2)

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

        print("BYBIT FAIL:", e)

    # =========================
    # KUCOIN
    # =========================

    try:

        bars = kucoin.fetch_ohlcv(
            symbol,
            timeframe=timeframe,
            limit=120
        )

        time.sleep(0.2)

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

        print("KUCOIN FAIL:", e)

    return None

# =========================================
# ANALYZE
# =========================================

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

        # SIGNAL

        signal = "⚪ NEUTRAL"

        if last["ema20"] > last["ema50"] and last["rsi"] > 55:
            signal = "🟢 BUY"

        elif last["ema20"] < last["ema50"] and last["rsi"] < 45:
            signal = "🔴 SELL"

        return {
            "price": float(last["close"]),
            "ema20": float(last["ema20"]),
            "ema50": float(last["ema50"]),
            "rsi": float(last["rsi"]),
            "volume": float(last["volume"]),
            "signal": signal
        }

    except Exception as e:

        print("ANALYZE ERROR:", e)

        return None

# =========================================
# SEND ALERT
# =========================================

async def send_alert(app, text):

    try:

        await app.bot.send_message(
            chat_id=CHAT_ID,
            text=text
        )

    except Exception as e:

        print("ALERT ERROR:", e)

# =========================================
# COIN MENU
# =========================================

def coin_menu(prefix):

    buttons = []

    row = []

    for label, symbol in COINS.items():

        row.append(
            InlineKeyboardButton(
                label,
                callback_data=f"{prefix}|{symbol}"
            )
        )

        if len(row) == 2:

            buttons.append(row)

            row = []

    if row:
        buttons.append(row)

    return InlineKeyboardMarkup(buttons)

# =========================================
# TIMEFRAME MENU
# =========================================

def timeframe_menu(prefix, symbol):

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "⚡5m",
                callback_data=f"{prefix}|{symbol}|5m"
            ),

            InlineKeyboardButton(
                "🔥15m",
                callback_data=f"{prefix}|{symbol}|15m"
            )
        ],

        [
            InlineKeyboardButton(
                "🌊4H",
                callback_data=f"{prefix}|{symbol}|4h"
            ),

            InlineKeyboardButton(
                "🌙1D",
                callback_data=f"{prefix}|{symbol}|1d"
            )
        ]
    ])

# =========================================
# START
# =========================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "🤖 ربات حرفه‌ای کریپتو فعال شد 🚀",
        reply_markup=main_keyboard
    )

# =========================================
# TARGET
# =========================================

async def target(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:

        symbol = context.args[0]

        price = float(context.args[1])

        targets[symbol] = price

        await update.message.reply_text(
            f"🎯 تارگت ثبت شد\n\n"
            f"{symbol} → {price}"
        )

    except:

        await update.message.reply_text(
            "مثال:\n"
            "/target BTC/USDT 120000"
        )

# =========================================
# BUTTON HANDLER
# =========================================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    data = query.data

    # =====================================
    # PRICE
    # =====================================

    if data.startswith("price|"):

        symbol = data.split("|")[1]

        result = analyze(symbol, "15m")

        price = None

        if result:
            price = result["price"]

        if price is None:
            price = get_coingecko_price(symbol)

        if price is None:

            await query.edit_message_text(
                "❌ خطا در دریافت دیتا"
            )

            return

        text = (
            f"💰 قیمت لحظه‌ای\n\n"
            f"💎 {symbol}\n\n"
            f"📌 {price}"
        )

        await query.edit_message_text(text)

    # =====================================
    # RSI MENU
    # =====================================

    elif (
        data.startswith("rsi|")
        and "|5m" not in data
        and "|15m" not in data
        and "|4h" not in data
        and "|1d" not in data
    ):

        symbol = data.split("|")[1]

        await query.edit_message_text(
            f"📈 RSI\n\n💎 {symbol}",
            reply_markup=timeframe_menu("rsi", symbol)
        )

    # =====================================
    # RSI RESULT
    # =====================================

    elif data.startswith("rsi|"):

        parts = data.split("|")

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

# =========================================
# EMA CROSS ALERT
# =========================================

def ema_cross_checker(app):

    while True:

        try:

            for symbol in COINS.values():

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
                                f"💎 {symbol}"
                            )
                        )

                    elif not current and old:

                        asyncio.run(
                            send_alert(
                                app,
                                f"🔴 DEATH CROSS\n\n"
                                f"💎 {symbol}"
                            )
                        )

                ema_cache[symbol] = current

            time.sleep(180)

        except Exception as e:

            print("EMA ERROR:", e)

            time.sleep(60)

# =========================================
# TARGET CHECKER
# =========================================

def target_checker(app):

    while True:

        try:

            for symbol, target_price in targets.items():

                result = analyze(symbol, "15m")

                if result is None:
                    continue

                price = result["price"]

                if price >= target_price:

                    asyncio.run(
                        send_alert(
                            app,
                            f"🎯 TARGET HIT\n\n"
                            f"💎 {symbol}\n"
                            f"📌 {price}"
                        )
                    )

                    del targets[symbol]

                    break

            time.sleep(120)

        except Exception as e:

            print("TARGET ERROR:", e)

            time.sleep(60)

# =========================================
# KEEP ALIVE
# =========================================

def keep_alive():

    while True:

        print("BOT STILL RUNNING 🚀")

        time.sleep(300)

# =========================================
# TEXT HANDLER
# =========================================

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

# =========================================
# RUN
# =========================================

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
    target=target_checker,
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
