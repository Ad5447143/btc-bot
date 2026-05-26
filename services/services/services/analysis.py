```python
import pandas as pd

from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator

from services.market import get_klines

from config import (
    RSI_OVERBOUGHT,
    RSI_OVERSOLD
)

# =========================================
# RSI
# =========================================

def calculate_rsi(symbol, timeframe):

    try:

        closes = get_klines(
            symbol,
            timeframe
        )

        if closes is None:
            return None

        df = pd.DataFrame(
            closes,
            columns=["close"]
        )

        rsi = RSIIndicator(
            close=df["close"],
            window=14
        ).rsi()

        return round(
            rsi.iloc[-1],
            2
        )

    except Exception as e:

        print(f"RSI ERROR: {e}")

        return None

# =========================================
# EMA CROSS
# =========================================

def ema_cross(symbol, timeframe):

    try:

        closes = get_klines(
            symbol,
            timeframe
        )

        if closes is None:
            return "خطا"

        df = pd.DataFrame(
            closes,
            columns=["close"]
        )

        ema20 = EMAIndicator(
            close=df["close"],
            window=20
        ).ema_indicator()

        ema50 = EMAIndicator(
            close=df["close"],
            window=50
        ).ema_indicator()

        # =============================
        # CURRENT
        # =============================

        current_20 = ema20.iloc[-1]
        current_50 = ema50.iloc[-1]

        previous_20 = ema20.iloc[-2]
        previous_50 = ema50.iloc[-2]

        # =============================
        # CROSS CHECK
        # =============================

        if (
            previous_20 < previous_50
            and
            current_20 > current_50
        ):

            return "🟢 کراس صعودی"

        elif (
            previous_20 > previous_50
            and
            current_20 < current_50
        ):

            return "🔴 کراس نزولی"

        elif current_20 > current_50:

            return "🟢 روند صعودی"

        else:

            return "🔴 روند نزولی"

    except Exception as e:

        print(f"EMA ERROR: {e}")

        return "خطا"

# =========================================
# MARKET PRESSURE
# =========================================

def market_pressure(symbol, timeframe):

    try:

        rsi = calculate_rsi(
            symbol,
            timeframe
        )

        if rsi is None:
            return "خطا"

        if rsi >= RSI_OVERBOUGHT:

            return "🟢 فشار خرید"

        elif rsi <= RSI_OVERSOLD:

            return "🔴 فشار فروش"

        else:

            return "⚪ خنثی"

    except Exception as e:

        print(f"PRESSURE ERROR: {e}")

        return "خطا"

# =========================================
# RSI DIVERGENCE
# =========================================

def detect_divergence(symbol, timeframe):

    try:

        closes = get_klines(
            symbol,
            timeframe
        )

        if closes is None:
            return None

        if len(closes) < 30:
            return None

        df = pd.DataFrame(
            closes,
            columns=["close"]
        )

        rsi = RSIIndicator(
            close=df["close"],
            window=14
        ).rsi()

        # =============================
        # POSITIVE DIVERGENCE
        # =============================

        if (
            df["close"].iloc[-1]
            <
            df["close"].iloc[-5]

            and

            rsi.iloc[-1]
            >
            rsi.iloc[-5]
        ):

            return "🟢 واگرایی مثبت"

        # =============================
        # NEGATIVE DIVERGENCE
        # =============================

        elif (
            df["close"].iloc[-1]
            >
            df["close"].iloc[-5]

            and

            rsi.iloc[-1]
            <
            rsi.iloc[-5]
        ):

            return "🔴 واگرایی منفی"

        return None

    except Exception as e:

        print(f"DIVERGENCE ERROR: {e}")

        return None

# =========================================
# MULTI TIMEFRAME ANALYSIS
# =========================================

def multi_timeframe_analysis(symbol):

    try:

        timeframes = [
            "5m",
            "15m",
            "4H",
            "1D"
        ]

        result = []

        bullish = 0
        bearish = 0

        for tf in timeframes:

            ema = ema_cross(
                symbol,
                tf
            )

            if "صعودی" in ema:

                bullish += 1

            elif "نزولی" in ema:

                bearish += 1

            result.append(
                f"{tf} → {ema}"
            )

        # =============================
        # FINAL RESULT
        # =============================

        if bullish > bearish:

            final = "🟢 بازار صعودی"

        elif bearish > bullish:

            final = "🔴 بازار نزولی"

        else:

            final = "⚪ بازار خنثی"

        text = "\n".join(result)

        return f"""
📊 تحلیل مولتی تایم‌فریم

{text}

━━━━━━━━━━━━━━

نتیجه نهایی:
{final}
"""

    except Exception as e:

        print(f"MULTI TF ERROR: {e}")

        return "خطا"
```
