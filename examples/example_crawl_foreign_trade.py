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

from src.market_data.application.crawler.crawl_foreign_trade import CrawlForeignTrade
from src.shared.utils.load_yaml_config import load_config
from src.market_data.application.use_case.crawl_foreign_trade import CrawlForeignTradeUseCase
from src.market_data.infrastructure.persistence.postgresql import ForeignTradeRepository



async def main():
    parser = argparse.ArgumentParser(description="Crawl foreign trade based on config.")
    parser.add_argument("--url", type=str, help="Path to the configuration YAML file", default="configs/crawl_foreign_trade.yaml")
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
    
    crawler = CrawlForeignTrade(headless=False)
    async for db in async_session_scope():
        loader = ForeignTradeRepository(session=db)
        use_case = CrawlForeignTradeUseCase(crawler, loader)    
        
        urls = config.get("urls", [])
        for url in urls:
            print(f"Crawling: {url}")
            result = await use_case.execute(url)
            print(result)

if __name__ == "__main__":
    asyncio.run(main())
