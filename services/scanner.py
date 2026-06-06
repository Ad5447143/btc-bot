# scanner service

from config import COINS

def run_scanner():
    print("Scanner started")

    for coin in COINS.keys():
        print("Scanning", coin)
