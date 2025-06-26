
# Robinhood_Crypto

This project provides tools for managing and automating cryptocurrency trading and portfolio tracking using Robinhood, Binance, and Notion.

## Features

- **Automated Crypto Trading**  
  The [`auto_trade.py`](auto_trade.py) script connects to both Robinhood and Binance. It monitors the price of BTC and automatically buys or sells on Robinhood based on real-time Binance prices and your last buy price.

- **Portfolio Sync to Notion**  
  The [`main.py`](main.py) script fetches your current Robinhood positions and updates a Notion database with your holdings, including symbol, quantity, average buy price, equity, percent change, and last updated time.

## Setup

1. **Install dependencies:**
    pip install -r requirements.txt

2. **Configure credentials:**
- For Robinhood and Binance, update the placeholders in [`auto_trade.py`](auto_trade.py) with your credentials.
- For Notion, set the `NOTION_API_KEY` and `NOTION_DATABASE_ID` environment variables.

3. **Run scripts:**
- To sync your Robinhood portfolio to Notion:
  ```
  python [main.py](http://_vscodecontentref_/1)
  ```
- To start automated trading:
  ```
  python [auto_trade.py](http://_vscodecontentref_/2)
  ```

## Files

- [`main.py`](main.py): Syncs Robinhood portfolio to Notion.
- [`auto_trade.py`](auto_trade.py): Automated trading bot for Robinhood using Binance prices.
- [`requirements.txt`](requirements.txt): Python dependencies.
- [`README.md`](README.md): Project documentation.

**Note:**  
Credentials are currently hardcoded in the scripts. For security, consider using environment variables or a `.env` file for all sensitive information.