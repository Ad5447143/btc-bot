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
    if div == "possible_divergence":
        score += 1
        reasons.append("احتمال واگرایی")

    # نتیجه نهایی
    if score >= 3:
        signal = "🟢 خرید قوی"
    elif score <= -3:
        signal = "🔴 فروش قوی"
    else:
        signal = "🟡 ضعیف"

    return signal, rsi, reasons, score
