import asyncio
import sys
import argparse
from pathlib import Path

# Add project root to sys.path if running as script
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
from src.shared.infrastructure.db.connection import async_session_scope

from src.market_data.application.crawler.crawl_foreign_trade import CrawlForeignTrade
from src.market_data.application.use_case.crawl_foreign_trade import CrawlForeignTradeUseCase
from src.market_data.infrastructure.persistence.postgresql import ForeignTradeRepository
from orchestration.python_script.share.postgre_config import (
    configure_postgres_env_from_airflow_connection,
    init_db_schema,
)
from orchestration.python_script.share.config_loader import load_yaml_config

async def run_crawl_foreign_trade(url: str, conn_id: str = None):
    # Explicitly load .env from project root
    env_path = PROJECT_ROOT / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
    else:
        load_dotenv() # Fallback to default search

    configure_postgres_env_from_airflow_connection(conn_id)
    await init_db_schema()

    config = load_yaml_config(url, PROJECT_ROOT)


    crawler = CrawlForeignTrade(headless=True)
    async for db in async_session_scope():
        loader = ForeignTradeRepository(session=db)
        use_case = CrawlForeignTradeUseCase(crawler, loader)
        
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

def main(url: str = "crawl_foreign_trade.yaml", conn_id: str = None):
    asyncio.run(run_crawl_foreign_trade(url, conn_id))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crawl foreign trade based on config.")
    parser.add_argument("--url", type=str, help="Path to the configuration YAML file", default="crawl_foreign_trade.yaml")
    parser.add_argument("--conn-id", type=str, help="Airflow Connection ID", default=None)
    args = parser.parse_args()
    main(args.url, args.conn_id)
