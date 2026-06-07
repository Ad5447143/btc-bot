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

        score = 0

        # RSI

        if rsi is not None:

            if rsi < 30:

                score += 1

            elif rsi > 70:

                score -= 1

        # EMA TREND

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

    except Exception as e:

        print(
            "SCAN ERROR:",
            e
        )

        return None


def scan_market():

    results = []

    for symbol in COINS.keys():

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

    results = scan_market()

    signals = []

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


def get_best_signal():

    signals = get_vip_signals()

    if not signals:

        return None

    return signals[0]


def get_market_summary():

    results = scan_market()

    bullish = 0
    bearish = 0
    neutral = 0

    for item in results:

        if item["score"] >= 2:

            bullish += 1

        elif item["score"] <= -2:

            bearish += 1

        else:

            neutral += 1

    return {
        "bullish": bullish,
        "bearish": bearish,
        "neutral": neutral,
        "total": len(results)
    }


def format_vip_signal(
    signal
):

    if not signal:

        return """
❌ سیگنال معتبری پیدا نشد
"""

    return f"""
🔥 سیگنال VIP

━━━━━━━━━━━━━━

🪙 نماد:
{signal['symbol']}

⏱ تایم فریم:
{signal['timeframe']}

💰 قیمت:
{signal['price']}

📈 RSI:
{signal['rsi']}

⚡ روند EMA:
{signal['ema_signal']}

⚡ کراس EMA:
{signal['ema_cross']}

📉 واگرایی:
{signal['divergence']}

🎯 امتیاز:
{signal['score']}

🚀 نتیجه:
{signal['signal']}
"""


def format_market_summary():

    summary = get_market_summary()

    return f"""
📊 خلاصه بازار

━━━━━━━━━━━━━━

🟢 صعودی:
{summary['bullish']}

🔴 نزولی:
{summary['bearish']}

🟡 خنثی:
{summary['neutral']}

📦 کل تحلیل‌ها:
{summary['total']}
"""
