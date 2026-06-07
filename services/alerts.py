LAST_PRICE_ALERTS = {}
LAST_RSI_ALERTS = {}

PRICE_TARGETS = {
    "BTCUSDT": 120000,
    "ETHUSDT": 5000,
    "SOLUSDT": 300
}

RSI_TARGET = 70
import json
import os

from services.scanner import (
    get_vip_signals
)

from services.market import (
    get_rsi,
    get_ema_cross,
    get_divergence
)

USERS_FILE = "storage/users.json"


def load_users():

    if not os.path.exists(
        USERS_FILE
    ):
        return {}

    try:

        with open(
            USERS_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    except:

        return {}


def save_users(data):

    with open(
        USERS_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=4
        )


def register_user(chat_id):

    users = load_users()

    chat_id = str(chat_id)

    if chat_id not in users:

        users[chat_id] = {

            "symbol": "BTCUSDT",

            "timeframe": "1h",

            "vip": True,

            "rsi": True,

            "ema": True,

            "divergence": True,

            "price_target": True,

            "rsi_target": True
        }

        save_users(users)


def get_user_settings(
    chat_id
):

    users = load_users()

    return users.get(
        str(chat_id),
        {}
    )


def set_symbol(
    chat_id,
    symbol
):

    users = load_users()

    chat_id = str(chat_id)

    if chat_id not in users:

        register_user(
            chat_id
        )

        users = load_users()

    users[chat_id]["symbol"] = symbol

    save_users(users)


def set_timeframe(
    chat_id,
    timeframe
):

    users = load_users()

    chat_id = str(chat_id)

    if chat_id not in users:

        register_user(
            chat_id
        )

        users = load_users()

    users[chat_id]["timeframe"] = timeframe

    save_users(users)


def toggle_alert(
    chat_id,
    alert_name
):

    users = load_users()

    chat_id = str(chat_id)

    if chat_id not in users:

        return False

    current = users[chat_id].get(
        alert_name,
        True
    )

    users[chat_id][alert_name] = (
        not current
    )

    save_users(users)

    return users[chat_id][alert_name]


async def send_vip_alerts(
    context
):

    users = load_users()

    signals = get_vip_signals()

    if not signals:

        return

    signals = signals[:5]

    for signal in signals:

        text = f"""
🔥 سیگنال VIP

━━━━━━━━━━━━━━

🪙 نماد:
{signal['symbol']}

⏱ تایم فریم:
{signal['timeframe']}

💰 قیمت:
{signal['price']}

📈 RSI:
{signal['rsi']}

⚡ روند EMA:
{signal['ema_signal']}

⚡ کراس EMA:
{signal['ema_cross']}

📉 واگرایی:
{signal['divergence']}

🎯 امتیاز:
{signal['score']}

🚀 نتیجه:
{signal['signal']}
"""

        for chat_id in users:

            if users[chat_id].get(
                "vip",
                True
            ):

                try:

                    await context.bot.send_message(
                        chat_id=int(chat_id),
                        text=text
                    )

                except Exception as e:

                    print(
                        "VIP ALERT ERROR:",
                        e
                    )


async def send_auto_alerts(
    context
):

    users = load_users()

    for chat_id in users:

        try:

            symbol = users[
                chat_id
            ].get(
                "symbol",
                "BTCUSDT"
            )

            timeframe = users[
                chat_id
            ].get(
                "timeframe",
                "1h"
            )

            # RSI

            if users[
                chat_id
            ].get(
                "rsi",
                True
            ):

                rsi = get_rsi(
                    symbol,
                    timeframe
                )

                if rsi:

                    if rsi >= 70:

                        await context.bot.send_message(
                            chat_id=int(chat_id),
                            text=f"""
🔥 هشدار RSI

نماد:
{symbol}

تایم فریم:
{timeframe}

RSI:
{rsi}

وضعیت:
اشباع خرید
"""
                        )

                    elif rsi <= 30:

                        await context.bot.send_message(
                            chat_id=int(chat_id),
                            text=f"""
🟢 هشدار RSI

نماد:
{symbol}

تایم فریم:
{timeframe}

RSI:
{rsi}

وضعیت:
اشباع فروش
"""
                        )

            # EMA CROSS

            if users[
                chat_id
            ].get(
                "ema",
                True
            ):

                cross = get_ema_cross(
                    symbol,
                    timeframe
                )

                if cross:

                    await context.bot.send_message(
                        chat_id=int(chat_id),
                        text=f"""
⚡ هشدار کراس EMA

نماد:
{symbol}

تایم فریم:
{timeframe}

نتیجه:
{cross}
"""
                    )

            # DIVERGENCE

            if users[
                chat_id
            ].get(
                "divergence",
                True
            ):

                divergence = get_divergence(
                    symbol,
                    timeframe
                )

                if divergence:

                    await context.bot.send_message(
                        chat_id=int(chat_id),
                        text=f"""
📉 هشدار واگرایی

نماد:
{symbol}

تایم فریم:
{timeframe}

نتیجه:
{divergence}
"""
                    )

        except Exception as e:

            print(
                "AUTO ALERT ERROR:",
                e
            )
