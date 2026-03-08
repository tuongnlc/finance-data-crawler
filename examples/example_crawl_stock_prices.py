import asyncio
import sys
import argparse
from pathlib import Path

# Add project root to sys.path if running as script
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
from src.shared.infrastructure.db.connection import async_session_scope, get_async_engine
from src.shared.infrastructure.db.models import Base

from src.market_data.application.crawler.crawl_stock_price import CrawlStockPrice
from src.market_data.application.use_case.crawl_stock_price import CrawlStockPriceUseCase
from src.market_data.infrastructure.persistence.postgresql import StockPriceRepository
from src.shared.utils.load_yaml_config import load_config


async def main():
    parser = argparse.ArgumentParser(description="Crawl stock prices based on config.")
    parser.add_argument("--url", type=str, help="Path to the configuration YAML file", default="configs/crawl_stock_price.yaml")
    args = parser.parse_args()

    load_dotenv()
    
    config_path = Path(args.url)
    if not config_path.exists():
        # Try finding it in configs directory relative to project root
        potential_path = PROJECT_ROOT / "configs" / args.url
        if potential_path.exists():
            config_path = potential_path
            
    print(f"Loading config from: {config_path}")
    config = load_config(config_path)
    
    engine = get_async_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    crawler = CrawlStockPrice(headless=False)
    async for db in async_session_scope():
        loader = StockPriceRepository(session=db)
        use_case = CrawlStockPriceUseCase(crawler, loader)
        
        urls = config.get("urls", [])
        for url in urls:
            print(f"Crawling: {url}")
            result = await use_case.execute(url)
            print(result)

if __name__ == "__main__":
    asyncio.run(main())
