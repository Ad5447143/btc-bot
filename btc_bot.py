from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

import ccxt
import pandas as pd
import numpy as np
import sqlite3
import asyncio
import time
import threading

# =========================
# 🔑 BOT TOKEN (SIMPLE MODE)
# =========================
BOT_TOKEN = "8995261480:AAFi0H9lQyC8i3od5SjeyStlhwtdpWpCmj0"
CHAT_ID = "369031827"

# =========================
# 💎 COINS
# =========================
COINS = {
    "🟡 BTC": "BTC/USDT",
    "🔵 ETH": "ETH/USDT",
    "🟠 BNB": "BNB/USDT",
    "🟢 SOL": "SOL/USDT",
    "🔴 XRP": "XRP/USDT",
    "⚫ DOGE": "DOGE/USDT",
    "🟣 ADA": "ADA/USDT",
    "🔶 TRX": "TRX/USDT"
}

# =========================
# 📡 BINANCE
# =========================
exchange = ccxt.binance({"enableRateLimit": True})

# =========================
# 🗄 DATABASE (ANTI DUPLICATE)
# =========================
conn = sqlite3.connect("signals.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS signals (
    symbol TEXT,
    type TEXT,
    time INTEGER
)
""")
conn.commit()

def already_sent(symbol, sig_type, cooldown=300):
    cursor.execute(
        "SELECT time FROM signals WHERE symbol=? AND type=? ORDER BY time DESC LIMIT 1",
        (symbol, sig_type)
    )
    row = cursor.fetchone()
    return row and time.time() - row[0] < cooldown

def save_signal(symbol, sig_type):
    cursor.execute(
        "INSERT INTO signals VALUES (?, ?, ?)",
        (symbol, sig_type, int(time.time()))
    )
    conn.commit()

# =========================
# 📊 DATA
# =========================
def get_ohlcv(symbol, tf="15m", limit=100):
    try:
        bars = exchange.fetch_ohlcv(COINS[symbol], tf, limit=limit)
        df = pd.DataFrame(bars, columns=["t","o","h","l","c","v"])
        return df
    except:
        return None

# =========================
# 📈 INDICATORS
# =========================
def ema(series, period):
    return series.ewm(span=period, adjust=False).mean()

def rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# =========================
# 🔔 SEND MESSAGE
# =========================
def send(app, text):
    async def _send():
        await app.bot.send_message(chat_id=CHAT_ID, text=text)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(_send())
    loop.close()

# =========================
# ⚡ EMA CROSS
# =========================
ema_state = {}

def ema_checker(app):
    while True:
        try:
            for s in COINS:

                df = get_ohlcv(s, "15m")
                if df is None or len(df) < 60:
                    continue

                close = df["c"]

                ema20 = ema(close, 20).iloc[-1]
                ema50 = ema(close, 50).iloc[-1]

                state = ema20 > ema50
                old = ema_state.get(s)

                if old is not None:

                    if state and not old:
                        if not already_sent(s, "golden"):
                            send(app, f"🟢 GOLDEN CROSS ⚡ {s}")
                            save_signal(s, "golden")

                    elif not state and old:
                        if not already_sent(s, "death"):
                            send(app, f"🔴 DEATH CROSS ⚡ {s}")
                            save_signal(s, "death")

                ema_state[s] = state

            time.sleep(60)

        except:
            time.sleep(10)

# =========================
# 📉 RSI DIVERGENCE (SIMPLE)
# =========================
div_cache = {}

def divergence_checker(app):
    while True:
        try:
            for s in COINS:

                df = get_ohlcv(s, "4h")
                if df is None or len(df) < 60:
                    continue

                close = df["c"]
                r = rsi(close)

                price = close.iloc[-1]
                rsi_v = r.iloc[-1]

                old = div_cache.get(s)

                if old:

                    move = abs(price - old["price"]) / old["price"]

                    if move < 0.002:
                        continue

                    if price > old["price"] and rsi_v < old["rsi"]:
                        if not already_sent(s, "bear_div"):
                            send(app, f"🔴 BEAR DIV 📉 {s}")
                            save_signal(s, "bear_div")

                    if price < old["price"] and rsi_v > old["rsi"]:
                        if not already_sent(s, "bull_div"):
                            send(app, f"🟢 BULL DIV 📈 {s}")
                            save_signal(s, "bull_div")

                div_cache[s] = {"price": price, "rsi": rsi_v}

            time.sleep(180)

        except:
            time.sleep(10)

# =========================
# 🎛 UI
# =========================
main_keyboard = ReplyKeyboardMarkup(
    [
        ["🚀 START"],
        ["⚡ EMA CROSS", "📉 DIVERGENCE"],
        ["📊 STATUS"]
    ],
    resize_keyboard=True
)

# =========================
# 🚀 START
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 BTC BOT ONLINE ⚡",
        reply_markup=main_keyboard
    )

# =========================
# 💬 HANDLER
# =========================
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    t = update.message.text

    if t == "🚀 START":
        await start(update, context)

# =========================
# ▶ RUN
# =========================
app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

threading.Thread(target=ema_checker, args=(app,), daemon=True).start()
threading.Thread(target=divergence_checker, args=(app,), daemon=True).start()

print("BOT RUNNING 🚀")

app.run_polling(drop_pending_updates=True)
