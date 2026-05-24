from telegram import ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import requests
import threading
import time

# =========================
# تنظیمات
# =========================

BOT_TOKEN = "8995261480:AAFi0H9lQyC8i3od5SjeyStlhwtdpWpCmj0"
CHAT_ID = "369031827"

# CoinGecko IDs (بدون تحریم)
COINS = {
    "BTCUSDT": "bitcoin",
    "ETHUSDT": "ethereum",
    "BNBUSDT": "binancecoin",
    "SOLUSDT": "solana",
    "XRPUSDT": "ripple",
    "DOGEUSDT": "dogecoin",
    "ADAUSDT": "cardano"
}

price_history = {}
user_targets = {}
last_alert = {}

# =========================
# گرفتن قیمت (CoinGecko)
# =========================

def get_price(symbol):
    try:
        coin_id = COINS.get(symbol)
        if not coin_id:
            return None

        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids": coin_id,
            "vs_currencies": "usd"
        }

        r = requests.get(url, params=params, timeout=10)
        data = r.json()

        return float(data[coin_id]["usd"])

    except Exception as e:
        print("PRICE ERROR:", e)
        return None

# =========================
# ارسال پیام تلگرام
# =========================

def send_message(text):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": text})
    except:
        pass

# =========================
# سیگنال
# =========================

def check_signal(symbol):
    price = get_price(symbol)
    if price is None:
        return

    now = time.time()

    if symbol in price_history:
        old_price, _ = price_history[symbol]

        change = ((price - old_price) / old_price) * 100

        # تارگت
        if symbol in user_targets:
            if price >= user_targets[symbol]:
                send_message(f"🎯 TARGET HIT\n{symbol}\nPrice: {price}")
                del user_targets[symbol]

        # ضد اسپم
        if symbol in last_alert:
            if now - last_alert[symbol] < 60:
                price_history[symbol] = (price, now)
                return

        # سیگنال‌ها
        if change >= 2:
            send_message(f"🚀 PUMP {symbol}\n{change:.2f}%\nPrice: {price}")
            last_alert[symbol] = now

        elif change <= -2:
            send_message(f"📉 DUMP {symbol}\n{change:.2f}%\nPrice: {price}")
            last_alert[symbol] = now

    price_history[symbol] = (price, now)

# =========================
# اسکنر
# =========================

def scanner():
    while True:
        for s in COINS.keys():
            check_signal(s)

        time.sleep(15)

# =========================
# تلگرام UI
# =========================

keyboard = [
    ["💰 قیمت‌ها"],
    ["📊 سیگنال"],
    ["🎯 تارگت"]
]

reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# =========================
# start
# =========================

async def start(update, context):
    await update.message.reply_text(
        "🤖 ربات فعال شد (نسخه ایران)\n\n"
        "📊 BTC / ETH / BNB / SOL / XRP / DOGE / ADA\n"
        "🚀 سیگنال خودکار فعال است",
        reply_markup=reply_markup
    )

# =========================
# قیمت همه
# =========================

async def prices(update, context):
    text = "💰 قیمت‌ها:\n\n"

    for s, cid in COINS.items():
        p = get_price(s)
        if p:
            text += f"{s}: {p}$\n"

    await update.message.reply_text(text)

# =========================
# راهنما سیگنال
# =========================

async def signals(update, context):
    await update.message.reply_text(
        "📊 سیستم سیگنال فعال:\n\n"
        "🚀 Pump / Dump > 2%\n"
        "⏱ بررسی هر 15 ثانیه\n"
        "📡 CoinGecko API (بدون تحریم)"
    )

# =========================
# تارگت
# =========================

async def target(update, context):
    try:
        symbol = context.args[0].upper()
        price = float(context.args[1])

        user_targets[symbol] = price

        await update.message.reply_text(
            f"🎯 تارگت ثبت شد\n{symbol} → {price}"
        )

    except:
        await update.message.reply_text(
            "مثال:\n/target BTCUSDT 80000"
        )

# =========================
# handler
# =========================

def handle(update, context):
    text = update.message.text

    if text == "💰 قیمت‌ها":
        return prices(update, context)

    if text == "📊 سیگنال":
        return signals(update, context)

    if text == "🎯 تارگت":
        update.message.reply_text("مثال:\n/target BTCUSDT 80000")

# =========================
# اجرا
# =========================

app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("target", target))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

threading.Thread(target=scanner, daemon=True).start()

print("BOT RUNNING 🚀")
app.run_polling()
