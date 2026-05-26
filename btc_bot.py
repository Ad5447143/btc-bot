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
# BOT TOKEN
# =========================================

BOT_TOKEN = "8995261480:AAFi0H9lQyC8i3od5SjeyStlhwtdpWpCmj0"

# =========================================
# COINS
# =========================================

COINS = [
    "BTC",
    "ETH",
    "BNB",
    "SOL",
    "XRP",
    "DOGE",
    "ADA",
    "TRX",
    "ZEC"
]

# =========================================
# COINGECKO IDS
# =========================================

COINGECKO_IDS = {
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
# MAIN MENU
# =========================================

main_menu = ReplyKeyboardMarkup(
    [
        ["🚀 شروع ربات"],
        ["💰 قیمت لحظه‌ای", "📊 تحلیل بازار"],
        ["📈 RSI", "⚡ EMA کراس"],
        ["📦 فشار بازار", "🩺 سلامت ربات"]
    ],
    resize_keyboard=True
)

# =========================================
# COIN KEYBOARD
# =========================================

def coin_keyboard():

    rows = []
    row = []

    for i, coin in enumerate(COINS, start=1):

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

        coin_id = COINGECKO_IDS[symbol]

        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"

        data = requests.get(
            url,
            timeout=10
        ).json()

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

        data = requests.get(
            url,
            timeout=10
        ).json()

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
# EMA CROSS
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
        return "خطا در دریافت دیتا"

    if rsi >= 70:

        return "🟢 فشار خرید قوی"

    elif rsi <= 30:

        return "🔴 فشار فروش قوی"

    else:

        return "⚪ بازار متعادل"

# =========================================
# START
# =========================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    welcome_message = """
🚀 به Crypto AI Bot V5 خوش آمدید

━━━━━━━━━━━━━━

📊 ربات تحلیل حرفه‌ای بازار ارز دیجیتال

💰 قیمت لحظه‌ای
📈 RSI حرفه‌ای
⚡ کراس EMA
📦 فشار بازار
🩺 سلامت ربات

━━━━━━━━━━━━━━

💎 ارزهای پشتیبانی‌شده:

BTC • ETH • BNB • SOL
XRP • DOGE • ADA • TRX • ZEC

━━━━━━━━━━━━━━

⏰ تایم‌فریم‌ها:

5m • 15m • 4H • 1D

━━━━━━━━━━━━━━

🟢 ربات آنلاین است
"""

    await update.message.reply_text(
        welcome_message,
        reply_markup=main_menu
    )

# =========================================
# HEALTH
# =========================================

async def health(update):

    text = """
🩺 وضعیت سیستم ربات

━━━━━━━━━━━━━━

🤖 وضعیت ربات:
🟢 آنلاین

📡 CoinGecko:
🟢 سالم

📊 KuCoin:
🟢 سالم

━━━━━━━━━━━━━━

✅ همه سیستم‌ها فعال هستند
"""

    await update.message.reply_text(text)

# =========================================
# MESSAGE HANDLER
# =========================================

async def messages(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text
    user_id = update.effective_user.id

    # =====================================
    # START
    # =====================================

    if text == "🚀 شروع ربات":

        await start(update, context)

    # =====================================
    # HEALTH
    # =====================================

    elif text == "🩺 سلامت ربات":

        await health(update)

    # =====================================
    # PRICE
    # =====================================

    elif text == "💰 قیمت لحظه‌ای":

        user_state[user_id] = {
            "action": "price"
        }

        await update.message.reply_text(
            "💎 ارز را انتخاب کن:",
            reply_markup=coin_keyboard()
        )

    # =====================================
    # RSI
    # =====================================

    elif text == "📈 RSI":

        user_state[user_id] = {
            "action": "rsi"
        }

        await update.message.reply_text(
            "💎 ارز را انتخاب کن:",
            reply_markup=coin_keyboard()
        )

    # =====================================
    # EMA
    # =====================================

    elif text == "⚡ EMA کراس":

        user_state[user_id] = {
            "action": "ema"
        }

        await update.message.reply_text(
            "💎 ارز را انتخاب کن:",
            reply_markup=coin_keyboard()
        )

    # =====================================
    # PRESSURE
    # =====================================

    elif text == "📦 فشار بازار":

        user_state[user_id] = {
            "action": "pressure"
        }

        await update.message.reply_text(
            "💎 ارز را انتخاب کن:",
            reply_markup=coin_keyboard()
        )

    # =====================================
    # ANALYSIS
    # =====================================

    elif text == "📊 تحلیل بازار":

        user_state[user_id] = {
            "action": "analysis"
        }

        await update.message.reply_text(
            "💎 ارز را انتخاب کن:",
            reply_markup=coin_keyboard()
        )

    # =====================================
    # COIN SELECT
    # =====================================

    elif text.startswith("💎"):

        coin = text.replace("💎 ", "")

        if coin not in COINS:
            return

        user_state[user_id]["coin"] = coin

        await update.message.reply_text(
            "⏰ تایم‌فریم را انتخاب کن:",
            reply_markup=timeframe_keyboard()
        )

    # =====================================
    # TIMEFRAME SELECT
    # =====================================

    elif text.startswith("⏰"):

        timeframe = text.replace("⏰ ", "")

        action = user_state[user_id]["action"]

        coin = user_state[user_id]["coin"]

        # =================================
        # PRICE
        # =================================

        if action == "price":

            price = get_price(coin)

            await update.message.reply_text(
                f"""
💰 قیمت لحظه‌ای

━━━━━━━━━━━━━━

💎 ارز: {coin}

💵 قیمت:
{price} $
"""
            )

        # =================================
        # RSI
        # =================================

        elif action == "rsi":

            rsi = calculate_rsi(
                coin,
                timeframe
            )

            status = "⚪ نرمال"

            if rsi >= 70:

                status = "🔴 اشباع خرید"

            elif rsi <= 30:

                status = "🟢 اشباع فروش"

            await update.message.reply_text(
                f"""
📈 تحلیل RSI

━━━━━━━━━━━━━━

💎 ارز: {coin}

⏰ تایم‌فریم: {timeframe}

📊 مقدار RSI:
{rsi}

{status}
"""
            )

        # =================================
        # EMA
        # =================================

        elif action == "ema":

            result = ema_cross(
                coin,
                timeframe
            )

            await update.message.reply_text(
                f"""
⚡ تحلیل EMA

━━━━━━━━━━━━━━

💎 ارز: {coin}

⏰ تایم‌فریم: {timeframe}

{result}
"""
            )

        # =================================
        # PRESSURE
        # =================================

        elif action == "pressure":

            result = market_pressure(
                coin,
                timeframe
            )

            await update.message.reply_text(
                f"""
📦 فشار بازار

━━━━━━━━━━━━━━

💎 ارز: {coin}

⏰ تایم‌فریم: {timeframe}

{result}
"""
            )

        # =================================
        # ANALYSIS
        # =================================

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
📊 تحلیل کامل بازار

━━━━━━━━━━━━━━

💎 ارز: {coin}

⏰ تایم‌فریم: {timeframe}

📈 RSI:
{rsi}

⚡ EMA:
{ema}

📦 فشار بازار:
{pressure}
"""
            )

        user_state.pop(user_id)

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

    print("BOT RUNNING 🚀")

    app.run_polling()

# =========================================
# RUN
# =========================================

if __name__ == "__main__":

    main()
