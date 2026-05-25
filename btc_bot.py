from telegram import (
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Update
)

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

from tradingview_ta import TA_Handler, Interval
import asyncio

# =========================
# تنظیمات
# =========================

BOT_TOKEN = "8995261480:AAFi0H9lQyC8i3od5SjeyStlhwtdpWpCmj0"

# =========================
# ارزها
# =========================

COINS = {
    "BTCUSDT": "BINANCE:BTCUSDT",
    "ETHUSDT": "BINANCE:ETHUSDT",
    "BNBUSDT": "BINANCE:BNBUSDT",
    "SOLUSDT": "BINANCE:SOLUSDT",
    "XRPUSDT": "BINANCE:XRPUSDT",
    "DOGEUSDT": "BINANCE:DOGEUSDT",
    "ADAUSDT": "BINANCE:ADAUSDT",
    "USDT": "CRYPTOCAP:USDT"
}

# =========================
# تایم‌فریم‌ها
# =========================

TIMEFRAMES = {
    "1m": Interval.INTERVAL_1_MINUTE,
    "5m": Interval.INTERVAL_5_MINUTES,
    "4h": Interval.INTERVAL_4_HOURS
}

# =========================
# منوی اصلی
# =========================

main_keyboard = ReplyKeyboardMarkup(
    [
        ["💰 قیمت ارزها"],
        ["📊 سیگنال"],
        ["🎯 تارگت"]
    ],
    resize_keyboard=True
)

# =========================
# منوی ارزها
# =========================

def coin_menu(mode):

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🟡 BTC",
                callback_data=f"{mode}_BTCUSDT"
            ),

            InlineKeyboardButton(
                "🔵 ETH",
                callback_data=f"{mode}_ETHUSDT"
            )
        ],

        [
            InlineKeyboardButton(
                "🟠 BNB",
                callback_data=f"{mode}_BNBUSDT"
            ),

            InlineKeyboardButton(
                "🟢 SOL",
                callback_data=f"{mode}_SOLUSDT"
            )
        ],

        [
            InlineKeyboardButton(
                "🔴 XRP",
                callback_data=f"{mode}_XRPUSDT"
            ),

            InlineKeyboardButton(
                "⚫ DOGE",
                callback_data=f"{mode}_DOGEUSDT"
            )
        ],

        [
            InlineKeyboardButton(
                "🔷 ADA",
                callback_data=f"{mode}_ADAUSDT"
            ),

            InlineKeyboardButton(
                "⚪ USDT",
                callback_data=f"{mode}_USDT"
            )
        ]
    ])

# =========================
# منوی تایم‌فریم
# =========================

def timeframe_menu(symbol):

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "1 Minute",
                callback_data=f"time_1m_{symbol}"
            ),

            InlineKeyboardButton(
                "5 Minute",
                callback_data=f"time_5m_{symbol}"
            )
        ],

        [
            InlineKeyboardButton(
                "4 Hour",
                callback_data=f"time_4h_{symbol}"
            )
        ]
    ])

# =========================
# گرفتن تحلیل
# =========================

def get_analysis(symbol, timeframe):

    try:

        tv_symbol = COINS[symbol]

        exchange, real_symbol = tv_symbol.split(":")

        handler = TA_Handler(
            symbol=real_symbol,
            screener="crypto",
            exchange=exchange,
            interval=TIMEFRAMES[timeframe]
        )

        analysis = handler.get_analysis()

        indicators = analysis.indicators

        price = indicators["close"]

        rsi = indicators.get("RSI", 0)

        ema25 = indicators.get("EMA25", 0)
        ema50 = indicators.get("EMA50", 0)
        ema100 = indicators.get("EMA100", 0)
        ema200 = indicators.get("EMA200", 0)

        recommendation = analysis.summary["RECOMMENDATION"]

        signal = "⚪ NEUTRAL"

        if recommendation == "BUY":
            signal = "🚀 BUY"

        elif recommendation == "SELL":
            signal = "📉 SELL"

        return {
            "price": price,
            "rsi": rsi,
            "ema25": ema25,
            "ema50": ema50,
            "ema100": ema100,
            "ema200": ema200,
            "signal": signal
        }

    except Exception as e:

        print("ERROR:", e)

        return None

# =========================
# start
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "🤖 ربات کریپتو فعال شد 🚀",
        reply_markup=main_keyboard
    )

# =========================
# قیمت
# =========================

async def prices(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "💰 انتخاب ارز 👇",
        reply_markup=coin_menu("price")
    )

# =========================
# سیگنال
# =========================

async def signals(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "📊 انتخاب ارز برای سیگنال 👇",
        reply_markup=coin_menu("signal")
    )

# =========================
# تارگت
# =========================

async def target(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "مثال:\n/target BTCUSDT 80000"
    )

# =========================
# دکمه‌ها
# =========================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    data = query.data

    # =====================
    # PRICE
    # =====================

    if data.startswith("price_"):

        symbol = data.replace("price_", "")

        result = get_analysis(symbol, "1m")

        if result:

            text = (
                f"💰 {symbol}\n\n"
                f"Price: {result['price']}$"
            )

            await query.edit_message_text(text)

    # =====================
    # SIGNAL
    # =====================

    elif data.startswith("signal_"):

        symbol = data.replace("signal_", "")

        await query.edit_message_text(
            f"⏱ تایم‌فریم {symbol}",
            reply_markup=timeframe_menu(symbol)
        )

    # =====================
    # TIMEFRAME
    # =====================

    elif data.startswith("time_"):

        parts = data.split("_")

        timeframe = parts[1]
        symbol = parts[2]

        result = get_analysis(symbol, timeframe)

        if result:

            text = (
                f"📊 {symbol}\n"
                f"⏱ TimeFrame: {timeframe}\n\n"

                f"💰 Price: {result['price']}$\n\n"

                f"📈 RSI: {result['rsi']:.2f}\n\n"

                f"EMA 25: {result['ema25']:.2f}\n"
                f"EMA 50: {result['ema50']:.2f}\n"
                f"EMA 100: {result['ema100']:.2f}\n"
                f"EMA 200: {result['ema200']:.2f}\n\n"

                f"📡 Signal: {result['signal']}"
            )

            await query.edit_message_text(text)

        else:

            await query.edit_message_text(
                "❌ خطا در دریافت دیتا"
            )

# =========================
# متن‌ها
# =========================

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text

    if text == "💰 قیمت ارزها":

        await prices(update, context)

    elif text == "📊 سیگنال":

        await signals(update, context)

    elif text == "🎯 تارگت":

        await target(update, context)

# =========================
# اجرای ربات
# =========================

app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_text
    )
)

app.add_handler(
    CallbackQueryHandler(button_handler)
)

# =========================
# MAIN
# =========================

async def main():

    print("BOT RUNNING 🚀")

    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    while True:
        await asyncio.sleep(60)

# =========================
# RUN
# =========================

if __name__ == "__main__":

    asyncio.run(main())
