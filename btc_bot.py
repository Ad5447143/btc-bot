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
import json
import os

# =========================================
# TOKEN
# =========================================

BOT_TOKEN = "8995261480:AAFi0H9lQyC8i3od5SjeyStlhwtdpWpCmj0"

CHAT_ID = "369031827"

# =========================================
# EXCHANGES
# =========================================

exchange = ccxt.kucoin({
    "enableRateLimit": True,
    "timeout": 30000
})

backup_exchange = ccxt.bybit({
    "enableRateLimit": True,
    "timeout": 30000
})

# =========================================
# FILES
# =========================================

TARGET_FILE = "rsi_targets.json"

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
# STORAGE
# =========================================

ema_cache = {}
target_alerts = {}
rsi_targets = {}

# =========================================
# LOAD TARGETS
# =========================================

if os.path.exists(TARGET_FILE):

    try:

        with open(TARGET_FILE, "r") as f:

            rsi_targets = json.load(f)

    except:

        rsi_targets = {}

# =========================================
# SAVE TARGETS
# =========================================

def save_targets():

    try:

        with open(TARGET_FILE, "w") as f:

            json.dump(rsi_targets, f)

    except Exception as e:

        print("SAVE ERROR:", e)

# =========================================
# MENU
# =========================================

main_keyboard = ReplyKeyboardMarkup(
    [
        ["🚀 شروع ربات"],
        ["💰 قیمت", "📊 سیگنال"],
        ["📈 RSI", "🎯 تارگت RSI"],
        ["⚡ EMA کراس", "📉 واگرایی RSI"]
    ],
    resize_keyboard=True
)

# =========================================
# COINGECKO PRICE
# =========================================

def get_live_price(symbol):

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
            timeout=15
        )

        data = r.json()

        return data[coin_id]["usd"]

    except Exception as e:

        print("PRICE ERROR:", e)

        return None

# =========================================
# GET OHLCV
# =========================================

def get_ohlcv(symbol, timeframe):

    try:

        bars = exchange.fetch_ohlcv(
            symbol,
            timeframe=timeframe,
            limit=120
        )

    except:

        try:

            bars = backup_exchange.fetch_ohlcv(
                symbol,
                timeframe=timeframe,
                limit=120
            )

        except:

            return None

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

# =========================================
# DIVERGENCE
# =========================================

def detect_divergence(df):

    try:

        closes = df["close"]

        rsi = ta.momentum.RSIIndicator(
            closes,
            window=14
        ).rsi()

        price_now = closes.iloc[-1]
        price_old = closes.iloc[-5]

        rsi_now = rsi.iloc[-1]
        rsi_old = rsi.iloc[-5]

        if price_now < price_old and rsi_now > rsi_old:

            return "🟢 واگرایی مثبت"

        elif price_now > price_old and rsi_now < rsi_old:

            return "🔴 واگرایی منفی"

        return None

    except:

        return None

# =========================================
# ANALYZE
# =========================================

def analyze(symbol, timeframe):

    try:

        df = get_ohlcv(symbol, timeframe)

        if df is None:
            return None

        df["ema20"] = ta.trend.ema_indicator(
            df["close"],
            window=20
        )

        df["ema50"] = ta.trend.ema_indicator(
            df["close"],
            window=50
        )

        df["rsi"] = ta.momentum.RSIIndicator(
            df["close"],
            window=14
        ).rsi()

        last = df.iloc[-1]

        signal = "⚪ NEUTRAL"

        strength = 0

        if last["ema20"] > last["ema50"]:
            strength += 1
        else:
            strength -= 1

        if last["rsi"] > 55:
            strength += 1

        elif last["rsi"] < 45:
            strength -= 1

        if strength >= 2:
            signal = "🟢 STRONG BUY"

        elif strength == 1:
            signal = "🟢 BUY"

        elif strength == -1:
            signal = "🔴 SELL"

        elif strength <= -2:
            signal = "🔴 STRONG SELL"

        return {
            "price": float(last["close"]),
            "ema20": float(last["ema20"]),
            "ema50": float(last["ema50"]),
            "rsi": float(last["rsi"]),
            "signal": signal,
            "volume": float(last["volume"])
        }

    except Exception as e:

        print("ANALYZE ERROR:", e)

        return None

# =========================================
# ALERT
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
        "🤖 Crypto AI Bot V3 فعال شد 🚀\n\n"
        "✅ Smart Signal Engine\n"
        "✅ EMA Cross Alert\n"
        "✅ RSI Divergence\n"
        "✅ RSI Targets\n"
        "✅ Real-Time Price\n"
        "✅ Multi TimeFrame\n"
        "✅ Stable System\n\n"
        "📊 ربات آماده تحلیل حرفه‌ای بازار است.",
        reply_markup=main_keyboard
    )

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

    elif text == "📊 سیگنال":

        await update.message.reply_text(
            "📊 انتخاب ارز:",
            reply_markup=coin_menu("signal")
        )

    elif text == "📈 RSI":

        await update.message.reply_text(
            "📈 انتخاب ارز:",
            reply_markup=coin_menu("rsi")
        )

    elif text == "🎯 تارگت RSI":

        await update.message.reply_text(
            "🎯 انتخاب ارز:",
            reply_markup=coin_menu("rsi_target")
        )

    elif text == "⚡ EMA کراس":

        await update.message.reply_text(
            "⚡ انتخاب ارز:",
            reply_markup=coin_menu("ema_manual")
        )

    elif text == "📉 واگرایی RSI":

        await update.message.reply_text(
            "📉 انتخاب ارز:",
            reply_markup=coin_menu("divergence")
        )

# =========================================
# BUTTON HANDLER
# =========================================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    data = query.data

    # PRICE

    if data.startswith("price|"):

        symbol = data.split("|")[1]

        price = get_live_price(symbol)

        if price is None:

            await query.edit_message_text(
                "❌ خطا در دریافت قیمت"
            )

            return

        await query.edit_message_text(
            f"💰 قیمت لحظه‌ای\n\n"
            f"💎 {symbol}\n\n"
            f"📌 {price}$"
        )

    # SIGNAL

    elif data.startswith("signal|"):

        symbol = data.split("|")[1]

        await query.edit_message_text(
            f"📊 انتخاب تایم فریم\n\n{symbol}",
            reply_markup=timeframe_menu(
                "signal_tf",
                symbol
            )
        )

    elif data.startswith("signal_tf|"):

        parts = data.split("|")

        symbol = parts[1]

        tf = parts[2]

        result = analyze(symbol, tf)

        if result is None:

            await query.edit_message_text("❌ خطا")

            return

        await query.edit_message_text(
            f"📊 SIGNAL\n\n"
            f"💎 {symbol}\n"
            f"⏰ {tf}\n\n"
            f"{result['signal']}\n\n"
            f"📈 RSI: {result['rsi']:.2f}"
        )

    # RSI

    elif data.startswith("rsi|"):

        symbol = data.split("|")[1]

        await query.edit_message_text(
            f"📈 انتخاب تایم فریم\n\n{symbol}",
            reply_markup=timeframe_menu(
                "rsi_tf",
                symbol
            )
        )

    elif data.startswith("rsi_tf|"):

        parts = data.split("|")

        symbol = parts[1]

        tf = parts[2]

        result = analyze(symbol, tf)

        if result is None:

            await query.edit_message_text("❌ خطا")

            return

        rsi = result["rsi"]

        status = "⚪ NORMAL"

        if rsi >= 70:
            status = "🔴 OVERBOUGHT"

        elif rsi <= 30:
            status = "🟢 OVERSOLD"

        await query.edit_message_text(
            f"📈 RSI\n\n"
            f"💎 {symbol}\n"
            f"⏰ {tf}\n\n"
            f"📊 RSI: {rsi:.2f}\n\n"
            f"{status}"
        )

    # RSI TARGET

    elif data.startswith("rsi_target|"):

        symbol = data.split("|")[1]

        await query.edit_message_text(
            f"🎯 انتخاب تایم فریم\n\n{symbol}",
            reply_markup=timeframe_menu(
                "rsi_target_tf",
                symbol
            )
        )

    elif data.startswith("rsi_target_tf|"):

        parts = data.split("|")

        symbol = parts[1]

        tf = parts[2]

        rsi_targets[symbol] = {
            "tf": tf,
            "rsi": 70
        }

        save_targets()

        await query.edit_message_text(
            f"✅ TARGET ذخیره شد\n\n"
            f"💎 {symbol}\n"
            f"⏰ {tf}\n\n"
            f"🎯 RSI = 70"
        )

    # EMA MANUAL

    elif data.startswith("ema_manual|"):

        symbol = data.split("|")[1]

        await query.edit_message_text(
            f"⚡ انتخاب تایم فریم\n\n{symbol}",
            reply_markup=timeframe_menu(
                "ema_manual_tf",
                symbol
            )
        )

    elif data.startswith("ema_manual_tf|"):

        parts = data.split("|")

        symbol = parts[1]

        tf = parts[2]

        result = analyze(symbol, tf)

        if result is None:

            await query.edit_message_text("❌ خطا")

            return

        cross = "❌ کراسی وجود ندارد"

        if result["ema20"] > result["ema50"]:

            cross = "🟢 EMA20 بالای EMA50"

        elif result["ema20"] < result["ema50"]:

            cross = "🔴 EMA20 پایین EMA50"

        await query.edit_message_text(
            f"⚡ EMA CROSS\n\n"
            f"💎 {symbol}\n"
            f"⏰ {tf}\n\n"
            f"{cross}"
        )

    # DIVERGENCE

    elif data.startswith("divergence|"):

        symbol = data.split("|")[1]

        await query.edit_message_text(
            f"📉 انتخاب تایم فریم\n\n{symbol}",
            reply_markup=timeframe_menu(
                "div_tf",
                symbol
            )
        )

    elif data.startswith("div_tf|"):

        parts = data.split("|")

        symbol = parts[1]

        tf = parts[2]

        df = get_ohlcv(symbol, tf)

        if df is None:

            await query.edit_message_text("❌ خطا")

            return

        div = detect_divergence(df)

        if div is None:

            div = "⚪ واگرایی خاصی یافت نشد"

        await query.edit_message_text(
            f"📉 RSI DIVERGENCE\n\n"
            f"💎 {symbol}\n"
            f"⏰ {tf}\n\n"
            f"{div}"
        )

# =========================================
# EMA CHECKER
# =========================================

def ema_checker(app):

    while True:

        try:

            for symbol in COINS.values():

                result = analyze(symbol, "15m")

                if result is None:
                    continue

                current = (
                    result["ema20"] >
                    result["ema50"]
                )

                old = ema_cache.get(symbol)

                if old is not None:

                    if current and not old:

                        asyncio.run(
                            send_alert(
                                app,
                                f"🟢 GOLDEN CROSS\n\n💎 {symbol}"
                            )
                        )

                        asyncio.run(
                            send_alert(
                                app,
                                f"🚀 روند صعودی فعال شد\n\n{symbol}"
                            )
                        )

                    elif not current and old:

                        asyncio.run(
                            send_alert(
                                app,
                                f"🔴 DEATH CROSS\n\n💎 {symbol}"
                            )
                        )

                        asyncio.run(
                            send_alert(
                                app,
                                f"⚠️ روند نزولی فعال شد\n\n{symbol}"
                            )
                        )

                ema_cache[symbol] = current

                df = get_ohlcv(symbol, "4h")

                if df is not None:

                    div = detect_divergence(df)

                    if div:

                        asyncio.run(
                            send_alert(
                                app,
                                f"{div}\n\n💎 {symbol}\n⏰ 4H"
                            )
                        )

                        asyncio.run(
                            send_alert(
                                app,
                                f"📉 هشدار واگرایی RSI\n\n{symbol}"
                            )
                        )

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

            for symbol, target_data in rsi_targets.items():

                timeframe = target_data["tf"]

                target_rsi = target_data["rsi"]

                result = analyze(symbol, timeframe)

                if result is None:
                    continue

                current_rsi = result["rsi"]

                cache_key = f"{symbol}_{timeframe}"

                old = target_alerts.get(cache_key)

                if current_rsi >= target_rsi:

                    if old != "hit":

                        asyncio.run(
                            send_alert(
                                app,
                                f"🎯 RSI TARGET HIT\n\n"
                                f"💎 {symbol}\n"
                                f"⏰ {timeframe}\n\n"
                                f"📈 RSI: {current_rsi:.2f}"
                            )
                        )

                        target_alerts[cache_key] = "hit"

                else:

                    target_alerts[cache_key] = None

            time.sleep(120)

        except Exception as e:

            print("TARGET ERROR:", e)

            time.sleep(30)

# =========================================
# KEEP ALIVE
# =========================================

def keep_alive():

    while True:

        print("BOT RUNNING 🚀")

        time.sleep(300)

# =========================================
# RUN
# =========================================

app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(
    CommandHandler("start", start)
)

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
    target=ema_checker,
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

print("BOT STARTED 🚀")

asyncio.set_event_loop(
    asyncio.new_event_loop()
)

while True:

    try:

        app.run_polling(
            drop_pending_updates=True
        )

    except Exception as e:

        print("MAIN ERROR:", e)

        time.sleep(10)
