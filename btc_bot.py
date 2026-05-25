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

# =====================================
# BOT TOKEN
# =====================================

BOT_TOKEN = "8995261480:AAFi0H9lQyC8i3od5SjeyStlhwtdpWpCmj0"

# =====================================
# SYMBOLS
# =====================================

COINS = {
    "BTCUSDT": "BINANCE",
    "ETHUSDT": "BINANCE",
    "BNBUSDT": "BINANCE",
    "SOLUSDT": "BINANCE",
    "XRPUSDT": "BINANCE",
    "DOGEUSDT": "BINANCE",
    "ADAUSDT": "BINANCE",
    "TRXUSDT": "BINANCE",
    "HYPEUSDT": "BINANCE",
    "UBUSDT": "BINANCE",
    "XAUUSD": "OANDA",
    "XAGUSD": "OANDA",
    "USDT": "BINANCE"
}

# =====================================
# TIMEFRAMES
# =====================================

TIMEFRAMES = {
    "5m": Interval.INTERVAL_5_MINUTES,
    "15m": Interval.INTERVAL_15_MINUTES,
    "4h": Interval.INTERVAL_4_HOURS,
    "1d": Interval.INTERVAL_1_DAY
}

# =====================================
# MAIN MENU
# =====================================

main_keyboard = ReplyKeyboardMarkup(
    [
        ["💰 قیمت"],
        ["📊 سیگنال"],
        ["📈 اندیکاتور"],
        ["📦 حجم"],
        ["💧 نقدینگی"]
    ],
    resize_keyboard=True
)

# =====================================
# START
# =====================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "🤖 ربات حرفه‌ای کریپتو فعال شد\n\n"
        "✅ قیمت لحظه‌ای\n"
        "✅ سیگنال\n"
        "✅ RSI\n"
        "✅ حجم بازار\n"
        "✅ نقدینگی\n"
        "✅ تایم فریم‌های مختلف",
        reply_markup=main_keyboard
    )

# =====================================
# COIN MENU
# =====================================

def coin_menu(prefix):

    buttons = []

    row = []

    for symbol in COINS.keys():

        row.append(
            InlineKeyboardButton(
                symbol,
                callback_data=f"{prefix}_coin_{symbol}"
            )
        )

        if len(row) == 2:
            buttons.append(row)
            row = []

    if row:
        buttons.append(row)

    return InlineKeyboardMarkup(buttons)

# =====================================
# TIMEFRAME MENU
# =====================================

def timeframe_menu(prefix, symbol):

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "5m",
                callback_data=f"{prefix}_tf_{symbol}_5m"
            ),
            InlineKeyboardButton(
                "15m",
                callback_data=f"{prefix}_tf_{symbol}_15m"
            )
        ],
        [
            InlineKeyboardButton(
                "4H",
                callback_data=f"{prefix}_tf_{symbol}_4h"
            ),
            InlineKeyboardButton(
                "1D",
                callback_data=f"{prefix}_tf_{symbol}_1d"
            )
        ]
    ])

# =====================================
# GET ANALYSIS
# =====================================

def get_analysis(symbol, interval):

    exchange = COINS[symbol]

    screener = "crypto"

    if exchange == "OANDA":
        screener = "forex"

    handler = TA_Handler(
        symbol=symbol,
        screener=screener,
        exchange=exchange,
        interval=interval
    )

    return handler.get_analysis()

# =====================================
# PRICE MENU
# =====================================

async def prices(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "💰 ارز مورد نظر را انتخاب کن:",
        reply_markup=coin_menu("price")
    )

# =====================================
# SIGNAL MENU
# =====================================

async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "📊 ارز مورد نظر برای سیگنال:",
        reply_markup=coin_menu("signal")
    )

# =====================================
# RSI MENU
# =====================================

async def indicator(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "📈 ارز مورد نظر برای RSI:",
        reply_markup=coin_menu("rsi")
    )

# =====================================
# VOLUME MENU
# =====================================

async def volume(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "📦 ارز مورد نظر برای حجم:",
        reply_markup=coin_menu("volume")
    )

# =====================================
# LIQUIDITY MENU
# =====================================

async def liquidity(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "💧 ارز مورد نظر برای نقدینگی:",
        reply_markup=coin_menu("liq")
    )

# =====================================
# BUTTON HANDLER
# =====================================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    data = query.data

    # =====================================
    # PRICE
    # =====================================

    if data.startswith("price_coin_"):

        symbol = data.replace("price_coin_", "")

        await query.edit_message_text(
            f"⏰ تایم فریم {symbol} را انتخاب کن:",
            reply_markup=timeframe_menu("price", symbol)
        )

    elif data.startswith("price_tf_"):

        parts = data.split("_")

        symbol = parts[2]
        tf = parts[3]

        analysis = get_analysis(
            symbol,
            TIMEFRAMES[tf]
        )

        price = analysis.indicators["close"]

        text = (
            f"💰 {symbol}\n\n"
            f"⏰ تایم فریم: {tf}\n"
            f"📌 قیمت: {price}"
        )

        await query.edit_message_text(text)

    # =====================================
    # SIGNAL
    # =====================================

    elif data.startswith("signal_coin_"):

        symbol = data.replace("signal_coin_", "")

        await query.edit_message_text(
            f"⏰ تایم فریم {symbol}:",
            reply_markup=timeframe_menu("signal", symbol)
        )

    elif data.startswith("signal_tf_"):

        parts = data.split("_")

        symbol = parts[2]
        tf = parts[3]

        analysis = get_analysis(
            symbol,
            TIMEFRAMES[tf]
        )

        recommendation = analysis.summary["RECOMMENDATION"]

        buy = analysis.summary["BUY"]
        sell = analysis.summary["SELL"]
        neutral = analysis.summary["NEUTRAL"]

        text = (
            f"📊 سیگنال {symbol}\n\n"
            f"⏰ تایم فریم: {tf}\n\n"
            f"📡 وضعیت: {recommendation}\n\n"
            f"🟢 BUY: {buy}\n"
            f"🔴 SELL: {sell}\n"
            f"⚪ NEUTRAL: {neutral}"
        )

        await query.edit_message_text(text)

    # =====================================
    # RSI
    # =====================================

    elif data.startswith("rsi_coin_"):

        symbol = data.replace("rsi_coin_", "")

        await query.edit_message_text(
            f"⏰ تایم فریم RSI {symbol}:",
            reply_markup=timeframe_menu("rsi", symbol)
        )

    elif data.startswith("rsi_tf_"):

        parts = data.split("_")

        symbol = parts[2]
        tf = parts[3]

        analysis = get_analysis(
            symbol,
            TIMEFRAMES[tf]
        )

        rsi = analysis.indicators["RSI"]

        status = "⚪ خنثی"

        if rsi >= 70:
            status = "🔴 نزدیک اشباع خرید"

        elif rsi <= 30:
            status = "🟢 نزدیک اشباع فروش"

        elif 45 <= rsi <= 55:
            status = "🟡 نزدیک RSI 50"

        text = (
            f"📈 RSI {symbol}\n\n"
            f"⏰ تایم فریم: {tf}\n"
            f"📌 RSI: {rsi:.2f}\n\n"
            f"📡 وضعیت: {status}"
        )

        await query.edit_message_text(text)

    # =====================================
    # VOLUME
    # =====================================

    elif data.startswith("volume_coin_"):

        symbol = data.replace("volume_coin_", "")

        await query.edit_message_text(
            f"⏰ تایم فریم حجم {symbol}:",
            reply_markup=timeframe_menu("volume", symbol)
        )

    elif data.startswith("volume_tf_"):

        parts = data.split("_")

        symbol = parts[2]
        tf = parts[3]

        analysis = get_analysis(
            symbol,
            TIMEFRAMES[tf]
        )

        buy = analysis.summary["BUY"]
        sell = analysis.summary["SELL"]

        status = "⚪ متعادل"

        if buy > sell:
            status = "🟢 فشار خرید"

        elif sell > buy:
            status = "🔴 فشار فروش"

        text = (
            f"📦 حجم {symbol}\n\n"
            f"⏰ تایم فریم: {tf}\n\n"
            f"🟢 BUY: {buy}\n"
            f"🔴 SELL: {sell}\n\n"
            f"📡 وضعیت: {status}"
        )

        await query.edit_message_text(text)

    # =====================================
    # LIQUIDITY
    # =====================================

    elif data.startswith("liq_coin_"):

        symbol = data.replace("liq_coin_", "")

        await query.edit_message_text(
            f"⏰ تایم فریم نقدینگی {symbol}:",
            reply_markup=timeframe_menu("liq", symbol)
        )

    elif data.startswith("liq_tf_"):

        parts = data.split("_")

        symbol = parts[2]
        tf = parts[3]

        analysis = get_analysis(
            symbol,
            TIMEFRAMES[tf]
        )

        high = analysis.indicators["high"]
        low = analysis.indicators["low"]
        close = analysis.indicators["close"]

        text = (
            f"💧 نقدینگی {symbol}\n\n"
            f"⏰ تایم فریم: {tf}\n\n"
            f"🔼 ناحیه نقدینگی بالا:\n"
            f"{high}\n\n"
            f"🔽 ناحیه نقدینگی پایین:\n"
            f"{low}\n\n"
            f"💰 قیمت فعلی:\n"
            f"{close}"
        )

        await query.edit_message_text(text)

# =====================================
# TEXT HANDLER
# =====================================

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text

    if text == "💰 قیمت":
        await prices(update, context)

    elif text == "📊 سیگنال":
        await signal(update, context)

    elif text == "📈 اندیکاتور":
        await indicator(update, context)

    elif text == "📦 حجم":
        await volume(update, context)

    elif text == "💧 نقدینگی":
        await liquidity(update, context)

# =====================================
# RUN BOT
# =====================================

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

print("BOT RUNNING 🚀")

asyncio.set_event_loop(asyncio.new_event_loop())

app.run_polling(drop_pending_updates=True)
