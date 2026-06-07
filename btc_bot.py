import sys
import telegram

print("================================")
print("PYTHON VERSION:")
print(sys.version)
print("================================")

print("TELEGRAM VERSION:")
print(telegram.__version__)
print("================================")

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

from config import BOT_TOKEN

print("🚀 BOT STARTED")


main_menu = ReplyKeyboardMarkup(
    [
        ["🚀 شروع ربات"],
        ["💰 قیمت لحظه‌ای", "📈 RSI"],
        ["⚡ کراس EMA", "📉 واگرایی RSI"],
        ["📦 فشار بازار", "🔥 سیگنال VIP"],
        ["🎯 تارگت قیمتی", "🎯 تارگت RSI"],
        ["🩺 سلامت ربات"]
    ],
    resize_keyboard=True
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 ربات فعال است",
        reply_markup=main_menu
    )


async def messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"دکمه انتخاب شده:\n{update.message.text}"
    )


def main():

    app = ApplicationBuilder().token(
        BOT_TOKEN
    ).build()

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            messages
        )
    )

    print("🚀 Bot Running")

    app.run_polling(
        drop_pending_updates=True
    )


if __name__ == "__main__":
    main()
