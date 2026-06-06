import requests
import pandas as pd

def get_klines(symbol, interval="15m", limit=100):
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
    rsi = 100 - (100 / (1 + rs))

    return round(rsi, 2)
