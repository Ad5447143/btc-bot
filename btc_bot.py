```python id="4g4e2l"
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton
)

from telegram.ext import (
    Application,
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
    api_health
)

from services.analysis import (
    calculate_rsi,
    ema_cross,
    market_pressure,
    detect_divergence,
    multi_timeframe_analysis
)

from services.scanner import (
    market_scanner
)

from services.targets import (
    add_target,
    check_targets,
    add_rsi_target,
    check_rsi_targets
)

from services.security import (
    register_user,
    users_text,
    anti_flood
)

# =========================================
# USER STATE
# =========================================

user_state = {}

# =========================================
# MAIN MENU
# =========================================

main_menu = ReplyKeyboardMarkup(
    [
        ["🚀 شروع ربات"],

        ["💰 قیمت لحظه‌ای",
         "📊 تحلیل بازار"],

        ["📈 RSI",
         "⚡ EMA کراس"],

        ["📉 واگرایی RSI",
         "📦 فشار بازار"],

        ["🧠 تحلیل مولتی تایم"],

        ["🎯 تارگت گذاری",
         "🎯 RSI تارگت"],

        ["🛡 امنیت"],

        ["🩺 سلامت ربات"]
    ],
    resize_keyboard=True
)

# =========================================
# COIN KEYBOARD
# =========================================

def coin_keyboard():

    rows = []

    row = []

    for i, coin in enumerate(
        COINS.keys(),
        start=1
    ):

        row.append(
            KeyboardButton(
                f"💎 {coin}"
            )
        )

        if i % 3 == 0:

            rows.append(row)

            row = []

    if row:

        rows.append(row)

    return ReplyKeyboardMarkup(
        rows,
        resize_keyboard=True
    )

# =========================================
# TIMEFRAME KEYBOARD
# =========================================

def timeframe_keyboard():

    return ReplyKeyboardMarkup(
        [
            ["⏰ 5m", "⏰ 15m"],
            ["⏰ 4H", "⏰ 1D"]
        ],
        resize_keyboard=True
    )

# =========================================
# START
# =========================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    text = """
🚀 Crypto AI Bot PRO

━━━━━━━━━━━━━━

✅ RSI Scanner
✅ EMA Scanner
✅ Divergence Scanner
✅ Multi Timeframe
✅ Real Targets
✅ RSI Targets
✅ Auto Alerts
✅ Security System

━━━━━━━━━━━━━━

🟢 ربات فعال است
"""

    await update.message.reply_text(
        text,
        reply_markup=main_menu
    )

# =========================================
# HEALTH
# =========================================

async def health(update):

    api = api_health()

    api_status = (
        "🟢 سالم"
        if api
        else
        "🔴 مشکل"
    )

    text = f"""
🩺 سلامت ربات

━━━━━━━━━━━━━━

CoinGecko:
{api_status}

KuCoin:
{api_status}

RSI Engine:
🟢 سالم

EMA Engine:
🟢 سالم

Scanner:
🟢 فعال

Targets:
🟢 فعال

RSI Targets:
🟢 فعال

Security:
🟢 فعال
"""

    await update.message.reply_text(
        text
    )

# =========================================
# MESSAGE HANDLER
# =========================================

async def messages(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    text = update.message.text

    user_id = update.effective_user.id

    # =====================================
    # SECURITY
    # =====================================

    await register_user(
        update,
        context
    )

    anti_flood(user_id)

    # =====================================
    # START
    # =====================================

    if text == "🚀 شروع ربات":

        await start(
            update,
            context
        )

    # =====================================
    # SECURITY PANEL
    # =====================================

    elif text == "🛡 امنیت":

        if user_id != 369031827:

            await update.message.reply_text(
                "❌ دسترسی غیر مجاز"
            )

            return

        users = users_text()

        await update.message.reply_text(
            users
        )

    # =====================================
    # HEALTH
    # =====================================

    elif text == "🩺 سلامت ربات":

        await health(update)

    # =====================================
    # PRICE
    # =====================================

    elif text == "💰 قیمت لحظه‌ای":

        user_state[user_id] = {
            "action": "price"
        }

        await update.message.reply_text(
            "💎 ارز را انتخاب کن:",
            reply_markup=coin_keyboard()
        )

    # =====================================
    # RSI
    # =====================================

    elif text == "📈 RSI":

        user_state[user_id] = {
            "action": "rsi"
        }

        await update.message.reply_text(
            "💎 ارز را انتخاب کن:",
            reply_markup=coin_keyboard()
        )

    # =====================================
    # EMA
    # =====================================

    elif text == "⚡ EMA کراس":

        user_state[user_id] = {
            "action": "ema"
        }

        await update.message.reply_text(
            "💎 ارز را انتخاب کن:",
            reply_markup=coin_keyboard()
        )

    # =====================================
    # PRESSURE
    # =====================================

    elif text == "📦 فشار بازار":

        user_state[user_id] = {
            "action": "pressure"
        }

        await update.message.reply_text(
            "💎 ارز را انتخاب کن:",
            reply_markup=coin_keyboard()
        )

    # =====================================
    # DIVERGENCE
    # =====================================

    elif text == "📉 واگرایی RSI":

        user_state[user_id] = {
            "action": "div"
        }

        await update.message.reply_text(
            "💎 ارز را انتخاب کن:",
            reply_markup=coin_keyboard()
        )

    # =====================================
    # MULTI TF
    # =====================================

    elif text == "🧠 تحلیل مولتی تایم":

        user_state[user_id] = {
            "action": "multi"
        }

        await update.message.reply_text(
            "💎 ارز را انتخاب کن:",
            reply_markup=coin_keyboard()
        )

    # =====================================
    # ANALYSIS
    # =====================================

    elif text == "📊 تحلیل بازار":

        user_state[user_id] = {
            "action": "analysis"
        }

        await update.message.reply_text(
            "💎 ارز را انتخاب کن:",
            reply_markup=coin_keyboard()
        )

    # =====================================
    # TARGET
    # =====================================

    elif text == "🎯 تارگت گذاری":

        user_state[user_id] = {
            "action": "target"
        }

        await update.message.reply_text(
            "💎 ارز را انتخاب کن:",
            reply_markup=coin_keyboard()
        )

    # =====================================
    # RSI TARGET
    # =====================================

    elif text == "🎯 RSI تارگت":

        user_state[user_id] = {
            "action": "rsi_target"
        }

        await update.message.reply_text(
            "💎 ارز را انتخاب کن:",
            reply_markup=coin_keyboard()
        )

    # =====================================
    # COIN SELECT
    # =====================================

    elif text.startswith("💎"):

        coin = text.replace(
            "💎 ",
            ""
        )

        if coin not in COINS:

            return

        user_state[user_id]["coin"] = coin

        action = user_state[user_id]["action"]

        # =================================
        # MULTI TIMEFRAME
        # =================================

        if action == "multi":

            result = multi_timeframe_analysis(
                coin
            )

            await update.message.reply_text(
                result
            )

            return

        await update.message.reply_text(
            "⏰ تایم فریم را انتخاب کن:",
            reply_markup=timeframe_keyboard()
        )

    # =====================================
    # TIMEFRAME
    # =====================================

    elif text.startswith("⏰"):

        timeframe = text.replace(
            "⏰ ",
            ""
        )

        action = user_state[user_id]["action"]

        coin = user_state[user_id]["coin"]

        # =================================
        # TARGET
        # =================================

        if action == "target":

            user_state[user_id]["timeframe"] = timeframe

            user_state[user_id]["step"] = "target1"

            await update.message.reply_text(
                "🎯 Target 1 را وارد کن:"
            )

            return

        # =================================
        # RSI TARGET
        # =================================

        if action == "rsi_target":

            user_state[user_id]["timeframe"] = timeframe

            await update.message.reply_text(
                "🎯 مقدار RSI را وارد کن:"
            )

            return

        # =================================
        # PRICE
        # =================================

        if action == "price":

            price = get_price(coin)

            await update.message.reply_text(
                f"""
💰 قیمت لحظه‌ای

💎 {coin}

💵 {price} $
"""
            )

        # =================================
        # RSI
        # =================================

        elif action == "rsi":

            rsi = calculate_rsi(
                coin,
                timeframe
            )

            await update.message.reply_text(
                f"""
📈 RSI

💎 {coin}
⏰ {timeframe}

📊 RSI:
{rsi}
"""
            )

        # =================================
        # EMA
        # =================================

        elif action == "ema":

            ema = ema_cross(
                coin,
                timeframe
            )

            await update.message.reply_text(
                f"""
⚡ EMA کراس

💎 {coin}
⏰ {timeframe}

{ema}
"""
            )

        # =================================
        # PRESSURE
        # =================================

        elif action == "pressure":

            pressure = market_pressure(
                coin,
                timeframe
            )

            await update.message.reply_text(
                f"""
📦 فشار بازار

💎 {coin}
⏰ {timeframe}

{pressure}
"""
            )

        # =================================
        # DIVERGENCE
        # =================================

        elif action == "div":

            div = detect_divergence(
                coin,
                timeframe
            )

            await update.message.reply_text(
                f"""
📉 واگرایی RSI

💎 {coin}
⏰ {timeframe}

{div}
"""
            )

        # =================================
        # ANALYSIS
        # =================================

        elif action == "analysis":

            rsi = calculate_rsi(
                coin,
                timeframe
            )

            ema = ema_cross(
                coin,
                timeframe
            )

            pressure = market_pressure(
                coin,
                timeframe
            )

            await update.message.reply_text(
                f"""
📊 تحلیل بازار

💎 {coin}
⏰ {timeframe}

━━━━━━━━━━━━━━

📈 RSI:
{rsi}

⚡ EMA:
{ema}

📦 فشار بازار:
{pressure}
"""
            )

    # =====================================
    # TARGET INPUTS
    # =====================================

    elif user_id in user_state:

        # =================================
        # RSI TARGET
        # =================================

        if user_state[user_id].get(
            "action"
        ) == "rsi_target":

            state = user_state[user_id]

            try:

                value = float(text)

            except:

                await update.message.reply_text(
                    "❌ عدد معتبر وارد کن"
                )

                return

            add_rsi_target(
                state["coin"],
                state["timeframe"],
                value
            )

            await update.message.reply_text(
                f"""
✅ RSI Target ذخیره شد

💎 {state['coin']}
⏰ {state['timeframe']}

🎯 RSI:
{value}
""",
                reply_markup=main_menu
            )

            del user_state[user_id]

            return

        # =================================
        # NORMAL TARGETS
        # =================================

        if user_state[user_id].get(
            "action"
        ) == "target":

            state = user_state[user_id]

            try:

                value = float(text)

            except:

                await update.message.reply_text(
                    "❌ عدد معتبر وارد کن"
                )

                return

            # =============================
            # TARGET 1
            # =============================

            if state["step"] == "target1":

                state["target1"] = value

                state["step"] = "target2"

                await update.message.reply_text(
                    "🎯 Target 2 را وارد کن:"
                )

                return

            # =============================
            # TARGET 2
            # =============================

            elif state["step"] == "target2":

                state["target2"] = value

                state["step"] = "target3"

                await update.message.reply_text(
                    "🎯 Target 3 را وارد کن:"
                )

                return

            # =============================
            # TARGET 3
            # =============================

            elif state["step"] == "target3":

                state["target3"] = value

                add_target(
                    state["coin"],
                    state["timeframe"],
                    state["target1"],
                    state["target2"],
                    value
                )

                await update.message.reply_text(
                    f"""
✅ تارگت ذخیره شد

💎 {state['coin']}
⏰ {state['timeframe']}

🎯 T1 → {state['target1']}
🎯 T2 → {state['target2']}
🎯 T3 → {value}
""",
                    reply_markup=main_menu
                )

                del user_state[user_id]

# =========================================
# MAIN
# =========================================

def main():

    print("BOT STARTED 🚀")

    app = Application.builder().token(
        BOT_TOKEN
    ).build()

    # =====================================
    # HANDLERS
    # =====================================

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

    # =====================================
    # MARKET SCANNER
    # =====================================

    app.job_queue.run_repeating(
        market_scanner,
        interval=SCANNER_INTERVAL,
        first=15
    )

    # =====================================
    # TARGET SCANNER
    # =====================================

    app.job_queue.run_repeating(
        check_targets,
        interval=60,
        first=20
    )

    # =====================================
    # RSI TARGET SCANNER
    # =====================================

    app.job_queue.run_repeating(
        check_rsi_targets,
        interval=60,
        first=25
    )

    print("BOT RUNNING 🚀")

    app.run_polling()

# =========================================
# RUN
# =========================================

if __name__ == "__main__":

    main()
```
