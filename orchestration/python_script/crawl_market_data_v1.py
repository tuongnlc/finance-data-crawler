import asyncio
import sys
import argparse
from pathlib import Path

# Add project root to sys.path if running as script
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.shared.infrastructure.db.connection import async_session_scope

from src.market_data.application.crawler.crawl_stock_index import CrawlStockIndex
from src.market_data.application.crawler.crawl_foreign_trade import CrawlForeignTrade
from src.market_data.application.crawler.crawl_stock_price import CrawlStockPrice
from src.market_data.infrastructure.persistence.postgresql import ForeignTradeRepository
from src.market_data.application.use_case.crawl_stock_index import CrawlStockIndexUseCase
from src.market_data.infrastructure.persistence.postgresql.stock_index_repository import StockIndexRepository
from src.market_data.infrastructure.persistence.postgresql.stock_price_repository import StockPriceRepository
from src.market_data.application.use_case.crawl_foreign_trade import CrawlForeignTradeUseCase
from src.market_data.application.use_case.crawl_stock_price import CrawlStockPriceUseCase
from src.market_data.application.crawler.crawl_newspaper_url import CrawlNewspaperUrl
from src.market_data.infrastructure.persistence.postgresql.newspaper_url_repository import NewspaperUrlRepository
from src.market_data.application.use_case.crawl_newspaper_url import CrawlNewspaperUrlUseCase



from orchestration.python_script.share.postgre_config import (
    configure_postgres_env_from_airflow_connection,
    init_db_schema,
)
from orchestration.python_script.share.config_loader import load_yaml_config

CRAWLER_CLASS = {
    "stock_index": 
        {
            "crawler": CrawlStockIndex,
            "loader": StockIndexRepository,
            "use_case": CrawlStockIndexUseCase,
        },
    "foreign_trade": 
        {
            "crawler": CrawlForeignTrade,
            "loader": ForeignTradeRepository,
            "use_case": CrawlForeignTradeUseCase,
        },
    "stock_price": 
        {
            "crawler": CrawlStockPrice,
            "loader": StockPriceRepository,
            "use_case": CrawlStockPriceUseCase,
        },
    "newspaper_url": 
        {
            "crawler": CrawlNewspaperUrl,
            "loader": NewspaperUrlRepository,
            "use_case": CrawlNewspaperUrlUseCase,
        },
    }

async def run_crawler(
    url: str,
    conn_id: str = None,
):
    configure_postgres_env_from_airflow_connection(conn_id)
    
    await init_db_schema()

    config = load_yaml_config(url, PROJECT_ROOT)

    crawler_type = config.get("kind")

    crawler_cls = CRAWLER_CLASS[crawler_type]["crawler"]
    loader_cls = CRAWLER_CLASS[crawler_type]["loader"]
    use_case_cls = CRAWLER_CLASS[crawler_type]["use_case"]

    crawler = crawler_cls(headless=True)

    async for db in async_session_scope():
        loader = loader_cls(session=db)
        use_case = use_case_cls(crawler, loader)
        
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

def main(url: str, conn_id: str = None):
    asyncio.run(run_crawler(url=url, conn_id=conn_id))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crawl stock prices based on config.")
    parser.add_argument("--url", type=str, help="Path to the configuration YAML file")
    parser.add_argument("--conn-id", type=str, help="Airflow Connection ID", default=None)
    args = parser.parse_args()
    main(args.url, args.conn_id)
