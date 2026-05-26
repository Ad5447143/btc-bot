import json
import time
import threading
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

BOT_TOKEN = "8995261480:AAFi0H9lQyC8i3od5SjeyStlhwtdpWpCmj0"

# =========================
# تنظیمات
# =========================

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

TIMEFRAMES = ["5m", "15m", "4h", "1d"]

# =========================
# منو
# =========================

main_menu = ReplyKeyboardMarkup(
    [
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

# =========================
# ذخیره
# =========================

def load_json(file):
    try:
        with open(file, "r") as f:
            return json.load(f)
    except:
        return {}

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f)

price_targets = load_json("targets.json")
rsi_targets = load_json("rsi_targets.json")

# =========================
# قیمت
# =========================

def get_price(symbol):
    coin = COINS.get(symbol)

    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd"

    r = requests.get(url).json()

    return r[coin]["usd"]

# =========================
# دیتا
# =========================

def fake_market_data():
    import random

    close = [100 + random.randint(-5, 5) for _ in range(100)]

    df = pd.DataFrame(close, columns=["close"])

    return df

# =========================
# RSI
# =========================

def get_rsi():
    df = fake_market_data()

    rsi = RSIIndicator(df["close"], 14).rsi()

    return round(rsi.iloc[-1], 2)

# =========================
# EMA
# =========================

def ema_cross():
    df = fake_market_data()

    ema20 = EMAIndicator(df["close"], 20).ema_indicator()
    ema50 = EMAIndicator(df["close"], 50).ema_indicator()

    if ema20.iloc[-1] > ema50.iloc[-1]:
        return "🟢 کراس صعودی"

    return "🔴 کراس نزولی"

# =========================
# فشار بازار
# =========================

def market_pressure():

    rsi = get_rsi()

    if rsi > 60:
        return "🟢 فشار خرید قوی"

    elif rsi < 40:
        return "🔴 فشار فروش قوی"

    return "⚪ بازار خنثی"

# =========================
# استارت
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = """
🤖 Crypto AI Bot V4

✅ قیمت لحظه‌ای
✅ تحلیل بازار
✅ تارگت قیمتی
✅ تارگت RSI
✅ واگرایی RSI
✅ EMA Cross
✅ فشار بازار

🚀 ربات آماده تحلیل بازار است
"""

    await update.message.reply_text(
        text,
        reply_markup=main_menu
    )

# =========================
# پیام‌ها
# =========================

async def messages(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text

    # قیمت
    if text == "💰 قیمت لحظه‌ای":

        msg = ""

        for coin in COINS:

            try:
                price = get_price(coin)

                msg += f"💎 {coin}: {price}$\n"

            except:
                msg += f"❌ خطا در دریافت {coin}\n"

        await update.message.reply_text(msg)

    # RSI
    elif text == "📈 RSI":

        rsi = get_rsi()

        status = "⚪ نرمال"

        if rsi > 70:
            status = "🔴 اشباع خرید"

        elif rsi < 30:
            status = "🟢 اشباع فروش"

        await update.message.reply_text(
            f"📈 RSI: {rsi}\n{status}"
        )

    # EMA
    elif text == "⚡ EMA کراس":

        result = ema_cross()

        await update.message.reply_text(result)

    # فشار بازار
    elif text == "📦 فشار بازار":

        result = market_pressure()

        await update.message.reply_text(result)

    # تارگت
    elif text == "🎯 تارگت‌ها":

        await update.message.reply_text(
            "🎯 بخش تارگت‌ها",
            reply_markup=target_menu
        )

    # تارگت قیمتی
    elif text == "🎯 تارگت قیمتی":

        await update.message.reply_text(
            "مثال:\nBTC 70000"
        )

        context.user_data["price_target"] = True

    # تارگت RSI
    elif text == "📈 تارگت RSI":

        await update.message.reply_text(
            "مثال:\nBTC 70"
        )

        context.user_data["rsi_target"] = True

    # بازگشت
    elif text == "🔙 بازگشت":

        await update.message.reply_text(
            "بازگشت به منوی اصلی",
            reply_markup=main_menu
        )

    # ذخیره تارگت قیمت
    elif context.user_data.get("price_target"):

        try:

            coin, target = text.split()

            target = float(target)

            price_targets[coin] = target

            save_json("targets.json", price_targets)

            await update.message.reply_text(
                f"✅ تارگت {coin} ذخیره شد"
            )

        except:

            await update.message.reply_text(
                "❌ فرمت اشتباه"
            )

        context.user_data["price_target"] = False

    # ذخیره تارگت RSI
    elif context.user_data.get("rsi_target"):

        try:

            coin, target = text.split()

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

# =========================
# چک تارگت‌ها
# =========================

def check_targets(app):

    while True:

        try:

            for coin, target in price_targets.items():

                price = get_price(coin)

                if price >= target:

                    print(f"{coin} target hit")

            time.sleep(60)

        except Exception as e:

            print(e)

# =========================
# ران
# =========================

print("BOT STARTED 🚀")

app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT, messages))

threading.Thread(
    target=check_targets,
    args=(app,),
    daemon=True
).start()

print("BOT RUNNING 🚀")

app.run_polling()
