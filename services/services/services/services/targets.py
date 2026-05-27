```python
import json
import os

from config import (
    ADMIN_ID
)

from services.market import (
    get_price
)

from services.analysis import (
    calculate_rsi
)

from services.alerts import (
    send_alert
)

# =========================================
# FILES
# =========================================

TARGETS_FILE = "storage/targets.json"

RSI_TARGETS_FILE = "storage/rsi_targets.json"

# =========================================
# CREATE FILES
# =========================================

if not os.path.exists(TARGETS_FILE):

    with open(TARGETS_FILE, "w") as f:

        json.dump([], f)

if not os.path.exists(RSI_TARGETS_FILE):

    with open(RSI_TARGETS_FILE, "w") as f:

        json.dump([], f)

# =========================================
# LOAD TARGETS
# =========================================

def load_targets():

    try:

        with open(TARGETS_FILE, "r") as f:

            return json.load(f)

    except:

        return []

# =========================================
# SAVE TARGETS
# =========================================

def save_targets(data):

    with open(TARGETS_FILE, "w") as f:

        json.dump(
            data,
            f,
            indent=4
        )

# =========================================
# ADD TARGET
# =========================================

def add_target(
    coin,
    timeframe,
    target1,
    target2,
    target3
):

    data = load_targets()

    data.append({

        "coin": coin,

        "timeframe": timeframe,

        "targets": [
            target1,
            target2,
            target3
        ]

    })

    save_targets(data)

# =========================================
# CHECK TARGETS
# =========================================

async def check_targets(context):

    try:

        data = load_targets()

        for item in data:

            coin = item["coin"]

            timeframe = item["timeframe"]

            targets = item["targets"]

            price = get_price(coin)

            if price is None:

                continue

            for i, target in enumerate(targets):

                if price >= target:

                    text = f"""
🎯 تارگت فعال شد

💎 {coin}
⏰ {timeframe}

✅ Target {i+1}

💰 قیمت:
{price}$

🎯 تارگت:
{target}$
"""

                    await send_alert(
                        context,
                        ADMIN_ID,
                        text,
                        f"TARGET_{coin}_{timeframe}_{target}"
                    )

    except Exception as e:

        print(f"TARGET ERROR: {e}")

# =========================================
# RSI TARGETS
# =========================================

def load_rsi_targets():

    try:

        with open(
            RSI_TARGETS_FILE,
            "r"
        ) as f:

            return json.load(f)

    except:

        return []

# =========================================
# SAVE RSI TARGETS
# =========================================

def save_rsi_targets(data):

    with open(
        RSI_TARGETS_FILE,
        "w"
    ) as f:

        json.dump(
            data,
            f,
            indent=4
        )

# =========================================
# ADD RSI TARGET
# =========================================

def add_rsi_target(
    coin,
    timeframe,
    target
):

    data = load_rsi_targets()

    data.append({

        "coin": coin,

        "timeframe": timeframe,

        "target": target

    })

    save_rsi_targets(data)

# =========================================
# CHECK RSI TARGETS
# =========================================

async def check_rsi_targets(context):

    try:

        data = load_rsi_targets()

        for item in data:

            coin = item["coin"]

            timeframe = item["timeframe"]

            target = item["target"]

            rsi = calculate_rsi(
                coin,
                timeframe
            )

            if rsi is None:

                continue

            if rsi >= target:

                text = f"""
🚨 RSI Target Hit

💎 {coin}
⏰ {timeframe}

📈 RSI:
{rsi}

🎯 Target:
{target}
"""

                await send_alert(
                    context,
                    ADMIN_ID,
                    text,
                    f"RSI_{coin}_{timeframe}_{target}"
                )

    except Exception as e:

        print(
            f"RSI TARGET ERROR: {e}"
        )
```
