import asyncio
import sys
import argparse
from pathlib import Path

# Add project root to sys.path if running as script
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from finance_data_crawler.shared.infrastructure.db.connection import async_session_scope

from finance_data_crawler.market_data.application.crawler.crawl_newspaper import CrawlNewspaper
from finance_data_crawler.market_data.infrastructure.persistence.postgresql.newspaper_url_repository import NewspaperUrlRepository
from finance_data_crawler.market_data.application.use_case.crawl_newspaper_url import CrawlNewspaperUrlUseCase
from finance_data_crawler.market_data.infrastructure.persistence.postgresql.newspaper_repository import NewspaperRepository
from finance_data_crawler.market_data.application.use_case.crawl_newspaper import CrawlNewspaperUseCase
from dotenv import load_dotenv

load_dotenv()

loader = NewspaperRepository()

async def run_crawler():
    async for db in async_session_scope():
        extractor = NewspaperUrlRepository(session=db)
        loader = NewspaperRepository(session=db)
        crawler = CrawlNewspaper()
        use_case = CrawlNewspaperUseCase(extractor, crawler, loader)
        await use_case.execute()

def main():
    asyncio.run(run_crawler())

if __name__ == "__main__":
    main()