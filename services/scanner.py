import time

from config import COINS
from services.signal_engine import generate_signal

last_signals = {}

def run_scanner():

    print("🚀 اسکنر فعال شد")

    while True:

        try:

            for coin in COINS.keys():

                signal, score, reasons = generate_signal(coin)

                if signal == "❌ NO SIGNAL":
                    continue

                old_signal = last_signals.get(coin)

                if old_signal == signal:
                    continue

                last_signals[coin] = signal

                print(
                    f"""
━━━━━━━━━━━━━━

💎 {coin}

{signal}

🎯 امتیاز:
{score}

📋 دلایل:

{chr(10).join(reasons)}

━━━━━━━━━━━━━━
"""
                )

        except Exception as e:

            print(
                f"خطای اسکنر: {e}"
            )

        time.sleep(300)
