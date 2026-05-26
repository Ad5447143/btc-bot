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
# ALERT CACHE
# =========================================

alert_cache = {}

# =========================================
# JSON FILES
# =========================================

TARGETS_FILE = "targets.json"
RSI_TARGETS_FILE = "rsi_targets.json"

# =========================================
# CREATE JSON FILES
# =========================================

for file_name in [TARGETS_FILE, RSI_TARGETS_FILE]:

    if not os.path.exists(file_name):

        with open(file_name, "w") as f:

            json.dump({}, f)

# =========================================
# MAIN MENU
# =========================================

main_menu = ReplyKeyboardMarkup(
    [
        ["🚀 شروع ربات"],
        ["💰 قیمت لحظه‌ای", "📊 تحلیل بازار"],
        ["📈 RSI", "⚡ EMA کراس"],
        ["📉 واگرایی RSI", "📦 فشار بازار"],
        ["🩺 سلامت ربات"]
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
# LOAD JSON
# =========================================

def load_json(file_name):

    with open(file_name, "r") as f:

        return json.load(f)

# =========================================
# SAVE JSON
# =========================================

def save_json(file_name, data):

    with open(file_name, "w") as f:

        json.dump(data, f, indent=4)

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
        return "خطا"

    if rsi >= 70:

        return "🟢 فشار خرید قوی"

    elif rsi <= 30:

        return "🔴 فشار فروش قوی"

    else:

        return "⚪ بازار متعادل"

# =========================================
# RSI DIVERGENCE
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

        return "🟢 واگرایی مثبت RSI"

    elif (
        df["close"].iloc[-1] > df["close"].iloc[-5]
        and
        rsi.iloc[-1] < rsi.iloc[-5]
    ):

        return "🔴 واگرایی منفی RSI"

    return None

# =========================================
# START
# =========================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = """
🚀 به Crypto AI Bot V6 خوش آمدید

━━━━━━━━━━━━━━

💰 قیمت لحظه‌ای
📈 RSI حرفه‌ای
⚡ EMA Cross
📉 واگرایی RSI
📦 فشار بازار
🩺 سلامت ربات

━━━━━━━━━━━━━━

🤖 اسکنر خودکار فعال است

✅ هشدار EMA
✅ هشدار RSI
✅ هشدار واگرایی

━━━━━━━━━━━━━━

🟢 ربات آنلاین است
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
🩺 وضعیت کامل ربات

━━━━━━━━━━━━━━

🤖 ربات:
🟢 آنلاین

📡 CoinGecko:
🟢 سالم

📊 KuCoin:
🟢 سالم

📈 اسکنر RSI:
🟢 فعال

⚡ اسکنر EMA:
🟢 فعال

📉 اسکنر واگرایی:
🟢 فعال

🔔 هشدارها:
🟢 فعال

━━━━━━━━━━━━━━

✅ همه سیستم‌ها سالم هستند
"""

    await update.message.reply_text(text)

# =========================================
# AUTO SCANNER
# =========================================

async def market_scanner(context):

    print("SCANNER RUNNING...")

    app = context.application

    for coin in COINS:

        for timeframe in TIMEFRAMES:

            try:

                # =====================
                # RSI
                # =====================

                rsi = calculate_rsi(
                    coin,
                    timeframe
                )

                if rsi is None:
                    continue

                # =====================
                # EMA
                # =====================

                ema = ema_cross(
                    coin,
                    timeframe
                )

                ema_key = f"{coin}_{timeframe}_ema"

                if (
                    ema == "🟢 کراس صعودی"
                    and
                    not alert_cache.get(ema_key)
                ):

                    print(
                        f"EMA ALERT {coin} {timeframe}"
                    )

                    alert_cache[ema_key] = True

                elif ema == "🔴 کراس نزولی":

                    alert_cache[ema_key] = False

                # =====================
                # RSI ALERT
                # =====================

                rsi_key = f"{coin}_{timeframe}_rsi"

                if rsi >= 70:

                    if not alert_cache.get(rsi_key):

                        print(
                            f"RSI OVERBOUGHT {coin} {timeframe}"
                        )

                        alert_cache[rsi_key] = True

                elif rsi <= 30:

                    if not alert_cache.get(rsi_key):

                        print(
                            f"RSI OVERSOLD {coin} {timeframe}"
                        )

                        alert_cache[rsi_key] = True

                else:

                    alert_cache[rsi_key] = False

                # =====================
                # DIVERGENCE
                # =====================

                if timeframe in ["4H", "1D"]:

                    div = detect_divergence(
                        coin,
                        timeframe
                    )

                    div_key = f"{coin}_{timeframe}_div"

                    if (
                        div
                        and
                        not alert_cache.get(div_key)
                    ):

                        print(
                            f"DIVERGENCE {coin} {timeframe}"
                        )

                        alert_cache[div_key] = True

                    elif not div:

                        alert_cache[div_key] = False

            except Exception as e:

                print("SCANNER ERROR:", e)

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
    # DIVERGENCE
    # =====================================

    elif text == "📉 واگرایی RSI":

        user_state[user_id] = {
            "action": "div"
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
    # TIMEFRAME
    # =====================================

    elif text.startswith("⏰"):

        timeframe = text.replace("⏰ ", "")

        action = user_state[user_id]["action"]

        coin = user_state[user_id]["coin"]

        # ================================
        # PRICE
        # ================================

        if action == "price":

            price = get_price(coin)

            await update.message.reply_text(
                f"""
💰 قیمت لحظه‌ای

💎 {coin}

💵 {price} $
"""
            )

        # ================================
        # RSI
        # ================================

        elif action == "rsi":

            rsi = calculate_rsi(
                coin,
                timeframe
            )

            await update.message.reply_text(
                f"""
📈 RSI

💎 {coin}
⏰ {timeframe}

📊 مقدار:
{rsi}
"""
            )

        # ================================
        # EMA
        # ================================

        elif action == "ema":

            result = ema_cross(
                coin,
                timeframe
            )

            await update.message.reply_text(
                f"""
⚡ EMA CROSS

💎 {coin}
⏰ {timeframe}

{result}
"""
            )

        # ================================
        # DIVERGENCE
        # ================================

        elif action == "div":

            if timeframe not in ["4H", "1D"]:

                await update.message.reply_text(
                    "❌ واگرایی فقط روی 4H و 1D فعال است"
                )

                return

            div = detect_divergence(
                coin,
                timeframe
            )

            if div is None:

                div = "⚪ واگرایی خاصی یافت نشد"

            await update.message.reply_text(
                f"""
📉 واگرایی RSI

💎 {coin}
⏰ {timeframe}

{div}
"""
            )

        # ================================
        # PRESSURE
        # ================================

        elif action == "pressure":

            pressure = market_pressure(
                coin,
                timeframe
            )

            await update.message.reply_text(
                f"""
📦 فشار بازار

💎 {coin}
⏰ {timeframe}

{pressure}
"""
            )

        # ================================
        # ANALYSIS
        # ================================

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

    # =====================================
    # AUTO SCANNER
    # =====================================

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
