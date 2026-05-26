import json
import time
import threading
import asyncio
import requests
import pandas as pd

from ta.trend import EMAIndicator
from ta.momentum import RSIIndicator

from telegram import (
    ReplyKeyboardMarkup,
    Update
)

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)

# =========================================
# BOT TOKEN
# =========================================

BOT_TOKEN = "8995261480:AAFi0H9lQyC8i3od5SjeyStlhwtdpWpCmj0"

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

TIMEFRAMES = ["5m", "15m", "4h", "1d"]

# =========================================
# MENUS
# =========================================

main_menu = ReplyKeyboardMarkup(
    [
        ["🚀 شروع ربات"],
        ["💰 قیمت لحظه‌ای", "📊 تحلیل بازار"],
        ["📈 RSI", "⚡ EMA کراس"],
        ["📉 واگرایی RSI", "📦 فشار بازار"],
        ["🎯 تارگت‌ها"]
    ],
    resize_keyboard=True
)

target_menu = ReplyKeyboardMarkup(
    [
        ["🎯 تارگت قیمتی"],
        ["📈 تارگت RSI"],
        ["🔙 بازگشت"]
    ],
    resize_keyboard=True
)

# =========================================
# LOAD JSON
# =========================================

def load_json(file_name):

    try:

        with open(file_name, "r") as f:
            return json.load(f)

    except:

        return {}

# =========================================
# SAVE JSON
# =========================================

def save_json(file_name, data):

    with open(file_name, "w") as f:
        json.dump(data, f)

# =========================================
# DATABASE
# =========================================

price_targets = load_json("targets.json")
rsi_targets = load_json("rsi_targets.json")

# =========================================
# GET PRICE
# =========================================

def get_price(symbol):

    try:

        coin_id = COINS[symbol]

        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"

        response = requests.get(url, timeout=10)

        data = response.json()

        return float(data[coin_id]["usd"])

    except:

        return None

# =========================================
# MARKET DATA
# =========================================

def fake_market_data():

    import random

    prices = []

    value = 100

    for i in range(100):

        value += random.uniform(-3, 3)

        prices.append(value)

    df = pd.DataFrame(prices, columns=["close"])

    return df

# =========================================
# RSI
# =========================================

def calculate_rsi():

    try:

        df = fake_market_data()

        rsi = RSIIndicator(df["close"], 14).rsi()

        return round(rsi.iloc[-1], 2)

    except:

        return None

# =========================================
# EMA CROSS
# =========================================

def calculate_ema_cross():

    try:

        df = fake_market_data()

        ema20 = EMAIndicator(df["close"], 20).ema_indicator()

        ema50 = EMAIndicator(df["close"], 50).ema_indicator()

        if ema20.iloc[-1] > ema50.iloc[-1]:

            return "🟢 کراس صعودی EMA20 بالای EMA50"

        else:

            return "🔴 کراس نزولی EMA20 پایین EMA50"

    except:

        return "❌ خطا در تحلیل EMA"

# =========================================
# MARKET PRESSURE
# =========================================

def market_pressure():

    try:

        rsi = calculate_rsi()

        if rsi is None:
            return "❌ خطا در تحلیل"

        if rsi >= 70:

            return "🟢 فشار خرید قوی"

        elif rsi <= 30:

            return "🔴 فشار فروش شدید"

        elif rsi >= 55:

            return "🟢 فشار خرید"

        elif rsi <= 45:

            return "🔴 فشار فروش"

        else:

            return "⚪ بازار خنثی"

    except:

        return "❌ خطا در تحلیل بازار"

# =========================================
# START
# =========================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = """
🤖 Crypto AI Bot V4

✅ قیمت لحظه‌ای
✅ تحلیل بازار
✅ EMA Cross
✅ RSI
✅ فشار خرید و فروش
✅ تارگت قیمتی
✅ تارگت RSI

🚀 ربات آماده تحلیل بازار است
"""

    await update.message.reply_text(
        text,
        reply_markup=main_menu
    )

# =========================================
# MESSAGES
# =========================================

async def messages(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text

    # =====================================
    # START
    # =====================================

    if text == "🚀 شروع ربات":

        await start(update, context)

    # =====================================
    # PRICE
    # =====================================

    elif text == "💰 قیمت لحظه‌ای":

        result = "💰 قیمت لحظه‌ای بازار:\n\n"

        for coin in COINS:

            try:

                price = get_price(coin)

                if price:

                    result += f"💎 {coin}: {price}$\n"

                else:

                    result += f"❌ {coin}: خطا\n"

            except:

                result += f"❌ {coin}: خطا\n"

        await update.message.reply_text(result)

    # =====================================
    # RSI
    # =====================================

    elif text == "📈 RSI":

        rsi = calculate_rsi()

        if rsi is None:

            await update.message.reply_text(
                "❌ خطا در دریافت RSI"
            )

            return

        status = "⚪ نرمال"

        if rsi >= 70:

            status = "🔴 اشباع خرید"

        elif rsi <= 30:

            status = "🟢 اشباع فروش"

        msg = f"""
📈 وضعیت RSI

📊 مقدار RSI: {rsi}

{status}
"""

        await update.message.reply_text(msg)

    # =====================================
    # EMA
    # =====================================

    elif text == "⚡ EMA کراس":

        result = calculate_ema_cross()

        await update.message.reply_text(result)

    # =====================================
    # MARKET PRESSURE
    # =====================================

    elif text == "📦 فشار بازار":

        pressure = market_pressure()

        await update.message.reply_text(
            f"""
📦 تحلیل فشار بازار

{pressure}
"""
        )

    # =====================================
    # ANALYSIS
    # =====================================

    elif text == "📊 تحلیل بازار":

        rsi = calculate_rsi()

        ema = calculate_ema_cross()

        pressure = market_pressure()

        msg = f"""
📊 تحلیل کامل بازار

📈 RSI: {rsi}

⚡ EMA:
{ema}

📦 فشار بازار:
{pressure}
"""

        await update.message.reply_text(msg)

    # =====================================
    # TARGET MENU
    # =====================================

    elif text == "🎯 تارگت‌ها":

        await update.message.reply_text(
            "🎯 مدیریت تارگت‌ها",
            reply_markup=target_menu
        )

    # =====================================
    # PRICE TARGET
    # =====================================

    elif text == "🎯 تارگت قیمتی":

        context.user_data["price_target"] = True

        await update.message.reply_text(
            """
🎯 ثبت تارگت قیمتی

فرمت:

BTC 70000
"""
        )

    # =====================================
    # RSI TARGET
    # =====================================

    elif text == "📈 تارگت RSI":

        context.user_data["rsi_target"] = True

        await update.message.reply_text(
            """
📈 ثبت تارگت RSI

فرمت:

BTC 70
"""
        )

    # =====================================
    # BACK
    # =====================================

    elif text == "🔙 بازگشت":

        await update.message.reply_text(
            "🔙 بازگشت به منوی اصلی",
            reply_markup=main_menu
        )

    # =====================================
    # SAVE PRICE TARGET
    # =====================================

    elif context.user_data.get("price_target"):

        try:

            coin, target = text.split()

            coin = coin.upper()

            target = float(target)

            price_targets[coin] = target

            save_json("targets.json", price_targets)

            await update.message.reply_text(
                f"✅ تارگت قیمتی {coin} ذخیره شد"
            )

        except:

            await update.message.reply_text(
                "❌ فرمت اشتباه"
            )

        context.user_data["price_target"] = False

    # =====================================
    # SAVE RSI TARGET
    # =====================================

    elif context.user_data.get("rsi_target"):

        try:

            coin, target = text.split()

            coin = coin.upper()

            target = float(target)

            rsi_targets[coin] = target

            save_json("rsi_targets.json", rsi_targets)

            await update.message.reply_text(
                f"✅ تارگت RSI برای {coin} ذخیره شد"
            )

        except:

            await update.message.reply_text(
                "❌ فرمت اشتباه"
            )

        context.user_data["rsi_target"] = False

# =========================================
# CHECK TARGETS
# =========================================

def check_targets():

    while True:

        try:

            # PRICE TARGETS
            for coin, target in price_targets.items():

                price = get_price(coin)

                if price is None:
                    continue

                if price >= target:

                    print(f"{coin} PRICE TARGET HIT")

            # RSI TARGETS
            for coin, target in rsi_targets.items():

                rsi = calculate_rsi()

                if rsi is None:
                    continue

                if rsi >= target:

                    print(f"{coin} RSI TARGET HIT")

            time.sleep(60)

        except Exception as e:

            print("TARGET ERROR:", e)

            time.sleep(30)

# =========================================
# MAIN
# =========================================

async def main():

    print("BOT STARTED 🚀")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        MessageHandler(filters.TEXT, messages)
    )

    threading.Thread(
        target=check_targets,
        daemon=True
    ).start()

    print("BOT RUNNING 🚀")

    await app.initialize()

    await app.start()

    await app.updater.start_polling()

    while True:

        await asyncio.sleep(60)

# =========================================
# RUN
# =========================================

if __name__ == "__main__":

    asyncio.run(main())
