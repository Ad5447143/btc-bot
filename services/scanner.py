from services.market import (
    get_price,
    get_rsi,
    get_ema_signal,
    get_ema_cross,
    get_divergence
)

from config import COINS


TIMEFRAMES = [
    "5m",
    "15m",
    "1h",
    "4h",
    "1d"
]


def analyze_symbol(
    symbol,
    timeframe="1h"
):

    try:

        score = 0

        price = get_price(symbol)

        rsi = get_rsi(
            symbol,
            timeframe
        )

        ema_signal = get_ema_signal(
            symbol,
            timeframe
        )

        ema_cross = get_ema_cross(
            symbol,
            timeframe
        )

        divergence = get_divergence(
            symbol,
            timeframe
        )

        # RSI

        if rsi:

            if rsi < 30:

                score += 1

            elif rsi > 70:

                score -= 1

        # EMA

        if ema_signal == "صعودی":

            score += 1

        elif ema_signal == "نزولی":

            score -= 1

        # EMA CROSS

        if ema_cross == "کراس صعودی":

            score += 1

        elif ema_cross == "کراس نزولی":

            score -= 1

        # DIVERGENCE

        if divergence == "واگرایی مثبت":

            score += 1

        elif divergence == "واگرایی منفی":

            score -= 1

        signal = "خنثی"

        if score >= 3:

            signal = "خرید قوی"

        elif score == 2:

            signal = "خرید"

        elif score <= -3:

            signal = "فروش قوی"

        elif score == -2:

            signal = "فروش"

        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "price": price,
            "rsi": rsi,
            "ema_signal": ema_signal,
            "ema_cross": ema_cross,
            "divergence": divergence,
            "score": score,
            "signal": signal
        }

    except:

        return None


def scan_market():

    results = []

    for symbol in COINS:

        for timeframe in TIMEFRAMES:

            result = analyze_symbol(
                symbol,
                timeframe
            )

            if result:

                results.append(
                    result
                )

    return results


def get_vip_signals():

    signals = []

    results = scan_market()

    for item in results:

        if item["score"] >= 3:

            signals.append(
                item
            )

    signals.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return signals
