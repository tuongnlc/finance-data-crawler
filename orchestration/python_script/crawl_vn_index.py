import asyncio
import sys
import argparse
from pathlib import Path

# Add project root to sys.path if running as script
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.shared.infrastructure.db.connection import async_session_scope

from src.market_data.application.crawler.crawl_vn_index import CrawlVnIndex
from src.market_data.application.use_case.crawl_vn_index import CrawlVnIndexUseCase
from src.market_data.infrastructure.persistence.postgresql.vn_index_repository import VNIndexRepository
from orchestration.python_script.share.postgre_config import (
    configure_postgres_env_from_airflow_connection,
    init_db_schema,
)


async def run_crawl_vn_index(
        crawl_page_url: str = "https://simplize.vn/chi-so/VNINDEX/lich-su-gia", 
        conn_id: str = None
    ):

    configure_postgres_env_from_airflow_connection(conn_id)
    await init_db_schema()


    crawler = CrawlVnIndex(headless=True)
    async for db in async_session_scope():
        loader = VNIndexRepository(session=db)
        use_case = CrawlVnIndexUseCase(crawler, loader)
        
        result = await use_case.execute(crawl_page_url)
        print(result)

def main(conn_id: str = None):
    asyncio.run(run_crawl_vn_index(conn_id=conn_id))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crawl VN Index based on config.")
    parser.add_argument("--conn-id", type=str, help="Airflow Connection ID", default=None)
    args = parser.parse_args()
    main(args.conn_id)
