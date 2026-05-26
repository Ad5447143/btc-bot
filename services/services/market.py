```python id="8lx9mq"
import requests

from config import (
    COINS,
    TIMEFRAMES
)

# =========================================
# GET PRICE
# =========================================

def get_price(symbol):

    try:

        coin_id = COINS[symbol]

        url = (
            "https://api.coingecko.com/api/v3/simple/price"
            f"?ids={coin_id}&vs_currencies=usd"
        )

        response = requests.get(
            url,
            timeout=10
        )

        data = response.json()

        return data[coin_id]["usd"]

    except Exception as e:

        print(f"PRICE ERROR: {e}")

        return None

# =========================================
# GET KLINES
# =========================================

def get_klines(symbol, timeframe):

    try:

        tf = TIMEFRAMES[timeframe]

        url = (
            "https://api.kucoin.com/api/v1/market/candles"
            f"?type={tf}&symbol={symbol}-USDT"
        )

        response = requests.get(
            url,
            timeout=10
        )

        data = response.json()

        candles = data["data"]

        closes = []

        for candle in candles:

            closes.append(
                float(candle[2])
            )

        closes.reverse()

        return closes

    except Exception as e:

        print(f"KLINES ERROR: {e}")

        return None

# =========================================
# API HEALTH
# =========================================

def api_health():

    try:

        btc = get_price("BTC")

        if btc is None:

            return False

        return True

    except:

        return False
```
