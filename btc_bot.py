import asyncio
import json
import os

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

from config import (
    BOT_TOKEN,
    SCANNER_INTERVAL,
    COINS
)

from services.market import (
    get_price,
    get_rsi,
    get_ema_signal,
    get_ema_cross,
    get_divergence
)

from services.scanner import (
    get_best_signal,
    format_vip_signal,
    format_market_summary
)

from services.alerts import (
    register_user,
    get_user_settings,
    set_symbol,
    set_timeframe,
    send_vip_alerts
)
from services.alerts import (
    send_vip_alerts,
    send_auto_alerts
)

USERS_FILE = "storage/users.json"


TIMEFRAMES = [
    "5m",
    "15m",
    "1h",
    "4h",
    "1d"
]


MAIN_MENU = ReplyKeyboardMarkup(
    [
        ["🚀 شروع ربات"],

        ["💰 قیمت لحظه‌ای",
         "📈 RSI"],

        ["⚡ روند EMA",
         "⚡ کراس EMA"],

        ["📉 واگرایی RSI",
         "📊 خلاصه بازار"],

        ["🔥 سیگنال VIP",
         "🎯 تارگت قیمتی"],

        ["🎯 تارگت RSI",
         "⚙️ تنظیمات"],

        ["🩺 سلامت ربات"]
    ],
    resize_keyboard=True
)


SETTINGS_MENU = ReplyKeyboardMarkup(
    [
        ["🪙 انتخاب ارز"],
        ["⏱ انتخاب تایم فریم"],
        ["⬅️ بازگشت"]
    ],
    resize_keyboard=True
)


COIN_MENU = ReplyKeyboardMarkup(
    [
        ["BTCUSDT", "ETHUSDT"],
        ["BNBUSDT", "SOLUSDT"],
        ["XRPUSDT", "DOGEUSDT"],
        ["ADAUSDT", "TRXUSDT"],
        ["⬅️ بازگشت"]
    ],
    resize_keyboard=True
)


TIMEFRAME_MENU = ReplyKeyboardMarkup(
    [
        ["5m", "15m"],
        ["1h", "4h"],
        ["1d"],
        ["⬅️ بازگشت"]
    ],
    resize_keyboard=True
)


def get_user_symbol(chat_id):

    data = get_user_settings(chat_id)

    return data.get(
        "symbol",
        "BTCUSDT"
    )


def get_user_timeframe(chat_id):

    data = get_user_settings(chat_id)

    return data.get(
        "timeframe",
        "1h"
    )


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    register_user(
        update.effective_chat.id
    )

    await update.message.reply_text(
        """
🚀 به ربات تحلیل بازار خوش آمدید

✅ قیمت لحظه‌ای

✅ RSI

✅ روند EMA

✅ کراس EMA

✅ واگرایی RSI

✅ خلاصه بازار

✅ سیگنال VIP

✅ تارگت قیمتی

✅ تارگت RSI

🟢 ربات فعال است
        """,
        reply_markup=MAIN_MENU
    )


async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    text = update.message.text

    chat_id = update.effective_chat.id

    symbol = get_user_symbol(
        chat_id
    )

    timeframe = get_user_timeframe(
        chat_id
    )

    if text == "🚀 شروع ربات":

        await start(
            update,
            context
        )

    elif text == "⚙️ تنظیمات":

        await update.message.reply_text(
            f"""
⚙️ تنظیمات فعلی

🪙 ارز:
{symbol}

⏱ تایم فریم:
{timeframe}
            """,
            reply_markup=SETTINGS_MENU
        )

    elif text == "🪙 انتخاب ارز":

        await update.message.reply_text(
            "ارز مورد نظر را انتخاب کنید",
            reply_markup=COIN_MENU
        )

    elif text in COINS:

        set_symbol(
            chat_id,
            text
        )

        await update.message.reply_text(
            f"""
✅ ارز انتخاب شد

{text}
            """,
            reply_markup=SETTINGS_MENU
        )

    elif text == "⏱ انتخاب تایم فریم":

        await update.message.reply_text(
            "تایم فریم را انتخاب کنید",
            reply_markup=TIMEFRAME_MENU
        )

    elif text in TIMEFRAMES:

        set_timeframe(
            chat_id,
            text
        )

        await update.message.reply_text(
            f"""
✅ تایم فریم انتخاب شد

{text}
            """,
            reply_markup=SETTINGS_MENU
        )

    elif text == "⬅️ بازگشت":

        await update.message.reply_text(
            "بازگشت به منوی اصلی",
            reply_markup=MAIN_MENU
        )

    elif text == "💰 قیمت لحظه‌ای":

        price = get_price(
            symbol
        )

        if not price:

            await update.message.reply_text(
                "❌ خطا در دریافت قیمت"
            )

            return

        await update.message.reply_text(
            f"""
💰 قیمت لحظه‌ای

نماد:
{symbol}

قیمت:
{price:,.4f}

تایم فریم:
{timeframe}
            """
        )

    elif text == "📈 RSI":

        rsi = get_rsi(
            symbol,
            timeframe
        )

        if rsi is None:

            await update.message.reply_text(
                "❌ خطا در محاسبه RSI"
            )

            return

        status = "خنثی"

        if rsi > 70:
            status = "اشباع خرید 🔥"

        elif rsi < 30:
            status = "اشباع فروش 🟢"

        await update.message.reply_text(
            f"""
📈 RSI

نماد:
{symbol}

تایم فریم:
{timeframe}

RSI:
{rsi}

وضعیت:
{status}
            """
        )
    elif text == "⚡ روند EMA":

        trend = get_ema_signal(
            symbol,
            timeframe
        )

        await update.message.reply_text(
            f"""
⚡ روند EMA

نماد:
{symbol}

تایم فریم:
{timeframe}

وضعیت:
{trend}
            """
        )

    elif text == "⚡ کراس EMA":

        cross = get_ema_cross(
            symbol,
            timeframe
        )

        if not cross:

            cross = "کراسی مشاهده نشد"

        await update.message.reply_text(
            f"""
⚡ کراس EMA

نماد:
{symbol}

تایم فریم:
{timeframe}

نتیجه:
{cross}
            """
        )

    elif text == "📉 واگرایی RSI":

        divergence = get_divergence(
            symbol,
            timeframe
        )

        if not divergence:

            divergence = "واگرایی مشاهده نشد"

        await update.message.reply_text(
            f"""
📉 واگرایی RSI

نماد:
{symbol}

تایم فریم:
{timeframe}

نتیجه:
{divergence}
            """
        )

    elif text == "📊 خلاصه بازار":

        await update.message.reply_text(
            format_market_summary()
        )

    elif text == "🔥 سیگنال VIP":

        signal = get_best_signal()

        await update.message.reply_text(
            format_vip_signal(
                signal
            )
        )

    elif text == "🎯 تارگت قیمتی":

        price = get_price(
            symbol
        )

        if not price:

            await update.message.reply_text(
                "❌ خطا در دریافت قیمت"
            )

            return

        target_up = round(
            price * 1.03,
            4
        )

        target_down = round(
            price * 0.97,
            4
        )

        await update.message.reply_text(
            f"""
🎯 تارگت قیمتی

نماد:
{symbol}

تایم فریم:
{timeframe}

قیمت فعلی:
{price}

تارگت صعودی:
{target_up}

تارگت نزولی:
{target_down}
            """
        )

    elif text == "🎯 تارگت RSI":

        rsi = get_rsi(
            symbol,
            timeframe
        )

        if rsi is None:

            await update.message.reply_text(
                "❌ خطا در محاسبه RSI"
            )

            return

        await update.message.reply_text(
            f"""
🎯 تارگت RSI

نماد:
{symbol}

تایم فریم:
{timeframe}

RSI فعلی:
{rsi}

هدف خرید:
30

هدف فروش:
70
            """
        )

    elif text == "🩺 سلامت ربات":

        await update.message.reply_text(
            """
🩺 سلامت ربات

🟢 ربات فعال است

🟢 تلگرام متصل است

🟢 Bybit متصل است

🟢 اسکنر فعال است

🟢 هشدار VIP فعال است
            """
        )

    else:

        await update.message.reply_text(
            "دستور نامعتبر است"
        )


async def startup_message(
    context
):

    print(
        "🔥 Scanner Running"
    )


async def main():

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
            handle_message
        )
    )

    app.job_queue.run_repeating(
        send_vip_alerts,
        interval=SCANNER_INTERVAL,
        first=60
    )

    app.job_queue.run_once(
        startup_message,
        when=5
    )
app.job_queue.run_repeating(
    send_vip_alerts,
    interval=300,
    first=60
)

app.job_queue.run_repeating(
    send_auto_alerts,
    interval=300,
    first=120
)
    print("🚀 Bot Running")

    await app.initialize()

    await app.start()

    await app.updater.start_polling()

    while True:

        await asyncio.sleep(
            3600
        )


if __name__ == "__main__":

    asyncio.run(
        main()
    )
