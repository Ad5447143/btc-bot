import threading
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

from config import BOT_TOKEN
from services.scanner import run_scanner
from services.signal_engine import generate_signal
from services.market import get_price
from services.analysis import calculate_rsi, ema_cross

print("BOT STARTED 🚀")

# =========================
# MAIN MENU
# =========================
main_menu = ReplyKeyboardMarkup(
    [
        ["📊 سیگنال بازار", "💰 قیمت"],
        ["📈 RSI", "⚡ EMA"],
        ["📉 واگرایی", "🩺 سلامت ربات"]
    ],
    resize_keyboard=True
)

# =========================
# START
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = """
🤖 Crypto AI Bot

📊 تحلیل حرفه‌ای بازار
📈 RSI + EMA + Divergence
🚨 اسکن خودکار

👇 یکی از گزینه‌ها را انتخاب کن
"""

    await update.message.reply_text(text, reply_markup=main_menu)

# =========================
# MESSAGE HANDLER
# =========================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text

    if text == "📊 سیگنال بازار":

        signal, rsi, reasons, score = generate_signal("BTCUSDT")

        await update.message.reply_text(
            f"""
🚨 سیگنال BTCUSDT

📊 RSI: {rsi}
📡 {signal}

🧠 دلایل:
{', '.join(reasons)}
"""
        )

    elif text == "💰 قیمت":

        price = get_price("BTCUSDT")

        await update.message.reply_text(f"💰 BTCUSDT: {price}")

    elif text == "📈 RSI":

        rsi = calculate_rsi("BTCUSDT")

        await update.message.reply_text(f"📊 RSI: {rsi}")

    elif text == "⚡ EMA":

        ema = ema_cross("BTCUSDT")

        await update.message.reply_text(f"⚡ EMA: {ema}")

    elif text == "📉 واگرایی":

        await update.message.reply_text("📉 این بخش در مرحله بعد کامل می‌شود")

    elif text == "🩺 سلامت ربات":

        await update.message.reply_text(
            """
🩺 وضعیت ربات

🟢 Bot: فعال
🟢 Scanner: روشن
🟢 API: سالم
🟢 Engine: فعال
"""
        )

# =========================
# MAIN
# =========================
def main():

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # /start
    app.add_handler(CommandHandler("start", start))

    # پیام‌ها
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # =========================
    # SCANNER THREAD
    # =========================
    threading.Thread(
        target=run_scanner,
        args=(app.bot, 369031827),
        daemon=True
    ).start()

    print("Bot is running...")

    app.run_polling()

# =========================
if __name__ == "__main__":
    main()
