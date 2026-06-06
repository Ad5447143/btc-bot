import requests
import pandas as pd

def get_klines(symbol, interval="15m", limit=50):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    data = requests.get(url).json()
    return pd.DataFrame(data)

def calculate_rsi(symbol, interval="15m"):
    df = get_klines(symbol, interval)

    close = df[4].astype(float)
    delta = close.diff()

    gain = (delta.where(delta > 0, 0)).mean()
    loss = (-delta.where(delta < 0, 0)).mean()

    rs = gain / loss if loss != 0 else 0
    return round(100 - (100 / (1 + rs)), 2)

# =========================
# EMA
# =========================
def ema_cross(symbol, interval="15m"):
    df = get_klines(symbol, interval)

    close = df[4].astype(float)

    ema_fast = close.ewm(span=9).mean()
    ema_slow = close.ewm(span=21).mean()

    if ema_fast.iloc[-1] > ema_slow.iloc[-1]:
        return "bullish"
    else:
        return "bearish"

# =========================
# RSI DIVERGENCE (MVP REAL)
# =========================
def detect_divergence(symbol, interval="15m"):

    df = get_klines(symbol, interval)

    close = df[4].astype(float)

    price_high = close.iloc[-1]
    price_prev = close.iloc[-5]

    # ساده ولی کاربردی
    if price_high > price_prev:
        return "no_divergence"
    else:
        return "bullish_divergence"
