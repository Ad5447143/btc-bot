from services.analysis import (
    calculate_rsi,
    ema_cross,
    detect_divergence,
    is_ranging
)

def generate_signal(symbol):

    if is_ranging(symbol):
        return "RANGE", 0

    score = 0

    rsi = calculate_rsi(symbol)

    if rsi < 30:
        score += 2

    if rsi > 70:
        score -= 2

    if ema_cross(symbol) == "bullish":
        score += 2
    else:
        score -= 2

    if detect_divergence(symbol) == "bullish_divergence":
        score += 2

    return "SIGNAL", score
