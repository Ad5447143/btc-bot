import requests
import pandas as pd

from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator

from config import COINS


def get_market_data(
    symbol="BTCUSDT",
    days=30
):

    try:

        coin_id = COINS[symbol]

        url = (
            f"https://api.coingecko.com/api/v3/coins/"
            f"{coin_id}/market_chart"
            f"?vs_currency=usd&days={days}"
        )

        response = requests.get(
            url,
            timeout=20
        )

        data = response.json()

        prices = [
            x[1]
            for x in data["prices"]
        ]

        df = pd.DataFrame(
            prices,
            columns=["close"]
        )

        return df

    except Exception as e:

        print(
            "COINGECKO ERROR:",
            e
        )

        return None


def get_price(
    symbol="BTCUSDT"
):

    try:

        coin_id = COINS[symbol]

        url = (
            "https://api.coingecko.com/api/v3/simple/price"
            f"?ids={coin_id}"
            "&vs_currencies=usd"
        )

        data = requests.get(
            url,
            timeout=10
        ).json()

        return float(
            data[coin_id]["usd"]
        )

    except Exception as e:

        print(
            "PRICE ERROR:",
            e
        )

        return None


def get_rsi(
    symbol="BTCUSDT",
    timeframe="1h"
):

    try:

        df = get_market_data(
            symbol
        )

        rsi = RSIIndicator(
            close=df["close"],
            window=14
        ).rsi()

        return round(
            float(
                rsi.iloc[-1]
            ),
            2
        )

    except Exception as e:

        print(
            "RSI ERROR:",
            e
        )

        return None


def get_ema20(
    symbol="BTCUSDT",
    timeframe="1h"
):

    try:

        df = get_market_data(
            symbol
        )

        ema = EMAIndicator(
            close=df["close"],
            window=20
        ).ema_indicator()

        return round(
            float(
                ema.iloc[-1]
            ),
            4
        )

    except Exception as e:

        print(
            "EMA20 ERROR:",
            e
        )

        return None


def get_ema50(
    symbol="BTCUSDT",
    timeframe="1h"
):

    try:

        df = get_market_data(
            symbol
        )

        ema = EMAIndicator(
            close=df["close"],
            window=50
        ).ema_indicator()

        return round(
            float(
                ema.iloc[-1]
            ),
            4
        )

    except Exception as e:

        print(
            "EMA50 ERROR:",
            e
        )

        return None


def get_ema_signal(
    symbol="BTCUSDT",
    timeframe="1h"
):

    try:

        ema20 = get_ema20(
            symbol,
            timeframe
        )

        ema50 = get_ema50(
            symbol,
            timeframe
        )

        if ema20 > ema50:

            return "صعودی"

        elif ema20 < ema50:

            return "نزولی"

        return "خنثی"

    except:

        return "نامشخص"


def get_ema_cross(
    symbol="BTCUSDT",
    timeframe="1h"
):

    try:

        df = get_market_data(
            symbol
        )

        ema20 = EMAIndicator(
            close=df["close"],
            window=20
        ).ema_indicator()

        ema50 = EMAIndicator(
            close=df["close"],
            window=50
        ).ema_indicator()

        prev20 = ema20.iloc[-2]
        prev50 = ema50.iloc[-2]

        last20 = ema20.iloc[-1]
        last50 = ema50.iloc[-1]

        if prev20 < prev50 and last20 > last50:

            return "کراس صعودی"

        if prev20 > prev50 and last20 < last50:

            return "کراس نزولی"

        return None

    except Exception as e:

        print(
            "CROSS ERROR:",
            e
        )

        return None


def get_divergence(
    symbol="BTCUSDT",
    timeframe="1h"
):

    try:

        df = get_market_data(
            symbol
        )

        rsi = RSIIndicator(
            close=df["close"],
            window=14
        ).rsi()

        price_last = df["close"].iloc[-1]
        price_old = df["close"].iloc[-15]

        rsi_last = rsi.iloc[-1]
        rsi_old = rsi.iloc[-15]

        if (
            price_last < price_old
            and
            rsi_last > rsi_old
        ):

            return "واگرایی مثبت"

        if (
            price_last > price_old
            and
            rsi_last < rsi_old
        ):

            return "واگرایی منفی"

        return None

    except Exception as e:

        print(
            "DIVERGENCE ERROR:",
            e
        )

        return None
