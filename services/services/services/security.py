```python
import json
import os
import time

from config import ADMIN_ID

# =========================================
# FILES
# =========================================

USERS_FILE = "users.json"

# =========================================
# CREATE FILE
# =========================================

if not os.path.exists(USERS_FILE):

    with open(USERS_FILE, "w") as f:

        json.dump([], f)

# =========================================
# REQUEST CACHE
# =========================================

request_cache = {}

# =========================================
# LOAD USERS
# =========================================

def load_users():

    try:

        with open(USERS_FILE, "r") as f:

            return json.load(f)

    except:

        return []

# =========================================
# SAVE USERS
# =========================================

def save_users(users):

    with open(USERS_FILE, "w") as f:

        json.dump(
            users,
            f,
            indent=4
        )

# =========================================
# REGISTER USER
# =========================================

async def register_user(
    update,
    context
):

    user = update.effective_user

    users = load_users()

    exists = False

    for u in users:

        if u["id"] == user.id:

            exists = True

            break

    if not exists:

        users.append(
            {
                "id": user.id,
                "username": user.username
            }
        )

        save_users(users)

        # =============================
        # ADMIN ALERT
        # =============================

        try:

            text = f"""
🚨 کاربر جدید وارد ربات شد

👤 {user.username}

🆔 {user.id}
"""

            await context.bot.send_message(
                ADMIN_ID,
                text
            )

        except:

            pass

# =========================================
# USERS TEXT
# =========================================

def users_text():

    users = load_users()

    if len(users) == 0:

        return "❌ کاربری وجود ندارد"

    text = "👥 کاربران فعال\n\n"

    for u in users:

        text += (
            f"👤 {u['username']}\n"
            f"🆔 {u['id']}\n\n"
        )

    return text

# =========================================
# LIGHT SECURITY
# =========================================

def anti_flood(user_id):

    now = time.time()

    if user_id not in request_cache:

        request_cache[user_id] = []

    request_cache[user_id].append(now)

    request_cache[user_id] = [

        t for t in request_cache[user_id]

        if now - t < 10
    ]

    # =============================
    # FLOOD WARNING
    # =============================

    if len(request_cache[user_id]) > 15:

        print(
            f"FLOOD WARNING: {user_id}"
        )

    return True
```
