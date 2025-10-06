import robin_stocks.robinhood as r
from notion_client import Client
from datetime import datetime
import os
from dotenv import load_dotenv
import pandas

load_dotenv()  # Loads variables from .env

username = os.getenv("ROBINHOOD_USERNAME")
password = os.getenv("ROBINHOOD_PASSWORD")

# Robinhood login
login = r.login('username',
                'password')

# Initialize Notion client
notion = Client(auth=os.environ.get("NOTION_API_KEY"))

def get_robinhood_positions():
    """Fetch current positions from Robinhood"""
    positions = r.account.build_holdings()
    formatted_positions = []
    
    for symbol, data in positions.items():
        position = {
            "symbol": symbol,
            "quantity": float(data['quantity']),
            "average_buy_price": float(data['average_buy_price']),
            "equity": float(data['equity']),
            "percent_change": float(data['percent_change']),
            "last_updated": datetime.now().isoformat()
        }
        formatted_positions.append(position)
    
    return formatted_positions

def update_notion_database(positions):
    """Update Notion database with current positions"""
    database_id = os.environ.get("NOTION_DATABASE_ID")
    
    # First, clear existing entries
    existing_pages = notion.databases.query(database_id=database_id)
    for page in existing_pages.get('results', []):
        notion.pages.update(page_id=page['id'], archived=True)
    
    # Add new entries
    for position in positions:
        notion.pages.create(
            parent={"database_id": database_id},
            properties={
                "Symbol": {"title": [{"text": {"content": position["symbol"]}}]},
                "Quantity": {"number": position["quantity"]},
                "Average Buy Price": {"number": position["average_buy_price"]},
                "Equity": {"number": position["equity"]},
                "Percent Change": {"number": position["percent_change"]},
                "Last Updated": {"date": {"start": position["last_updated"]}}
            }
        )

def main():
    try:
        # Get positions from Robinhood
        positions = get_robinhood_positions()
        
        # Update Notion database
        update_notion_database(positions)
        print("Successfully updated Notion database with current positions!")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        # Logout from Robinhood
        r.logout()

if __name__ == "__main__":
    main()
