import random

def calculate_rsi(symbol, timeframe="1h"):
    return random.randint(25, 75)

def ema_cross(symbol, timeframe="1h"):

    rsi = calculate_rsi(symbol, timeframe)

    if rsi > 50:
        return "bullish"

    return "bearish"

def detect_divergence(symbol, timeframe="1h"):

    rsi = calculate_rsi(symbol, timeframe)

    if rsi < 35:
        return "bullish_divergence"

    if rsi > 65:
        return "bearish_divergence"

    return "none"

def is_ranging(symbol):

    rsi = calculate_rsi(symbol)

    return 45 <= rsi <= 55
