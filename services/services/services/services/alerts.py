```python
import json
import os

from config import (
    ALERT_CACHE_FILE
)

# =========================================
# CREATE CACHE FILE
# =========================================

if not os.path.exists(ALERT_CACHE_FILE):

    with open(ALERT_CACHE_FILE, "w") as f:

        json.dump({}, f)

# =========================================
# LOAD CACHE
# =========================================

def load_cache():

    try:

        with open(ALERT_CACHE_FILE, "r") as f:

            return json.load(f)

    except:

        return {}

# =========================================
# SAVE CACHE
# =========================================

def save_cache(data):

    with open(ALERT_CACHE_FILE, "w") as f:

        json.dump(
            data,
            f,
            indent=4
        )

# =========================================
# CHECK ALERT
# =========================================

def already_alerted(key):

    cache = load_cache()

    return key in cache

# =========================================
# SAVE ALERT
# =========================================

def save_alert(key):

    cache = load_cache()

    cache[key] = True

    save_cache(cache)

# =========================================
# SEND ALERT
# =========================================

async def send_alert(
    context,
    chat_id,
    text,
    alert_key
):

    try:

        # =============================
        # ANTI SPAM
        # =============================

        if already_alerted(alert_key):

            return

        # =============================
        # SEND MESSAGE
        # =============================

        await context.bot.send_message(
            chat_id=chat_id,
            text=text
        )

        # =============================
        # SAVE ALERT
        # =============================

        save_alert(alert_key)

        print(f"ALERT SENT: {alert_key}")

    except Exception as e:

        print(f"ALERT ERROR: {e}")

# =========================================
# RESET ALERT
# =========================================

def reset_alert(alert_key):

    cache = load_cache()

    if alert_key in cache:

        del cache[alert_key]

    save_cache(cache)
```
