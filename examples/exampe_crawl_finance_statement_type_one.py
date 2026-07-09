from finance_data_crawler.market_data.application.use_case.crawl_finance_statement import CrawlFinanceStatementUseCase
from finance_data_crawler.market_data.infrastructure.persistence.postgresql.final_statement_repository import FinalStatementRepository


import asyncio
import sys
import argparse
from pathlib import Path

# Add project root to sys.path if running as script
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from finance_data_crawler.shared.infrastructure.db.connection import async_session_scope

from dotenv import load_dotenv

load_dotenv()

from finance_data_crawler.market_data.application.crawler.finance_statement_factory.crawl_finance_statement_factory import CrawlFinanceStatementFactory

async def run_crawler():
    async for db in async_session_scope():
        crawler = CrawlFinanceStatementFactory.create("income_statement_type_one")
        model_path = "finance_data_crawler.shared.infrastructure.db.models.IncomeStatementType1"
        final_repo = FinalStatementRepository(model_path=model_path, session=db)

        use_case = CrawlFinanceStatementUseCase(crawler, final_repo)
        links = [
            "https://fireant.vn/ma-chung-khoan/DBC",
            "https://fireant.vn/ma-chung-khoan/HSG"
        ]
        await use_case.execute(links)

def main():
    asyncio.run(run_crawler())

if __name__ == "__main__":
    main()