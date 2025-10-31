"""Secure portfolio sync to Notion with proper credential management."""
import robin_stocks.robinhood as r
from notion_client import Client
from datetime import datetime
import logging
from typing import List, Dict
from config import config

logger = logging.getLogger(__name__)

class PortfolioSync:
    """Syncs Robinhood portfolio to Notion database."""
    
    def __init__(self):
        self.notion_client = None
        self.robinhood_logged_in = False
    
    def initialize(self) -> bool:
        """Initialize connections with proper error handling."""
        try:
            # Validate configuration
            if not config.validate():
                logger.error("Configuration validation failed")
                return False
            
            # Check Notion credentials
            if not config.NOTION_API_KEY or not config.NOTION_DATABASE_ID:
                logger.error("Notion credentials missing")
                return False
            
            # Login to Robinhood using config
            logger.info("Logging into Robinhood...")
            login_response = r.login(
                config.ROBINHOOD_USERNAME,
                config.ROBINHOOD_PASSWORD
            )
            
            if login_response:
                self.robinhood_logged_in = True
                logger.info("✅ Successfully logged into Robinhood")
            else:
                logger.error("❌ Failed to login to Robinhood")
                return False
            
            # Initialize Notion client
            logger.info("Initializing Notion client...")
            self.notion_client = Client(auth=config.NOTION_API_KEY)
            logger.info("✅ Successfully initialized Notion client")
            
            return True
            
        except Exception as e:
            logger.error(f"Initialization failed: {str(e)}")
            return False
    
    def get_robinhood_positions(self) -> List[Dict]:
        """Fetch current positions from Robinhood."""
        try:
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
                
                logger.info(f"Position: {symbol} - {position['quantity']} @ ${position['average_buy_price']:.2f}")
            
            return formatted_positions
            
        except Exception as e:
            logger.error(f"Error fetching positions: {str(e)}")
            return []
    
    def update_notion_database(self, positions: List[Dict]) -> bool:
        """Update Notion database with current positions."""
        try:
            database_id = config.NOTION_DATABASE_ID
            
            # Archive existing entries
            logger.info("Archiving existing Notion entries...")
            existing_pages = self.notion_client.databases.query(database_id=database_id)
            
            for page in existing_pages.get('results', []):
                self.notion_client.pages.update(page_id=page['id'], archived=True)
            
            logger.info(f"Archived {len(existing_pages.get('results', []))} entries")
            
            # Add new entries
            logger.info(f"Adding {len(positions)} new positions...")
            for position in positions:
                self.notion_client.pages.create(
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
            
            logger.info("✅ Successfully updated Notion database")
            return True
            
        except Exception as e:
            logger.error(f"Error updating Notion: {str(e)}")
            return False
    
    def run(self) -> None:
        """Main execution function."""
        try:
            logger.info("="*50)
            logger.info("Portfolio Sync to Notion")
            logger.info("="*50)
            
            # Initialize
            if not self.initialize():
                logger.error("Failed to initialize")
                return
            
            # Get positions
            logger.info("\nFetching Robinhood positions...")
            positions = self.get_robinhood_positions()
            
            if not positions:
                logger.warning("No positions found")
                return
            
            logger.info(f"\nFound {len(positions)} positions")
            
            # Update Notion
            logger.info("\nUpdating Notion database...")
            success = self.update_notion_database(positions)
            
            if success:
                logger.info("\n✅ Portfolio sync completed successfully!")
            else:
                logger.error("\n❌ Portfolio sync failed")
            
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
        
        finally:
            # Cleanup
            if self.robinhood_logged_in:
                logger.info("\nLogging out from Robinhood...")
                r.logout()

if __name__ == "__main__":
    sync = PortfolioSync()
    sync.run()