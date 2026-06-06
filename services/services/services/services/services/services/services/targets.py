from services.analysis import calculate_rsi, ema_cross, detect_divergence, is_ranging

def generate_signal(symbol):

    if is_ranging(symbol):
        return "🟡 بازار رنج", 0, ["بازار بدون روند"], 0

    rsi = calculate_rsi(symbol)
    ema = ema_cross(symbol)
    div = detect_divergence(symbol)

    score = 0
    reasons = []

    if rsi < 30:
        score += 2
        reasons.append("RSI اشباع فروش")
    elif rsi > 70:
        score -= 2
        reasons.append("RSI اشباع خرید")

    if ema == "bullish":
        score += 2
        reasons.append("EMA صعودی")
    else:
        score -= 2
        reasons.append("EMA نزولی")

    if div == "bullish_divergence":
        score += 2
        reasons.append("واگرایی صعودی")

    if score >= 4:
        signal = "🟢 خرید قوی"
    elif score <= -4:
        signal = "🔴 فروش قوی"
    else:
        signal = "🟡 ضعیف"

    return signal, rsi, reasons, score
