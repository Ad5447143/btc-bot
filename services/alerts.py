import json
import os

from services.scanner import (
    get_vip_signals
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

    os.makedirs(
        "storage",
        exist_ok=True
    )

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


def get_user_settings(chat_id):

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

        register_user(chat_id)

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

        register_user(chat_id)

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

    users[chat_id][alert_name] = not current

    save_users(users)

    return users[chat_id][alert_name]


async def send_vip_alerts(context):

    users = load_users()

    signals = get_vip_signals()

    if not signals:

        return

    signals = signals[:5]

    for signal in signals:

        text = f"""
🔥 سیگنال VIP

نماد:
{signal['symbol']}

تایم فریم:
{signal['timeframe']}

قیمت:
{signal['price']}

RSI:
{signal['rsi']}

EMA:
{signal['ema_signal']}

کراس EMA:
{signal['ema_cross']}

واگرایی:
{signal['divergence']}

امتیاز:
{signal['score']}

سیگنال:
{signal['signal']}
"""

        for chat_id, settings in users.items():

            if not settings.get(
                "vip",
                True
            ):
                continue

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
