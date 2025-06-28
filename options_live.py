import robin_stocks.robinhood as r
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

def login_robinhood():
    username = os.getenv("ROBINHOOD_USERNAME")
    password = os.getenv("ROBINHOOD_PASSWORD")
    r.login(username, password)

def get_live_options_data(symbol, expiration_date=None, option_type='call'):
    """
    Fetches live options data for a given symbol.
    :param symbol: Stock symbol (e.g., 'AAPL')
    :param expiration_date: Expiration date in 'YYYY-MM-DD' format (optional)
    :param option_type: 'call' or 'put'
    :return: List of options contracts with market data
    """
    # Get all expiration dates if not specified
    if not expiration_date:
        dates = r.options.get_chains(symbol)['expiration_dates']
    else:
        dates = [expiration_date]

    options_data = []
    for date in dates:
        options = r.options.find_options_by_expiration(symbol, date, optionType=option_type)
        for option in options:
            options_data.append({
                "symbol": symbol,
                "expiration_date": date,
                "strike_price": float(option['strike_price']),
                "option_type": option_type,
                "bid_price": float(option['bid_price']) if option['bid_price'] else None,
                "ask_price": float(option['ask_price']) if option['ask_price'] else None,
                "last_trade_price": float(option['last_trade_price']) if option['last_trade_price'] else None,
                "implied_volatility": float(option['implied_volatility']) if option['implied_volatility'] else None,
                "delta": float(option['delta']) if option['delta'] else None,
                "gamma": float(option['gamma']) if option['gamma'] else None,
                "theta": float(option['theta']) if option['theta'] else None,
                "vega": float(option['vega']) if option['vega'] else None,
                "rho": float(option['rho']) if option['rho'] else None,
                "updated_at": datetime.now().isoformat()
            })
    return options_data

if __name__ == "__main__":
    login_robinhood()
    symbol = "AAPL"  # Example symbol
    options = get_live_options_data(symbol)
    for opt in options[:5]:  # Print first 5 options for brevity
        print(opt)
    r.logout()