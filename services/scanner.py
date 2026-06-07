import time

from config import COINS
from services.signal_engine import generate_signal

last_signals = {}

def run_scanner():

    print("🚀 Scanner Started")

    while True:

        try:

            for coin in COINS.keys():

                signal, score = generate_signal(coin)

                if score >= 4:

                    if last_signals.get(coin) == signal:
                        continue

                    last_signals[coin] = signal

                    print(
                        f"🟢 {coin} | Signal Score: {score}"
                    )

        except Exception as e:

            print(
                f"Scanner Error: {e}"
            )

        time.sleep(300)
