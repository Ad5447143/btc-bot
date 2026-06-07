import requests

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

        url = (
            "https://api.coingecko.com/api/v3/simple/price"
            f"?ids={coin_id}&vs_currencies=usd"
        )

        data = requests.get(url, timeout=10).json()

        return data[coin_id]["usd"]

    except Exception as e:
        print("Market Error:", e)
        return None
