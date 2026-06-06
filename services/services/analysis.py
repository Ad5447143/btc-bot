import requests
import pandas as pd

def get_klines(symbol, interval="15m", limit=100):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    data = requests.get(url).json()
    return pd.DataFrame(data)

def ema_cross(symbol, interval="15m"):
    df = get_klines(symbol, interval)

    close = df[4].astype(float)

    ema_fast = close.ewm(span=9).mean()
    ema_slow = close.ewm(span=21).mean()

    if ema_fast.iloc[-1] > ema_slow.iloc[-1]:
        return "bullish"
    else:
        return "bearish"
