from services.analysis import calculate_rsi, ema_cross, detect_divergence

def generate_signal(symbol, timeframe="15m"):

    rsi = calculate_rsi(symbol, timeframe)
    ema = ema_cross(symbol, timeframe)
    div = detect_divergence(symbol, timeframe)

    score = 0
    reasons = []

    # RSI
    if rsi < 30:
        score += 2
        reasons.append("RSI اشباع فروش")
    elif rsi > 70:
        score -= 2
        reasons.append("RSI اشباع خرید")

    # EMA
    if ema == "bullish":
        score += 2
        reasons.append("EMA صعودی")
    else:
        score -= 2
        reasons.append("EMA نزولی")

    # Divergence
    if div == "bullish_divergence":
        score += 2
        reasons.append("واگرایی صعودی")

    # نتیجه
    if score >= 4:
        signal = "🟢 خرید قوی"
    elif score <= -4:
        signal = "🔴 فروش قوی"
    else:
        signal = "🟡 ضعیف"

    return signal, rsi, reasons, score
