from services.analysis import calculate_rsi

def generate_signal(symbol, timeframe="15m"):

    rsi = calculate_rsi(symbol, timeframe)

    score = 0
    reasons = []

    # RSI logic
    if rsi < 30:
        score += 2
        reasons.append("RSI اشباع فروش")
    elif rsi > 70:
        score -= 2
        reasons.append("RSI اشباع خرید")

    # تصمیم نهایی
    if score >= 2:
        signal = "🟢 خرید قوی"
    elif score <= -2:
        signal = "🔴 فروش قوی"
    else:
        signal = "🟡 ضعیف"

    return signal, rsi, reasons, score
