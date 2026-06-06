import requests

# تبدیل کوین به id کوین‌گکو
COIN_MAP = {
    "BTCUSDT": "bitcoin",
    "ETHUSDT": "ethereum",
    "BNBUSDT": "binancecoin",
    "SOLUSDT": "solana",
    "XRPUSDT": "ripple",
    "DOGEUSDT": "dogecoin",
    "ADAUSDT": "cardano",
    "TRXUSDT": "tron"
}

def get_price(symbol):

    try:
        coin_id = COIN_MAP.get(symbol)

        if not coin_id:
            return None

        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"

        data = requests.get(url).json()

        return data[coin_id]["usd"]

    except:
        return None
