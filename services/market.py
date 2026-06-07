import requests
import pandas as pd

from ta.momentum import RSIIndicator


def get_price(symbol="bitcoin"):

    try:

        url = (
            "https://api.coingecko.com/api/v3/simple/price"
            f"?ids={symbol}&vs_currencies=usd"
        )

        data = requests.get(
            url,
            timeout=10
        ).json()

        return data[symbol]["usd"]

    except:

        return None


def get_rsi(symbol="bitcoin"):

    try:

        url = (
            f"https://api.coingecko.com/api/v3/coins/{symbol}"
            "/market_chart?vs_currency=usd&days=30"
        )

        data = requests.get(
            url,
            timeout=10
        ).json()

        prices = [
            x[1]
            for x in data["prices"]
        ]

        df = pd.DataFrame(
            prices,
            columns=["close"]
        )

        rsi = RSIIndicator(
            close=df["close"],
            window=14
        ).rsi()

        return round(
            float(rsi.iloc[-1]),
            2
        )

    except:

        return None
