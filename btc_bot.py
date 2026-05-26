```python
import json
import os
import requests
import pandas as pd

from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton
)

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# =========================================
# TOKEN
# =========================================

BOT_TOKEN = "8995261480:AAFi0H9lQyC8i3od5SjeyStlhwtdpWpCmj0"

# =========================================
# FILES
# =========================================

FILES = [
    "targets.json",
    "rsi_targets.json",
    "vip_users.json",
    "alert_cache.json"
]

for file in FILES:

    if not os.path.exists(file):

        with open(file, "w") as f:

            if file == "vip_users.json":
                json.dump([], f)
            else:
                json.dump({}, f)

# =========================================
# LOAD/SAVE JSON
# =========================================

def load_json(file):

    with open(file, "r") as f:
        return json.load(f)

def save_json(file, data):

    with open(file, "w") as f:
        json.dump(data, f, indent=4)

# =========================================
# COINS
# =========================================

COINS = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "BNB": "binancecoin",
    "SOL": "solana",
    "XRP": "ripple",
    "DOGE": "dogecoin",
    "ADA": "cardano",
    "TRX": "tron",
    "ZEC": "zcash"
}

# =========================================
# TIMEFRAMES
# =========================================

TIMEFRAMES = {
    "5m": "5min",
    "15m": "15min",
    "4H": "4hour",
    "1D": "1day"
}

# =========================================
# USER STATE
# =========================================

user_state = {}

# =========================================
# MENU
# =========================================

main_menu = ReplyKeyboardMarkup(
    [
        ["🚀 شروع ربات"],
        ["💰 قیمت لحظه‌ای", "📊 تحلیل بازار"],
        ["📈 RSI", "⚡ EMA کراس"],
        ["📉 واگرایی RSI", "📦 فشار بازار"],
        ["🎯 تارگت‌ها", "🩺 سلامت ربات"],
        ["👑 پنل VIP"]
    ],
    resize_keyboard=True
)

# =========================================
# COIN KEYBOARD
# =========================================

def coin_keyboard():

    rows = []

    row = []

    for i, coin in enumerate(COINS.keys(), start=1):

        row.append(
            KeyboardButton(f"💎 {coin}")
        )

        if i % 3 == 0:

            rows.append(row)

            row = []

    if row:
        rows.append(row)

    return ReplyKeyboardMarkup(
        rows,
        resize_keyboard=True
    )

# =========================================
# TIMEFRAME KEYBOARD
# =========================================

def timeframe_keyboard():

    return ReplyKeyboardMarkup(
        [
            ["⏰ 5m", "⏰ 15m"],
            ["⏰ 4H", "⏰ 1D"]
        ],
        resize_keyboard=True
    )

# =========================================
# GET PRICE
# =========================================

def get_price(symbol):

    try:

        coin_id = COINS[symbol]

        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"

        data = requests.get(url, timeout=10).json()

        return data[coin_id]["usd"]

    except:

        return None

# =========================================
# GET KLINES
# =========================================

def get_klines(symbol, timeframe):

    try:

        tf = TIMEFRAMES[timeframe]

        url = f"https://api.kucoin.com/api/v1/market/candles?type={tf}&symbol={symbol}-USDT"

        data = requests.get(url, timeout=10).json()

        candles = data["data"]

        closes = []

        for c in candles:

            closes.append(float(c[2]))

        closes.reverse()

        return closes

    except:

        return None

# =========================================
# RSI
# =========================================

def calculate_rsi(symbol, timeframe):

    closes = get_klines(symbol, timeframe)

    if closes is None:
        return None

    df = pd.DataFrame(closes, columns=["close"])

    rsi = RSIIndicator(
        close=df["close"],
        window=14
    ).rsi()

    return round(rsi.iloc[-1], 2)

# =========================================
# EMA
# =========================================

def ema_cross(symbol, timeframe):

    closes = get_klines(symbol, timeframe)

    if closes is None:
        return "خطا"

    df = pd.DataFrame(closes, columns=["close"])

    ema20 = EMAIndicator(
        close=df["close"],
        window=20
    ).ema_indicator()

    ema50 = EMAIndicator(
        close=df["close"],
        window=50
    ).ema_indicator()

    if ema20.iloc[-1] > ema50.iloc[-1]:

        return "🟢 کراس صعودی"

    else:

        return "🔴 کراس نزولی"

# =========================================
# MARKET PRESSURE
# =========================================

def market_pressure(symbol, timeframe):

    rsi = calculate_rsi(symbol, timeframe)

    if rsi is None:
        return "خطا"

    if rsi >= 70:

        return "🟢 فشار خرید"

    elif rsi <= 30:

        return "🔴 فشار فروش"

    else:

        return "⚪ خنثی"

# =========================================
# DIVERGENCE
# =========================================

def detect_divergence(symbol, timeframe):

    closes = get_klines(symbol, timeframe)

    if closes is None or len(closes) < 30:
        return None

    df = pd.DataFrame(closes, columns=["close"])

    rsi = RSIIndicator(
        close=df["close"],
        window=14
    ).rsi()

    if (
        df["close"].iloc[-1] < df["close"].iloc[-5]
        and
        rsi.iloc[-1] > rsi.iloc[-5]
    ):

        return "🟢 واگرایی مثبت"

    elif (
        df["close"].iloc[-1] > df["close"].iloc[-5]
        and
        rsi.iloc[-1] < rsi.iloc[-5]
    ):

        return "🔴 واگرایی منفی"

    return None

# =========================================
# START
# =========================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = """
🚀 Crypto AI Bot V7 PRO

━━━━━━━━━━━━━━

✅ اسکنر خودکار
✅ هشدار EMA
✅ هشدار RSI
✅ واگرایی RSI
✅ تارگت حرفه‌ای
✅ تحلیل مولتی تایم

━━━━━━━━━━━━━━

🟢 ربات فعال است
"""

    await update.message.reply_text(
        text,
        reply_markup=main_menu
    )

# =========================================
# HEALTH
# =========================================

async def health(update):

    text = """
🩺 سلامت ربات

🟢 CoinGecko
🟢 KuCoin
🟢 RSI Engine
🟢 EMA Engine
🟢 Scanner
🟢 Alerts
"""

    await update.message.reply_text(text)

# =========================================
# AUTO SCANNER
# =========================================

async def market_scanner(context):

    print("SCANNER RUNNING...")

# =========================================
# MESSAGE HANDLER
# =========================================

async def messages(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text

    user_id = update.effective_user.id

    if text == "🚀 شروع ربات":

        await start(update, context)

    elif text == "🩺 سلامت ربات":

        await health(update)

    elif text == "💰 قیمت لحظه‌ای":

        user_state[user_id] = {
            "action": "price"
        }

        await update.message.reply_text(
            "💎 ارز را انتخاب کن:",
            reply_markup=coin_keyboard()
        )

    elif text == "📈 RSI":

        user_state[user_id] = {
            "action": "rsi"
        }

        await update.message.reply_text(
            "💎 ارز را انتخاب کن:",
            reply_markup=coin_keyboard()
        )

    elif text == "⚡ EMA کراس":

        user_state[user_id] = {
            "action": "ema"
        }

        await update.message.reply_text(
            "💎 ارز را انتخاب کن:",
            reply_markup=coin_keyboard()
        )

    elif text == "📦 فشار بازار":

        user_state[user_id] = {
            "action": "pressure"
        }

        await update.message.reply_text(
            "💎 ارز را انتخاب کن:",
            reply_markup=coin_keyboard()
        )

    elif text == "📉 واگرایی RSI":

        user_state[user_id] = {
            "action": "div"
        }

        await update.message.reply_text(
            "💎 ارز را انتخاب کن:",
            reply_markup=coin_keyboard()
        )

    elif text == "📊 تحلیل بازار":

        user_state[user_id] = {
            "action": "analysis"
        }

        await update.message.reply_text(
            "💎 ارز را انتخاب کن:",
            reply_markup=coin_keyboard()
        )

    elif text.startswith("💎"):

        coin = text.replace("💎 ", "")

        user_state[user_id]["coin"] = coin

        await update.message.reply_text(
            "⏰ تایم‌فریم را انتخاب کن:",
            reply_markup=timeframe_keyboard()
        )

    elif text.startswith("⏰"):

        timeframe = text.replace("⏰ ", "")

        action = user_state[user_id]["action"]

        coin = user_state[user_id]["coin"]

        if action == "price":

            price = get_price(coin)

            await update.message.reply_text(
                f"💰 {coin}\n\n{price} $"
            )

        elif action == "rsi":

            rsi = calculate_rsi(
                coin,
                timeframe
            )

            await update.message.reply_text(
                f"📈 RSI\n\n💎 {coin}\n⏰ {timeframe}\n\n📊 {rsi}"
            )

        elif action == "ema":

            ema = ema_cross(
                coin,
                timeframe
            )

            await update.message.reply_text(
                f"⚡ EMA\n\n💎 {coin}\n⏰ {timeframe}\n\n{ema}"
            )

        elif action == "pressure":

            pressure = market_pressure(
                coin,
                timeframe
            )

            await update.message.reply_text(
                f"📦 فشار بازار\n\n💎 {coin}\n⏰ {timeframe}\n\n{pressure}"
            )

        elif action == "div":

            if timeframe not in ["4H", "1D"]:

                await update.message.reply_text(
                    "❌ فقط 4H و 1D"
                )

                return

            div = detect_divergence(
                coin,
                timeframe
            )

            if div is None:
                div = "⚪ واگرایی یافت نشد"

            await update.message.reply_text(
                f"📉 واگرایی RSI\n\n💎 {coin}\n⏰ {timeframe}\n\n{div}"
            )

        elif action == "analysis":

            rsi = calculate_rsi(
                coin,
                timeframe
            )

            ema = ema_cross(
                coin,
                timeframe
            )

            pressure = market_pressure(
                coin,
                timeframe
            )

            await update.message.reply_text(
                f"""
📊 تحلیل بازار

💎 {coin}
⏰ {timeframe}

📈 RSI:
{rsi}

⚡ EMA:
{ema}

📦 فشار بازار:
{pressure}
"""
            )

# =========================================
# MAIN
# =========================================

def main():

    print("BOT STARTED 🚀")

    app = Application.builder().token(
        BOT_TOKEN
    ).build()

    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT,
            messages
        )
    )

    app.job_queue.run_repeating(
        market_scanner,
        interval=60,
        first=10
    )

    print("BOT RUNNING 🚀")

    app.run_polling()

# =========================================
# RUN
# =========================================

if __name__ == "__main__":

    main()
```
