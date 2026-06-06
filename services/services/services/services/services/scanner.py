import time

from config import COINS, SCANNER_INTERVAL
from services.signal_engine import generate_signal
from services.market import get_price
from services.targets import set_target, check_targets


last_signal = {}


def run_scanner(bot, chat_id):

    print("Scanner started...")

    while True:

        try:

            for coin in COINS.keys():

                # =========================
                # SIGNAL ENGINE (VIP + NORMAL)
                # =========================
                signal, rsi, reasons, score, direction, is_vip = generate_signal(coin)

                price = get_price(coin)

                # =========================
                # TARGET CHECK
                # =========================
                result = check_targets(coin, price)

                if result:
                    bot.send_message(
                        chat_id,
                        f"""
🚨 TARGET HIT

💎 {coin}
📊 {result}
"""
                    )

                # =========================
                # ONLY STRONG SIGNALS
                # =========================
                if score >= 4 or score <= -4:

                    # جلوگیری از تکرار پیام
                    if last_signal.get(coin) == signal:
                        continue

                    last_signal[coin] = signal

                    tp = "-"
                    sl = "-"

                    # =========================
                    # SET TARGET (ONLY IF DIRECTION EXISTS)
                    # =========================
                    if direction and price:

                        tp, sl = set_target(coin, direction, price)

                    # =========================
                    # MESSAGE TYPE
                    # =========================
                    tag = "🔥 VIP SIGNAL" if is_vip else "📊 SIGNAL"

                    msg = f"""
{tag}

💎 Coin: {coin}
💰 Price: {price}

📊 RSI: {rsi}
📡 Signal: {signal}

🎯 TP: {tp}
🛑 SL: {sl}

🧠 Reasons:
{', '.join(reasons)}
"""

                    bot.send_message(chat_id, msg)

        except Exception as e:
            print("Scanner error:", e)

        time.sleep(SCANNER_INTERVAL)
