import asyncio
import sys
import os
import argparse
from pathlib import Path

# Add project root to sys.path if running as script
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
from src.shared.infrastructure.db.connection import async_session_scope, get_async_engine, get_async_session_factory
from src.shared.infrastructure.db.models import Base

from src.market_data.application.crawler.crawl_stock_price import CrawlStockPrice
from src.market_data.application.use_case.crawl_stock_price import CrawlStockPriceUseCase
from src.market_data.infrastructure.persistence.postgresql import StockPriceRepository
from src.shared.utils.load_yaml_config import load_config


async def run_crawl_stock_price(url: str, conn_id: str = None):
    # Explicitly load .env from project root
    env_path = PROJECT_ROOT / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
    else:
        load_dotenv() # Fallback to default search

    if conn_id:
        try:
            from airflow.hooks.base import BaseHook
            print(f"Fetching connection details for {conn_id} from Airflow...")
            conn = BaseHook.get_connection(conn_id)
            
            # Set environment variables from Airflow Connection
            if conn.host:
                os.environ["POSTGRES_HOST"] = conn.host
            if conn.login:
                os.environ["POSTGRES_USER"] = conn.login
            if conn.password:
                os.environ["POSTGRES_PASSWORD"] = conn.password
            if conn.port:
                os.environ["POSTGRES_PORT"] = str(conn.port)
            if conn.schema:
                os.environ["POSTGRES_DB"] = conn.schema
            
            print(f"Updated DB config from Airflow connection: {conn.host}:{conn.port}/{conn.schema}")
            
            # Clear DB connection cache to ensure new settings take effect
            get_async_engine.cache_clear()
            get_async_session_factory.cache_clear()
            
        except ImportError:
            print("Warning: Airflow not installed, skipping connection lookup.")
        except Exception as e:
            print(f"Error fetching connection {conn_id}: {e}")
    
    config_path = Path(url)
    if not config_path.exists():
        # Try finding it in configs directory relative to project root
        potential_path = PROJECT_ROOT / "configs" / url
        if potential_path.exists():
            config_path = potential_path
            
    print(f"Loading config from: {config_path}")
    config = load_config(config_path)
    
    engine = get_async_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    crawler = CrawlStockPrice(headless=True)
    async for db in async_session_scope():
        loader = StockPriceRepository(session=db)
        use_case = CrawlStockPriceUseCase(crawler, loader)
        
        urls = config.get("urls", [])
        for item in urls:
            if isinstance(item, dict):
                for category, url_list in item.items():
                    print(f"Processing category: {category}")
                    for url in url_list:
                        print(f"Crawling: {url}")
                        result = await use_case.execute(url)
                        print(result)
            elif isinstance(item, str):
                print(f"Crawling: {item}")
                result = await use_case.execute(item)
                print(result)

def main(url: str = "crawl_stock_price.yaml", conn_id: str = None):
    asyncio.run(run_crawl_stock_price(url, conn_id))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crawl stock prices based on config.")
    parser.add_argument("--url", type=str, help="Path to the configuration YAML file", default="crawl_stock_price.yaml")
    parser.add_argument("--conn-id", type=str, help="Airflow Connection ID", default=None)
    args = parser.parse_args()
    main(args.url, args.conn_id)
