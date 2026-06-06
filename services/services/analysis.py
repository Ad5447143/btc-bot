import requests
import pandas as pd

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

def get_ohlc(symbol, days=1):

    coin_id = COIN_MAP.get(symbol)

    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days={days}"

    data = requests.get(url).json()

    prices = data["prices"]

    df = pd.DataFrame(prices, columns=["time", "price"])

    return df

# =====================
# RSI واقعی (CoinGecko)
# =====================

def calculate_rsi(symbol):

    df = get_ohlc(symbol)

    close = df["price"]

    delta = close.diff()

    gain = (delta.where(delta > 0, 0)).mean()
    loss = (-delta.where(delta < 0, 0)).mean()

    rs = gain / loss if loss != 0 else 0

    return round(100 - (100 / (1 + rs)), 2)

# =====================
# EMA
# =====================

def ema_cross(symbol):

    df = get_ohlc(symbol)

    close = df["price"]

    ema_fast = close.ewm(span=9).mean()
    ema_slow = close.ewm(span=21).mean()

    if ema_fast.iloc[-1] > ema_slow.iloc[-1]:
        return "bullish"
    else:
        return "bearish"

# =====================
# Divergence ساده
# =====================

def detect_divergence(symbol):

    df = get_ohlc(symbol)

    close = df["price"]

    if close.iloc[-1] > close.iloc[-5]:
        return "no_divergence"
    else:
        return "bullish_divergence"

# =====================
# بازار رنج
# =====================

def is_ranging(symbol):

    df = get_ohlc(symbol)

    high = df["price"].max()
    low = df["price"].min()

    range_percent = ((high - low) / low) * 100

    return range_percent < 1.5
