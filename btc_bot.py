import threading
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from config import BOT_TOKEN
from services.scanner import run_scanner

print("BOT STARTED 🚀")

# =========================
# START COMMAND
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 ربات فعال شد و آماده کار است")

# =========================
# MAIN FUNCTION
# =========================
def main():

    # ساخت اپلیکیشن
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # هندلر /start
    app.add_handler(CommandHandler("start", start))

    # =========================
    # اجرای اسکنر در پس‌زمینه
    # =========================
    scanner_thread = threading.Thread(
        target=run_scanner,
        args=(app.bot, 369031827),
        daemon=True
    )
    scanner_thread.start()

    print("Bot is running...")

    # اجرای ربات
    app.run_polling()

# =========================
if __name__ == "__main__":
    main()
