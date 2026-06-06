import requests

def get_active_coins():
    """
    دریافت 20 کوین برتر از نظر حجم معاملات از CoinGecko
    خروجی نمونه:
    ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', ...]
    """

    url = "https://api.coingecko.com/api/v3/coins/markets"

    params = {
        "vs_currency": "usd",
        "order": "volume_desc",
        "per_page": 20,
        "page": 1,
        "sparkline": "false"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        coins = []

        for coin in data:
            symbol = coin.get("symbol", "").upper()

            if symbol:
                coins.append(f"{symbol}USDT")

        return coins

    except Exception as e:
        print(f"get_active_coins error: {e}")
        return []
