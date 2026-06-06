from services.analysis import calculate_rsi, ema_cross, detect_divergence, is_ranging

def generate_signal(symbol):

    # ❌ فیلتر شدید بازار رنج
    if is_ranging(symbol):
        return "🟡 بازار رنج", 0, ["بازار بدون روند"], 0, None, False

    rsi = calculate_rsi(symbol)
    ema = ema_cross(symbol)
    div = detect_divergence(symbol)

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

    # =========================
    # VIP LOGIC
    # =========================
    is_vip = False

    if score >= 6:
        signal = "🔥 VIP خرید قوی"
        direction = "buy"
        is_vip = True

    elif score <= -6:
        signal = "🔥 VIP فروش قوی"
        direction = "sell"
        is_vip = True

    elif score >= 4:
        signal = "🟢 خرید قوی"
        direction = "buy"

    elif score <= -4:
        signal = "🔴 فروش قوی"
        direction = "sell"

    else:
        signal = "🟡 ضعیف"
        direction = None

    return signal, rsi, reasons, score, direction, is_vip
