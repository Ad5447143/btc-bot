import time
from config import COINS, SCANNER_INTERVAL
from services.signal_engine import generate_signal

last_signal = {}

def run_scanner(bot, chat_id):

    print("Scanner started...")

    while True:

        try:

            for coin in COINS.keys():

                signal, rsi, reasons, score = generate_signal(coin, "15m")

                # فقط سیگنال قوی
                if score >= 3 or score <= -3:

                    # جلوگیری از تکرار پیام
                    if last_signal.get(coin) == signal:
                        continue

                    last_signal[coin] = signal

                    msg = f"""
🚨 سیگنال قوی

💎 {coin}
📊 RSI: {rsi}

📡 {signal}

🧠 دلایل:
{', '.join(reasons)}
"""

                    bot.send_message(chat_id, msg)

        except Exception as e:
            print("Scanner error:", e)

        time.sleep(SCANNER_INTERVAL)
