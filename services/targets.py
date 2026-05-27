```python
import json
import os

from config import (
    TARGETS_FILE,
    ADMIN_ID
)

from services.market import (
    get_price
)

from services.alerts import (
    send_alert
)

# =========================================
# CREATE FILE
# =========================================

if not os.path.exists(TARGETS_FILE):

    with open(TARGETS_FILE, "w") as f:

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

    item = {
        "coin": coin,
        "timeframe": timeframe,
        "targets": [
            target1,
            target2,
            target3
        ]
    }

    data.append(item)

    save_targets(data)

# =========================================
# CHECK TARGETS
# =========================================

async def check_targets(context):

    try:

        data = load_targets()

        if len(data) == 0:

            return

        for item in data:

            coin = item["coin"]

            timeframe = item["timeframe"]

            targets = item["targets"]

            price = get_price(coin)

            if price is None:

                continue

            for i, target in enumerate(targets):

                if target is None:
                    continue

                if price >= target:

                    alert_key = (
                        f"TARGET_{coin}_{timeframe}_{target}"
                    )

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
                        alert_key
                    )

    except Exception as e:

        print(f"TARGET ERROR: {e}")
```
