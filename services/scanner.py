from services.market import (
    get_rsi,
    get_ema_cross,
    get_divergence
)

from config import COINS


async def send_auto_alerts(context):

    users = load_users()

    for chat_id, settings in users.items():

        symbol = settings.get(
            "symbol",
            "BTCUSDT"
        )

        timeframe = settings.get(
            "timeframe",
            "1h"
        )

        try:

            # RSI ALERT

            if settings.get(
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

            # EMA CROSS ALERT

            if settings.get(
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

            # DIVERGENCE ALERT

            if settings.get(
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
