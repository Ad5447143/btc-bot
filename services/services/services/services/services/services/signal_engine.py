from services.analysis import calculate_rsi
from services.market import get_price

def generate_signal(symbol, interval="15m"):
    rsi = calculate_rsi(symbol, interval)

    score = 0
    reasons = []

    if rsi < 30:
        score += 2
        reasons.append("RSI Oversold")
    elif rsi > 70:
        score -= 2
        reasons.append("RSI Overbought")

    if score >= 2:
        signal = "🟢 خرید"
    elif score <= -2:
        signal = "🔴 فروش"
    else:
        signal = "🟡 خنثی"

    return signal, rsi, reasons
