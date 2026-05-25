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
# TOKEN
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
    "ZECUSDT": ("BINANCE", "ZECUSDT"),
    "HYPEUSDT": ("MEXC", "HYPEUSDT"),
    "UBUSDT": ("MEXC", "UBUSDT"),
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
# STORAGE
# =====================================

user_targets = {}
rsi_targets = {}

MAX_ALERTS = 3

# =====================================
# MENU
# =====================================

main_keyboard = ReplyKeyboardMarkup(
    [
        ["🚀 شروع ربات"],
        ["💰 قیمت لحظه‌ای"],
        ["📊 سیگنال"],
        ["📈 اندیکاتور RSI"],
        ["🎯 تارگت RSI"],
        ["📦 حجم بازار"],
        ["💧 نقدینگی"],
        ["🎯 تنظیم تارگت"]
    ],
    resize_keyboard=True
)

# =====================================
# ANALYSIS
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
# PRICE
# =====================================

def get_price(symbol):

    analysis = get_analysis(symbol)

    if analysis:

        return analysis.indicators.get("close")

    return None

# =====================================
# ALERT
# =====================================

def send_multi_alert(app, text):

    try:

        for i in range(MAX_ALERTS):

            asyncio.run(
                app.bot.send_message(
                    chat_id=CHAT_ID,
                    text=f"{text}\n\n🔔 Alert {i+1}"
                )
            )

            time.sleep(2)

    except Exception as e:

        print("ALERT ERROR:", e)

# =====================================
# MENUS
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
        "✅ تارگت RSI\n"
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
# TARGET
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
            "❌ مثال:\n/target BTCUSDT 120000"
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

                    send_multi_alert(
                        app,
                        f"🎯 TARGET HIT\n\n"
                        f"{symbol}\n"
                        f"💰 {current_price}"
                    )

                    del user_targets[symbol]

            time.sleep(30)

        except Exception as e:

            print("TARGET ERROR:", e)

            time.sleep(30)

# =====================================
# RSI TARGET CHECKER
# =====================================

def rsi_target_checker(app):

    while True:

        try:

            for key, target in list(rsi_targets.items()):

                parts = key.split("_")

                symbol = parts[0]

                tf = parts[1]

                analysis = get_analysis(
                    symbol,
                    TIMEFRAMES[tf]
                )

                if analysis is None:
                    continue

                rsi = analysis.indicators.get("RSI")

                if rsi is None:
                    continue

                if rsi >= target:

                    send_multi_alert(
                        app,
                        f"🎯 RSI TARGET HIT\n\n"
                        f"{symbol}\n"
                        f"⏰ {tf}\n"
                        f"📈 RSI: {rsi:.2f}"
                    )

                    del rsi_targets[key]

            time.sleep(20)

        except Exception as e:

            print("RSI TARGET ERROR:", e)

            time.sleep(20)

# =====================================
# BUTTONS
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
                "❌ موردی یافت نشد"
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
            f"⏰ تایم فریم {symbol}",
            reply_markup=timeframe_menu("signal", symbol)
        )

    elif data.startswith("signal_"):

        parts = data.split("_")

        symbol = parts[1]

        tf = parts[2]

        analysis = get_analysis(
            symbol,
            TIMEFRAMES[tf]
        )

        if analysis is None:

            await query.edit_message_text(
                "❌ خطا"
            )

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
            f"⏰ تایم فریم RSI {symbol}",
            reply_markup=timeframe_menu("rsi", symbol)
        )

    elif data.startswith("rsi_"):

        parts = data.split("_")

        symbol = parts[1]

        tf = parts[2]

        analysis = get_analysis(
            symbol,
            TIMEFRAMES[tf]
        )

        if analysis is None:

            await query.edit_message_text(
                "❌ خطا"
            )

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

    # RSI TARGET

    elif data.startswith("rsitarget_") and "_15m" not in data and "_4h" not in data and "_1d" not in data:

        symbol = data.replace("rsitarget_", "")

        await query.edit_message_text(
            f"⏰ تایم فریم RSI Target {symbol}",
            reply_markup=timeframe_menu("rsitarget", symbol)
        )

    elif data.startswith("rsitarget_"):

        parts = data.split("_")

        symbol = parts[1]

        tf = parts[2]

        context.user_data["rsi_symbol"] = symbol

        context.user_data["rsi_tf"] = tf

        await query.message.reply_text(
            "📌 عدد RSI را ارسال کن\nمثال:\n70"
        )

# =====================================
# SAVE RSI TARGET
# =====================================

async def save_rsi_target(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:

        value = float(update.message.text)

        symbol = context.user_data.get("rsi_symbol")

        tf = context.user_data.get("rsi_tf")

        if not symbol or not tf:
            return

        key = f"{symbol}_{tf}"

        rsi_targets[key] = value

        await update.message.reply_text(
            f"✅ تارگت RSI ثبت شد\n\n"
            f"{symbol}\n"
            f"⏰ {tf}\n"
            f"📈 {value}"
        )

        context.user_data.clear()

    except:

        pass

# =====================================
# TEXT HANDLER
# =====================================

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if "rsi_symbol" in context.user_data:

        await save_rsi_target(update, context)

        return

    text = update.message.text

    if text == "🚀 شروع ربات":

        await start(update, context)

    elif text == "💰 قیمت لحظه‌ای":

        await update.message.reply_text(
            "💰 انتخاب ارز:",
            reply_markup=coin_menu("price")
        )

    elif text == "📊 سیگنال":

        await update.message.reply_text(
            "📊 انتخاب ارز:",
            reply_markup=coin_menu("signal")
        )

    elif text == "📈 اندیکاتور RSI":

        await update.message.reply_text(
            "📈 انتخاب ارز:",
            reply_markup=coin_menu("rsi")
        )

    elif text == "🎯 تارگت RSI":

        await update.message.reply_text(
            "🎯 انتخاب ارز:",
            reply_markup=coin_menu("rsitarget")
        )

    elif text == "🎯 تنظیم تارگت":

        await update.message.reply_text(
            "مثال:\n/target BTCUSDT 120000"
        )

    elif text == "📦 حجم بازار":

        await update.message.reply_text(
            "📦 بخش حجم بازار بزودی حرفه‌ای‌تر می‌شود"
        )

    elif text == "💧 نقدینگی":

        await update.message.reply_text(
            "💧 بخش نقدینگی بزودی حرفه‌ای‌تر می‌شود"
        )

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

threading.Thread(
    target=rsi_target_checker,
    args=(app,),
    daemon=True
).start()

print("BOT RUNNING 🚀")

asyncio.set_event_loop(asyncio.new_event_loop())

app.run_polling(
    drop_pending_updates=True
)
