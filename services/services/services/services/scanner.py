import time
from config import COINS, SCANNER_INTERVAL
from services.signal_engine import generate_signal

def run_scanner(bot, chat_id):

    print("Scanner started...")

    while True:

        try:

            for coin in COINS.keys():

                signal, rsi, reasons = generate_signal(coin, "15m")

                # فقط سیگنال مهم
                if signal != "🟡 خنثی":

                    msg = f"""
🚨 هشدار سیگنال

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
