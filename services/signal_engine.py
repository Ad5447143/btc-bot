from services.analysis import calculate_rsi, ema_cross, market_pressure

def generate_signal(coin, timeframe):
    rsi = calculate_rsi(coin, timeframe)
    ema = ema_cross(coin, timeframe)
    pressure = market_pressure(coin)

    score = 0
    reasons = []

    # RSI
    if rsi < 30:
        score += 2
        reasons.append("RSI Oversold")
    elif rsi > 70:
        score -= 2
        reasons.append("RSI Overbought")

    # EMA
    if ema == "bullish":
        score += 2
        reasons.append("EMA Bullish")
    elif ema == "bearish":
        score -= 2
        reasons.append("EMA Bearish")

    # Pressure
    if pressure == "buy":
        score += 1
    elif pressure == "sell":
        score -= 1

    # Final decision
    if score >= 3:
        signal = "🟢 BUY"
    elif score <= -3:
        signal = "🔴 SELL"
    else:
        signal = "🟡 NEUTRAL"

    return signal, score, reasons
