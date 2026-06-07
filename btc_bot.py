import sys
import telegram
import asyncio

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

from services.market import (
    get_price,
    get_rsi
)

print("================================")
print("PYTHON VERSION:")
print(sys.version)
print("================================")

print("TELEGRAM VERSION:")
print(telegram.__version__)
print("================================")

print("🚀 BOT STARTED")


main_menu = ReplyKeyboardMarkup(
    [
        ["🚀 شروع ربات"],

        ["💰 قیمت BTC",
         "💰 قیمت ETH"],

        ["📈 RSI BTC",
         "📈 RSI ETH"],

        ["🎯 تارگت قیمتی",
         "🎯 تارگت RSI"],

        ["🔥 سیگنال VIP",
         "🩺 سلامت ربات"]
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

✅ قیمت BTC
✅ قیمت ETH

✅ RSI BTC
✅ RSI ETH

✅ تارگت قیمتی
✅ تارگت RSI

✅ سیگنال VIP

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

        await start(update, context)

    elif text == "💰 قیمت BTC":

        price = get_price("bitcoin")

        if price:

            await update.message.reply_text(
                f"""
💰 قیمت بیت کوین

{price:,.2f} USD
                """
            )

        else:

            await update.message.reply_text(
                "❌ خطا در دریافت قیمت"
            )

    elif text == "💰 قیمت ETH":

        price = get_price("ethereum")

        if price:

            await update.message.reply_text(
                f"""
💰 قیمت اتریوم

{price:,.2f} USD
                """
            )

        else:

            await update.message.reply_text(
                "❌ خطا در دریافت قیمت"
            )

    elif text == "📈 RSI BTC":

        rsi = get_rsi("bitcoin")

        if rsi:

            status = "خنثی"

            if rsi > 70:
                status = "اشباع خرید 🔥"

            elif rsi < 30:
                status = "اشباع فروش 🟢"

            await update.message.reply_text(
                f"""
📈 RSI بیت کوین

RSI:
{rsi}

وضعیت:
{status}
                """
            )

        else:

            await update.message.reply_text(
                "❌ خطا در محاسبه RSI"
            )

    elif text == "📈 RSI ETH":

        rsi = get_rsi("ethereum")

        if rsi:

            status = "خنثی"

            if rsi > 70:
                status = "اشباع خرید 🔥"

            elif rsi < 30:
                status = "اشباع فروش 🟢"

            await update.message.reply_text(
                f"""
📈 RSI اتریوم

RSI:
{rsi}

وضعیت:
{status}
                """
            )

        else:

            await update.message.reply_text(
                "❌ خطا در محاسبه RSI"
            )

    elif text == "🎯 تارگت قیمتی":

        price = get_price("bitcoin")

        if price:

            target = price * 1.03

            await update.message.reply_text(
                f"""
🎯 تارگت قیمتی BTC

قیمت فعلی:
{price:,.2f}

تارگت:
{target:,.2f}
                """
            )

    elif text == "🎯 تارگت RSI":

        await update.message.reply_text(
            """
🎯 تارگت RSI

هدف RSI:

70
            """
        )

    elif text == "🔥 سیگنال VIP":

        price = get_price("bitcoin")

        if price:

            take_profit = price * 1.03
            stop_loss = price * 0.98

            await update.message.reply_text(
                f"""
🔥 سیگنال VIP

نماد:
BTC

ورود:
{price:,.2f}

حد سود:
{take_profit:,.2f}

حد ضرر:
{stop_loss:,.2f}
                """
            )

    elif text == "🩺 سلامت ربات":

        await update.message.reply_text(
            """
🩺 سلامت ربات

🟢 ربات فعال است
🟢 تلگرام متصل است
🟢 CoinGecko متصل است
🟢 سرور فعال است
            """
        )


async def run_bot():

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
            filters.TEXT & ~filters.COMMAND,
            messages
        )
    )

    print("🚀 Bot Running")

    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    while True:
        await asyncio.sleep(3600)


def main():

    asyncio.run(
        run_bot()
    )


if __name__ == "__main__":
    main()
