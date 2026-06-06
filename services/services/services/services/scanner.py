import time
from config import COINS, SCANNER_INTERVAL
from services.signal_engine import generate_signal

def run_scanner(bot, chat_id):
    while True:
        for coin in COINS.keys():

            signal, rsi, reasons = generate_signal(coin)

            if signal != "🟡 خنثی":

                msg = f"""
🚨 سیگنال جدید

💎 {coin}
📊 RSI: {rsi}

📡 {signal}

🧠 {', '.join(reasons)}
"""

                bot.send_message(chat_id, msg)

        time.sleep(SCANNER_INTERVAL)
