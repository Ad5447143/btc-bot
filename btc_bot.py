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
import threading
import time

# =====================================
# TOKEN + CHAT ID
# =====================================

BOT_TOKEN = "8995261480:AAFi0H9lQyC8i3od5SjeyStlhwtdpWpCmj0"

CHAT_ID = "369031827"

# =====================================
# COINS
# =====================================

COINS = {
    "BTCUSDT": ("BINANCE", "BTCUSDT"),
    "ETHUSDT": ("BINANCE", "ETHUSDT"),
    "BNBUSDT": ("BINANCE", "BNBUSDT"),
    "SOLUSDT": ("BINANCE", "SOLUSDT"),
    "XRPUSDT": ("BINANCE", "XRPUSDT"),
    "DOGEUSDT": ("BINANCE", "DOGEUSDT"),
    "ADAUSDT": ("BINANCE", "ADAUSDT"),
    "TRXUSDT": ("BINANCE", "TRXUSDT"),
    "HYPEUSDT": ("BINANCE", "HYPEUSDT"),
    "ZECUSDT": ("BINANCE", "ZECUSDT"),
    "XAUUSD": ("OANDA", "XAUUSD"),
    "XAGUSD": ("OANDA", "XAGUSD"),
    "USDT": ("CRYPTOCAP", "USDT")
}

# =====================================
# TIMEFRAMES
# =====================================

TIMEFRAMES = {
    "15m": Interval.INTERVAL_15_MINUTES,
    "4h": Interval.INTERVAL_4_HOURS,
    "1d": Interval.INTERVAL_1_DAY
}

# =====================================
# TARGETS
# =====================================

user_targets = {}

# =====================================
# MAIN MENU
# =====================================

main_keyboard = ReplyKeyboardMarkup(
    [
        ["🚀 شروع ربات"],
        ["💰 قیمت لحظه‌ای"],
        ["📊 سیگنال"],
        ["📈 اندیکاتور RSI"],
        ["📦 حجم بازار"],
        ["💧 نقدینگی"],
        ["🎯 تنظیم تارگت"]
    ],
    resize_keyboard=True
)

# =====================================
# GET ANALYSIS
# =====================================

def get_analysis(symbol, interval=Interval.INTERVAL_15_MINUTES):

    try:

        exchange, tv_symbol = COINS[symbol]

        screener = "crypto"

        if exchange == "OANDA":
            screener = "forex"

        handler = TA_Handler(
            symbol=tv_symbol,
            screener=screener,
            exchange=exchange,
            interval=interval
        )

        return handler.get_analysis()

    except Exception as e:

        print("ERROR:", e)
        return None

# =====================================
# GET PRICE
# =====================================

def get_price(symbol):

    analysis = get_analysis(symbol)

    if analysis:
        return analysis.indicators.get("close")

    return None

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
                callback_data=f"{prefix}_{symbol}"
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
                "15m",
                callback_data=f"{prefix}_{symbol}_15m"
            ),
            InlineKeyboardButton(
                "4H",
                callback_data=f"{prefix}_{symbol}_4h"
            )
        ],
        [
            InlineKeyboardButton(
                "1D",
                callback_data=f"{prefix}_{symbol}_1d"
            )
        ]
    ])

# =====================================
# START
# =====================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = (
        "🤖 ربات حرفه‌ای کریپتو فعال شد\n\n"
        "✅ قیمت لحظه‌ای\n"
        "✅ سیگنال حرفه‌ای\n"
        "✅ RSI\n"
        "✅ حجم خرید و فروش\n"
        "✅ نقدینگی\n"
        "✅ تارگت قیمت\n"
        "✅ طلا و نقره\n"
        "✅ تایم فریم 15m / 4h / 1d"
    )

    await update.message.reply_text(
        text,
        reply_markup=main_keyboard
    )

# =====================================
# MENUS
# =====================================

async def price_menu(update, context):

    await update.message.reply_text(
        "💰 ارز مورد نظر را انتخاب کن:",
        reply_markup=coin_menu("price")
    )

async def signal_menu(update, context):

    await update.message.reply_text(
        "📊 ارز مورد نظر:",
        reply_markup=coin_menu("signal")
    )

async def rsi_menu(update, context):

    await update.message.reply_text(
        "📈 ارز مورد نظر:",
        reply_markup=coin_menu("rsi")
    )

async def volume_menu(update, context):

    await update.message.reply_text(
        "📦 ارز مورد نظر:",
        reply_markup=coin_menu("volume")
    )

async def liquidity_menu(update, context):

    await update.message.reply_text(
        "💧 ارز مورد نظر:",
        reply_markup=coin_menu("liq")
    )

async def target_menu(update, context):

    await update.message.reply_text(
        "🎯 مثال:\n/target BTCUSDT 120000"
    )

# =====================================
# TARGET COMMAND
# =====================================

async def target(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:

        symbol = context.args[0].upper()
        price = float(context.args[1])

        user_targets[symbol] = price

        await update.message.reply_text(
            f"✅ تارگت ثبت شد\n\n"
            f"{symbol} → {price}"
        )

    except:

        await update.message.reply_text(
            "❌ مثال صحیح:\n"
            "/target BTCUSDT 120000"
        )

# =====================================
# TARGET CHECKER
# =====================================

def target_checker(app):

    while True:

        try:

            for symbol, target_price in list(user_targets.items()):

                current_price = get_price(symbol)

                if current_price is None:
                    continue

                if current_price >= target_price:

                    text = (
                        f"🎯 TARGET HIT\n\n"
                        f"{symbol}\n"
                        f"💰 Price: {current_price}"
                    )

                    asyncio.run(
                        app.bot.send_message(
                            chat_id=CHAT_ID,
                            text=text
                        )
                    )

                    del user_targets[symbol]

            time.sleep(30)

        except Exception as e:

            print("TARGET ERROR:", e)
            time.sleep(30)

# =====================================
# BUTTON HANDLER
# =====================================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    data = query.data

    # PRICE

    if data.startswith("price_"):

        symbol = data.replace("price_", "")

        price = get_price(symbol)

        if price is None:

            await query.edit_message_text(
                "❌ دریافت قیمت ناموفق بود"
            )

            return

        await query.edit_message_text(
            f"💰 {symbol}\n\n"
            f"📌 قیمت لحظه‌ای:\n{price}"
        )

    # SIGNAL

    elif data.startswith("signal_") and "_15m" not in data and "_4h" not in data and "_1d" not in data:

        symbol = data.replace("signal_", "")

        await query.edit_message_text(
            f"⏰ تایم فریم {symbol}:",
            reply_markup=timeframe_menu("signal", symbol)
        )

    elif data.startswith("signal_"):

        parts = data.split("_")

        symbol = parts[1]
        tf = parts[2]

        analysis = get_analysis(symbol, TIMEFRAMES[tf])

        if analysis is None:

            await query.edit_message_text("❌ خطا")

            return

        summary = analysis.summary

        text = (
            f"📊 {symbol}\n\n"
            f"⏰ تایم فریم: {tf}\n\n"
            f"📡 وضعیت: {summary['RECOMMENDATION']}\n\n"
            f"🟢 BUY: {summary['BUY']}\n"
            f"🔴 SELL: {summary['SELL']}\n"
            f"⚪ NEUTRAL: {summary['NEUTRAL']}"
        )

        await query.edit_message_text(text)

    # RSI

    elif data.startswith("rsi_") and "_15m" not in data and "_4h" not in data and "_1d" not in data:

        symbol = data.replace("rsi_", "")

        await query.edit_message_text(
            f"⏰ تایم فریم RSI {symbol}:",
            reply_markup=timeframe_menu("rsi", symbol)
        )

    elif data.startswith("rsi_"):

        parts = data.split("_")

        symbol = parts[1]
        tf = parts[2]

        analysis = get_analysis(symbol, TIMEFRAMES[tf])

        if analysis is None:

            await query.edit_message_text("❌ خطا")

            return

        rsi = analysis.indicators["RSI"]

        status = "⚪ خنثی"

        if rsi >= 70:
            status = "🔴 اشباع خرید"

        elif rsi <= 30:
            status = "🟢 اشباع فروش"

        elif 45 <= rsi <= 55:
            status = "🟡 نزدیک RSI 50"

        text = (
            f"📈 RSI {symbol}\n\n"
            f"⏰ تایم فریم: {tf}\n\n"
            f"📌 RSI: {rsi:.2f}\n\n"
            f"📡 وضعیت:\n{status}"
        )

        await query.edit_message_text(text)

# =====================================
# TEXT HANDLER
# =====================================

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text

    if text == "🚀 شروع ربات":

        await start(update, context)

    elif text == "💰 قیمت لحظه‌ای":

        await price_menu(update, context)

    elif text == "📊 سیگنال":

        await signal_menu(update, context)

    elif text == "📈 اندیکاتور RSI":

        await rsi_menu(update, context)

    elif text == "📦 حجم بازار":

        await volume_menu(update, context)

    elif text == "💧 نقدینگی":

        await liquidity_menu(update, context)

    elif text == "🎯 تنظیم تارگت":

        await target_menu(update, context)

# =====================================
# RUN
# =====================================

app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))

app.add_handler(CommandHandler("target", target))

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        text_handler
    )
)

app.add_handler(CallbackQueryHandler(button_handler))

threading.Thread(
    target=target_checker,
    args=(app,),
    daemon=True
).start()

print("BOT RUNNING 🚀")

asyncio.set_event_loop(asyncio.new_event_loop())

app.run_polling(
    drop_pending_updates=True
)
