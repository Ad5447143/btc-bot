from config import COINS

from services.market import (
get_price,
get_rsi,
get_ema_signal,
get_ema_cross,
get_divergence
)

def calculate_score(signal):

```
score = 0

if signal["rsi"] < 30:
    score += 3

elif signal["rsi"] > 70:
    score += 3

if signal["ema_signal"] == "صعودی":
    score += 2

if signal["ema_cross"] == "کراس صعودی":
    score += 2

if signal["divergence"] == "واگرایی مثبت":
    score += 3

return score
```

def get_vip_signals():

```
results = []

for symbol in COINS.keys():

    try:

        price = get_price(symbol)

        rsi = get_rsi(symbol)

        ema_signal = get_ema_signal(symbol)

        ema_cross = get_ema_cross(symbol)

        divergence = get_divergence(symbol)

        signal = {
            "symbol": symbol,
            "timeframe": "1h",
            "price": price,
            "rsi": rsi,
            "ema_signal": ema_signal,
            "ema_cross": ema_cross,
            "divergence": divergence
        }

        signal["score"] = calculate_score(signal)

        if signal["score"] >= 5:

            signal["signal"] = "BUY"

            results.append(signal)

    except Exception as e:

        print(
            "SCANNER ERROR:",
            e
        )

results.sort(
    key=lambda x: x["score"],
    reverse=True
)

return results
```

def get_best_signal():

```
signals = get_vip_signals()

if not signals:
    return None

return signals[0]
```

def format_vip_signal(signal):

```
if not signal:

    return "❌ سیگنالی پیدا نشد"

return f"""
```

🔥 سیگنال VIP

━━━━━━━━━━━━━━

🪙 نماد:
{signal['symbol']}

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

```
text = "📊 خلاصه بازار\n\n"

for symbol in COINS.keys():

    try:

        price = get_price(symbol)

        rsi = get_rsi(symbol)

        trend = get_ema_signal(symbol)

        text += f"""
```

🪙 {symbol}

💰 {price}

📈 RSI: {rsi}

⚡ روند: {trend}

━━━━━━━━━━━━━━
"""

```
    except:

        pass

return text
```
