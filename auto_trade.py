import robin_stocks.robinhood as r
from binance.client import Client
import time
import pandas

# Robinhood login
r.login('your_robinhood_username', 'your_robinhood_password')

# Binance API setup
binance_client = Client('your_binance_api_key', 'your_binance_api_secret')

SYMBOL = 'BTCUSD'
QUANTITY = 0.001  # Example quantity

def get_binance_price(symbol):
    ticker = binance_client.get_symbol_ticker(symbol=symbol.replace('USD', 'USDT'))
    return float(ticker['price'])

def get_last_buy_price(symbol):
    orders = r.orders.get_all_crypto_orders()
    buys = [o for o in orders if o['side'] == 'buy' and o['state'] == 'filled' and o['currency_pair_id'].startswith(symbol.lower())]
    if not buys:
        return None
    last_buy = sorted(buys, key=lambda x: x['created_at'], reverse=True)[0]
    return float(last_buy['average_price'])

def buy_crypto(symbol, quantity):
    print(f"Buying {quantity} {symbol}")
    r.orders.order_buy_crypto_by_quantity(symbol, quantity)

def sell_crypto(symbol, quantity):
    print(f"Selling {quantity} {symbol}")
    r.orders.order_sell_crypto_by_quantity(symbol, quantity)

def main():
    while True:
        price = get_binance_price(SYMBOL)
        last_buy = get_last_buy_price(SYMBOL)
        print(f"Current price: {price}, Last buy: {last_buy}")

        if last_buy is None or price < last_buy:
            buy_crypto(SYMBOL, QUANTITY)
        elif price > last_buy * 1.01:  # Sell if price is 1% above last buy
            sell_crypto(SYMBOL, QUANTITY)
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    main()