import json
import os

from scanner import (
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

            "vip": True,

            "rsi": True,

            "ema": True,

            "divergence": True,

            "price_target": True,

            "rsi_target": True
        }

        save_users(users)


def toggle_alert(
    chat_id,
    alert_name
):

    users = load_users()

    chat_id = str(chat_id)

    if chat_id not in users:

        return False

    current = users[chat_id][alert_name]

    users[chat_id][alert_name] = not current

    save_users(users)

    return users[chat_id][alert_name]


def get_user_settings(
    chat_id
):

    users = load_users()

    chat_id = str(chat_id)

    return users.get(
        chat_id,
        {}
    )


async def send_vip_alerts(
    context
):

    users = load_users()

    signals = get_vip_signals()

    if not signals:

        return

    top_signals = signals[:5]

    for signal in top_signals:

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

واگرایی:
{signal['divergence']}

امتیاز:
{signal['score']}

سیگنال:
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

                except:

                    pass
