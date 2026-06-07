import requests
import pandas as pd

from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator


BASE_URL = "https://api.bybit.com/v5/market/kline"


TIMEFRAMES = {
    "5m": "5",
    "15m": "15",
    "1h": "60",
    "4h": "240",
    "1d": "D"
}


def get_klines(
    symbol="BTCUSDT",
    timeframe="1h",
    limit=200
):

    try:

        interval = TIMEFRAMES[timeframe]

        params = {
            "category": "linear",
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }

        response = requests.get(
            BASE_URL,
            params=params,
            timeout=15
        )

        data = response.json()

        candles = data["result"]["list"]

        candles.reverse()

        df = pd.DataFrame(
            candles,
            columns=[
                "time",
                "open",
                "high",
                "low",
                "close",
                "volume",
                "turnover"
            ]
        )

        df["close"] = df["close"].astype(float)
        df["high"] = df["high"].astype(float)
        df["low"] = df["low"].astype(float)

        return df

    except:

        return None


def get_price(
    symbol="BTCUSDT"
):

    try:

        df = get_klines(
            symbol,
            "5m",
            2
        )

        return float(
            df["close"].iloc[-1]
        )

    except:

        return None


def get_rsi(
    symbol="BTCUSDT",
    timeframe="1h"
):

    try:

        df = get_klines(
            symbol,
            timeframe
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


def get_ema20(
    symbol="BTCUSDT",
    timeframe="1h"
):

    try:

        df = get_klines(
            symbol,
            timeframe
        )

        ema = EMAIndicator(
            close=df["close"],
            window=20
        ).ema_indicator()

        return round(
            float(ema.iloc[-1]),
            2
        )

    except:

        return None


def get_ema50(
    symbol="BTCUSDT",
    timeframe="1h"
):

    try:

        df = get_klines(
            symbol,
            timeframe
        )

        ema = EMAIndicator(
            close=df["close"],
            window=50
        ).ema_indicator()

        return round(
            float(ema.iloc[-1]),
            2
        )

    except:

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

        df = get_klines(
            symbol,
            timeframe
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

    except:

        return None


def get_divergence(
    symbol="BTCUSDT",
    timeframe="1h"
):

    try:

        df = get_klines(
            symbol,
            timeframe,
            60
        )

        rsi = RSIIndicator(
            close=df["close"],
            window=14
        ).rsi()

        price_last = df["close"].iloc[-1]
        price_old = df["close"].iloc[-15]

        rsi_last = rsi.iloc[-1]
        rsi_old = rsi.iloc[-15]

        if price_last < price_old and rsi_last > rsi_old:

            return "واگرایی مثبت"

        if price_last > price_old and rsi_last < rsi_old:

            return "واگرایی منفی"

        return None

    except:

        return None
