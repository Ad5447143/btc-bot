import requests


def get_price(symbol="bitcoin"):

    url = (
        "https://api.coingecko.com/api/v3/simple/price"
        f"?ids={symbol}&vs_currencies=usd"
    )

    try:

        data = requests.get(
            url,
            timeout=10
        ).json()

        return data[symbol]["usd"]

    except:

        return None
