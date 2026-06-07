targets = {}

def add_target(symbol, price):

    targets[symbol] = price

def check_target(symbol, current_price):

    if symbol not in targets:
        return False

    return current_price >= targets[symbol]
