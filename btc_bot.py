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
import numpy as np
import pandas as pd

# =========================
# تنظیمات
# =========================

BOT_TOKEN = "8995261480:AAFi0H9lQyC8i3od5SjeyStlhwtdpWpCmj0"

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

# =========================
# گرفتن قیمت
# =========================

def get_price(symbol):

    try:

        coin_id = COINS.get(symbol)

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

        return float(data[coin_id]["usd"])

    except Exception as e:

        print("PRICE ERROR:", e)

        return None

# =========================
# کندل‌ها
# =========================

def get_klines(symbol, interval="1min"):

    try:

        kucoin_symbol = symbol.replace("USDT", "-USDT")

        url = (
            f"https://api.kucoin.com/api/v1/market/candles"
            f"?type={interval}&symbol={kucoin_symbol}"
        )

        r = requests.get(url, timeout=10)

        data = r.json()["data"]

        closes = []

        for candle in data[:250]:

            closes.append(float(candle[2]))

        closes.reverse()

        return closes

    except Exception as e:

        print("KLINE ERROR:", e)

        return None

# =========================
# RSI
# =========================

def calculate_rsi(prices, period=14):

    try:

        deltas = np.diff(prices)

        gains = []
        losses = []

        for d in deltas:

            if d >= 0:
                gains.append(d)
                losses.append(0)

            else:
                gains.append(0)
                losses.append(abs(d))

        avg_gain = np.mean(gains[:period])
        avg_loss = np.mean(losses[:period])

        if avg_loss == 0:
            return 100

        rs = avg_gain / avg_loss

        rsi = 100 - (100 / (1 + rs))

        return round(rsi, 2)

    except:
        return None

# =========================
# EMA
# =========================

def calculate_ema(prices, period):

    try:

        series = pd.Series(prices)

        ema = series.ewm(
            span=period,
            adjust=False
        ).mean()

        return round(float(ema.iloc[-1]), 2)

    except:
        return None

# =========================
# منوی ارزها
# =========================

def coin_menu():

    return InlineKeyboardMarkup([

        [
            InlineKeyboardButton(
                "🟡 BTC",
                callback_data="coin_BTCUSDT"
            ),

            InlineKeyboardButton(
                "🔵 ETH",
                callback_data="coin_ETHUSDT"
            )
        ],

        [
            InlineKeyboardButton(
                "🟠 BNB",
                callback_data="coin_BNBUSDT"
            ),

            InlineKeyboardButton(
                "🟢 SOL",
                callback_data="coin_SOLUSDT"
            )
        ],

        [
            InlineKeyboardButton(
                "🔴 XRP",
                callback_data="coin_XRPUSDT"
            ),

            InlineKeyboardButton(
                "⚫ DOGE",
                callback_data="coin_DOGEUSDT"
            )
        ],

        [
            InlineKeyboardButton(
                "🔷 ADA",
                callback_data="coin_ADAUSDT"
            ),

            InlineKeyboardButton(
                "⚪ USDT",
                callback_data="coin_USDT"
            )
        ]
    ])

# =========================
# منوی تایم‌فریم
# =========================

def timeframe_menu(symbol):

    return InlineKeyboardMarkup([

        [
            InlineKeyboardButton(
                "⏱ 1m",
                callback_data=f"tf_{symbol}_1min"
            ),

            InlineKeyboardButton(
                "⏱ 5m",
                callback_data=f"tf_{symbol}_5min"
            )
        ],

        [
            InlineKeyboardButton(
                "⏱ 4h",
                callback_data=f"tf_{symbol}_4hour"
            )
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
        "🤖 ربات حرفه‌ای کریپتو فعال شد",
        reply_markup=main_keyboard
    )

# =========================
# قیمت‌ها
# =========================

async def prices(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = "💰 قیمت ارزها:\n\n"

    for symbol in COINS:

        p = get_price(symbol)

        if p:
            text += f"{symbol}: {p}$\n"

    await update.message.reply_text(text)

# =========================
# سیگنال
# =========================

async def signal_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "📊 انتخاب ارز:",
        reply_markup=coin_menu()
    )

# =========================
# کلیک‌ها
# =========================

async def button_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    data = query.data

    if data.startswith("coin_"):

        symbol = data.replace("coin_", "")

        await query.edit_message_text(
            f"📊 {symbol}\n\n"
            f"⏱ تایم‌فریم را انتخاب کن",
            reply_markup=timeframe_menu(symbol)
        )

    elif data.startswith("tf_"):

        parts = data.split("_")

        symbol = parts[1]
        timeframe = parts[2]

        closes = get_klines(symbol, timeframe)

        if not closes:

            await query.edit_message_text(
                "❌ خطا در دریافت دیتا"
            )

            return

        rsi = calculate_rsi(closes)

        ema25 = calculate_ema(closes, 25)
        ema50 = calculate_ema(closes, 50)
        ema100 = calculate_ema(closes, 100)
        ema200 = calculate_ema(closes, 200)

        price = closes[-1]

        if rsi <= 35:
            signal = "🟢 BUY ZONE"

        elif rsi >= 65:
            signal = "🔴 SELL ZONE"

        elif 45 <= rsi <= 55:
            signal = "⚪ SIDEWAYS"

        else:
            signal = "🟡 NEUTRAL"

        trend = "⚪ SIDEWAYS"

        if ema25 > ema50 > ema100:
            trend = "🚀 BULLISH"

        elif ema25 < ema50 < ema100:
            trend = "📉 BEARISH"

        if ema25 > ema200:
            trend += "\n🔥 Above EMA200"

        else:
            trend += "\n❄️ Below EMA200"

        text = (
            f"📊 {symbol}\n\n"
            f"⏱ TF: {timeframe}\n"
            f"💰 Price: {price}$\n\n"
            f"📈 RSI: {rsi}\n"
            f"📡 Signal: {signal}\n\n"
            f"EMA25: {ema25}\n"
            f"EMA50: {ema50}\n"
            f"EMA100: {ema100}\n"
            f"EMA200: {ema200}\n\n"
            f"{trend}"
        )

        await query.edit_message_text(text)

# =========================
# دکمه‌ها
# =========================

async def handle_text(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    text = update.message.text

    if text == "💰 قیمت ارزها":
        await prices(update, context)

    elif text == "📊 سیگنال":
        await signal_menu(update, context)

# =========================
# اجرا
# =========================

app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_text
    )
)

app.add_handler(
    CallbackQueryHandler(button_handler)
)

print("BOT RUNNING 🚀")

if __name__ == "__main__":

    app.run_polling(
        drop_pending_updates=True
    )
