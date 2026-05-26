```python id="7fuhp8"
from services.analysis import (
    calculate_rsi,
    ema_cross,
    detect_divergence
)

from services.alerts import (
    send_alert
)

from config import (
    COINS
)

# =========================================
# SCANNER
# =========================================

async def market_scanner(context):

    try:

        print("SCANNER RUNNING...")

        # =====================================
        # ALL USERS
        # =====================================

        users = []

        try:

            with open("storage/vip_users.json", "r") as f:

                import json

                users = json.load(f)

        except:

            users = []

        # =====================================
        # IF NO USERS
        # =====================================

        if len(users) == 0:

            print("NO USERS FOUND")

            return

        # =====================================
        # SCAN
        # =====================================

        for user_id in users:

            for coin in COINS.keys():

                # =============================
                # EMA SCAN
                # =============================

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
                            user_id,
                            text,
                            alert_key
                        )

                # =============================
                # RSI SCAN
                # =============================

                for tf in ["5m", "15m", "4H", "1D"]:

                    rsi = calculate_rsi(
                        coin,
                        tf
                    )

                    if rsi is None:
                        continue

                    # =========================
                    # OVERBOUGHT
                    # =========================

                    if rsi >= 70:

                        alert_key = (
                            f"RSI_HIGH_{coin}_{tf}"
                        )

                        text = f"""
📈 هشدار RSI

💎 {coin}
⏰ {tf}

🟢 RSI بالا

📊 RSI: {rsi}
"""

                        await send_alert(
                            context,
                            user_id,
                            text,
                            alert_key
                        )

                    # =========================
                    # OVERSOLD
                    # =========================

                    elif rsi <= 30:

                        alert_key = (
                            f"RSI_LOW_{coin}_{tf}"
                        )

                        text = f"""
📉 هشدار RSI

💎 {coin}
⏰ {tf}

🔴 RSI پایین

📊 RSI: {rsi}
"""

                        await send_alert(
                            context,
                            user_id,
                            text,
                            alert_key
                        )

                # =============================
                # DIVERGENCE
                # =============================

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
📉 هشدار واگرایی

💎 {coin}
⏰ {tf}

{div}
"""

                    await send_alert(
                        context,
                        user_id,
                        text,
                        alert_key
                    )

    except Exception as e:

        print(f"SCANNER ERROR: {e}")
```
