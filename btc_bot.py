from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from config import BOT_TOKEN

from services.scanner import run_scanner

import threading

print("BOT STARTED 🚀")

# =========================
# START COMMAND
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 ربات فعال شد و آماده است")

# =========================
# MAIN
# =========================
def main():

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # /start command
    app.add_handler(CommandHandler("start", start))

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
