```python id="8qoh6m"
from services.analysis import (
    calculate_rsi,
    ema_cross,
    detect_divergence
)

from services.alerts import (
    send_alert
)

from config import (
    COINS,
    ADMIN_ID
)

# =========================================
# SCANNER
# =========================================

async def market_scanner(context):

    try:

        print("SCANNER RUNNING...")

        # =====================================
        # ALL COINS
        # =====================================

        for coin in COINS.keys():

            # =================================
            # EMA SCANNER
            # =================================

            for tf in ["5m", "15m", "4H", "1D"]:

                ema = ema_cross(
                    coin,
                    tf
                )

                if (
                    "کراس صعودی" in ema
                    or
                    "کراس نزولی" in ema
                ):

                    alert_key = (
                        f"EMA_{coin}_{tf}_{ema}"
                    )

                    text = f"""
⚡ هشدار EMA

💎 {coin}
⏰ {tf}

{ema}
"""

                    await send_alert(
                        context,
                        ADMIN_ID,
                        text,
                        alert_key
                    )

            # =================================
            # RSI SCANNER
            # =================================

            for tf in ["5m", "15m", "4H", "1D"]:

                rsi = calculate_rsi(
                    coin,
                    tf
                )

                if rsi is None:
                    continue

                # =============================
                # RSI HIGH
                # =============================

                if rsi >= 70:

                    alert_key = (
                        f"RSI_HIGH_{coin}_{tf}"
                    )

                    text = f"""
📈 هشدار RSI

💎 {coin}
⏰ {tf}

🟢 اشباع خرید

📊 RSI: {rsi}
"""

                    await send_alert(
                        context,
                        ADMIN_ID,
                        text,
                        alert_key
                    )

                # =============================
                # RSI LOW
                # =============================

                elif rsi <= 30:

                    alert_key = (
                        f"RSI_LOW_{coin}_{tf}"
                    )

                    text = f"""
📉 هشدار RSI

💎 {coin}
⏰ {tf}

🔴 اشباع فروش

📊 RSI: {rsi}
"""

                    await send_alert(
                        context,
                        ADMIN_ID,
                        text,
                        alert_key
                    )

            # =================================
            # DIVERGENCE
            # =================================

            for tf in ["4H", "1D"]:

                div = detect_divergence(
                    coin,
                    tf
                )

                if div is None:
                    continue

                alert_key = (
                    f"DIV_{coin}_{tf}_{div}"
                )

                text = f"""
📉 هشدار واگرایی RSI

💎 {coin}
⏰ {tf}

{div}
"""

                await send_alert(
                    context,
                    ADMIN_ID,
                    text,
                    alert_key
                )

        print("SCANNER DONE ✅")

    except Exception as e:

        print(f"SCANNER ERROR: {e}")
```
