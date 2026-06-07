import requests
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator


COIN_MAP = {
    "BTCUSDT": "bitcoin",
    "ETHUSDT": "ethereum",
    "BNBUSDT": "binancecoin",
    "SOLUSDT": "solana",
    "XRPUSDT": "ripple",
    "DOGEUSDT": "dogecoin",
    "ADAUSDT": "cardano",
    "TRXUSDT": "tron"
}


def get_market_chart(symbol):

    coin_id = COIN_MAP.get(symbol)

    if not coin_id:
        return None

    url = (
        f"https://api.coingecko.com/api/v3/coins/"
        f"{coin_id}/market_chart"
        f"?vs_currency=usd&days=7"
    )

    data = requests.get(url, timeout=15).json()

    prices = data.get("prices", [])

    closes = [p[1] for p in prices]

    return closes


def calculate_rsi(symbol):

    closes = get_market_chart(symbol)

    if not closes:
        return None

    df = pd.DataFrame(closes, columns=["close"])

    rsi = RSIIndicator(
        close=df["close"],
        window=14
    ).rsi()

    return round(float(rsi.iloc[-1]), 2)


def ema_cross(symbol):

    closes = get_market_chart(symbol)

    if not closes:
        return "unknown"

    df = pd.DataFrame(closes, columns=["close"])

    ema20 = EMAIndicator(
        close=df["close"],
        window=20
    ).ema_indicator()

    ema50 = EMAIndicator(
        close=df["close"],
        window=50
    ).ema_indicator()

    if ema20.iloc[-1] > ema50.iloc[-1]:
        return "bullish"

    return "bearish"


def detect_divergence(symbol):

    rsi = calculate_rsi(symbol)

    if rsi is None:
        return "none"

    if rsi < 30:
        return "bullish_divergence"

    if rsi > 70:
        return "bearish_divergence"

    return "none"


def market_pressure(symbol):

    rsi = calculate_rsi(symbol)

    if rsi is None:
        return "unknown"

    if rsi > 60:
        return "buyers"

    if rsi < 40:
        return "sellers"

    return "neutral"
