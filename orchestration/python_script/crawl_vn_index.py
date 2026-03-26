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

from src.market_data.application.crawler.crawl_vn_index import CrawlVnIndex
from src.market_data.application.use_case.crawl_vn_index import CrawlVnIndexUseCase
from src.market_data.infrastructure.persistence.postgresql.vn_index_repository import VNIndexRepository


async def run_crawl_vn_index(
    crawl_page_url: str = "https://simplize.vn/chi-so/VNINDEX/lich-su-gia", 
    conn_id: str = None):

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

    engine = get_async_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

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
