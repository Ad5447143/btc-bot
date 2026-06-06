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

                signal, rsi, reasons, score, direction = generate_signal(coin)

                price = get_price(coin)

                # بررسی تارگت
                result = check_targets(coin, price)
                if result:
                    bot.send_message(chat_id, f"🚨 {coin}\n{result}")

                # فقط سیگنال قوی
                if score >= 4 or score <= -4:

                    if last_signal.get(coin) == signal:
                        continue

                    last_signal[coin] = signal

                    # تنظیم تارگت
                    if direction:
                        tp, sl = set_target(coin, direction, price)

                        msg = f"""
🚨 سیگنال قوی

💎 {coin}
💰 قیمت: {price}

📊 RSI: {rsi}
📡 {signal}

🎯 TP: {tp}
🛑 SL: {sl}

🧠 {', '.join(reasons)}
"""
                        bot.send_message(chat_id, msg)

        except Exception as e:
            print("Scanner error:", e)

        time.sleep(SCANNER_INTERVAL)
