from telegram import (
    Update,
    ReplyKeyboardMarkup
)

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

        ["💰 قیمت لحظه‌ای",
         "📈 RSI"],

        ["⚡ کراس EMA",
         "📉 واگرایی RSI"],

        ["📦 فشار بازار",
         "🔥 سیگنال VIP"],

        ["🎯 تارگت قیمتی",
         "🎯 تارگت RSI"],

        ["🩺 سلامت ربات"]
    ],
    resize_keyboard=True
)


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        """
🚀 به ربات تحلیل بازار خوش آمدید

━━━━━━━━━━━━━━

✅ قیمت لحظه‌ای
✅ RSI
✅ کراس EMA
✅ واگرایی RSI
✅ سیگنال VIP
✅ تارگت قیمتی
✅ تارگت RSI

━━━━━━━━━━━━━━

🟢 ربات فعال است
        """,
        reply_markup=main_menu
    )


async def messages(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    text = update.message.text

    if text == "🚀 شروع ربات":

        await start(
            update,
            context
        )

    elif text == "🩺 سلامت ربات":

        await update.message.reply_text(
            """
🩺 سلامت ربات

🟢 ربات فعال است
🟢 اسکنر فعال است
🟢 موتور تحلیل فعال است
            """
        )

    elif text == "💰 قیمت لحظه‌ای":

        await update.message.reply_text(
            "💰 بخش قیمت لحظه‌ای در حال تکمیل است."
        )

    elif text == "📈 RSI":

        await update.message.reply_text(
            "📈 بخش RSI در حال تکمیل است."
        )

    elif text == "⚡ کراس EMA":

        await update.message.reply_text(
            "⚡ بخش EMA در حال تکمیل است."
        )

    elif text == "📉 واگرایی RSI":

        await update.message.reply_text(
            "📉 بخش واگرایی در حال تکمیل است."
        )

    elif text == "📦 فشار بازار":

        await update.message.reply_text(
            "📦 بخش فشار بازار در حال تکمیل است."
        )

    elif text == "🔥 سیگنال VIP":

        await update.message.reply_text(
            "🔥 بخش سیگنال VIP در حال تکمیل است."
        )

    elif text == "🎯 تارگت قیمتی":

        await update.message.reply_text(
            "🎯 بخش تارگت قیمتی در حال تکمیل است."
        )

    elif text == "🎯 تارگت RSI":

        await update.message.reply_text(
            "🎯 بخش تارگت RSI در حال تکمیل است."
        )


def main():

    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .build()
    )

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

    print("🚀 Bot Running")

    app.run_polling()


if __name__ == "__main__":
    main()
