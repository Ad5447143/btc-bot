from services.analysis import (
    calculate_rsi,
    ema_cross,
    detect_divergence,
    market_pressure
)


def generate_signal(symbol):

    score = 0

    reasons = []

    rsi = calculate_rsi(symbol)

    if rsi is None:
        return (
            "NO SIGNAL",
            0,
            []
        )

    # RSI

    if rsi < 30:
        score += 2
        reasons.append("RSI Oversold")

    elif rsi > 70:
        score -= 2
        reasons.append("RSI Overbought")

    # EMA

    ema = ema_cross(symbol)

    if ema == "bullish":
        score += 2
        reasons.append("Bullish EMA Cross")

    elif ema == "bearish":
        score -= 2
        reasons.append("Bearish EMA Cross")

    # Divergence

    div = detect_divergence(symbol)

    if div == "bullish_divergence":
        score += 2
        reasons.append("Bullish Divergence")

    elif div == "bearish_divergence":
        score -= 2
        reasons.append("Bearish Divergence")

    # Pressure

    pressure = market_pressure(symbol)

    if pressure == "buyers":
        score += 1
        reasons.append("Buyers Pressure")

    elif pressure == "sellers":
        score -= 1
        reasons.append("Sellers Pressure")

    # FINAL SIGNAL

    if score >= 5:

        signal = "🔥 VIP BUY"

    elif score >= 3:

        signal = "📈 BUY"

    elif score <= -5:

        signal = "🔥 VIP SELL"

    elif score <= -3:

        signal = "📉 SELL"

    else:

        signal = "❌ NO SIGNAL"

    return (
        signal,
        score,
        reasons
    )
