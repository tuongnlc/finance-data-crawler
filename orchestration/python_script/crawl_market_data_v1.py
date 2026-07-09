import asyncio
import sys
import argparse
from pathlib import Path

# Add project root to sys.path if running as script
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from finance_data_crawler.shared.infrastructure.db.connection import async_session_scope

from finance_data_crawler.market_data.application.crawler.crawl_stock_index import CrawlStockIndex
from finance_data_crawler.market_data.application.crawler.crawl_foreign_trade import CrawlForeignTrade
from finance_data_crawler.market_data.application.crawler.crawl_stock_price import CrawlStockPrice
from finance_data_crawler.market_data.infrastructure.persistence.postgresql import ForeignTradeRepository
from finance_data_crawler.market_data.application.use_case.crawl_stock_index import CrawlStockIndexUseCase
from finance_data_crawler.market_data.infrastructure.persistence.postgresql.stock_index_repository import StockIndexRepository
from finance_data_crawler.market_data.infrastructure.persistence.postgresql.stock_price_repository import StockPriceRepository
from finance_data_crawler.market_data.application.use_case.crawl_foreign_trade import CrawlForeignTradeUseCase
from finance_data_crawler.market_data.application.use_case.crawl_stock_price import CrawlStockPriceUseCase
from finance_data_crawler.market_data.application.crawler.crawl_newspaper_url import CrawlNewspaperUrl
from finance_data_crawler.market_data.infrastructure.persistence.postgresql.newspaper_url_repository import NewspaperUrlRepository
from finance_data_crawler.market_data.application.use_case.crawl_newspaper_url import CrawlNewspaperUrlUseCase
from finance_data_crawler.market_data.application.crawler.crawl_newspaper import CrawlNewspaper
from finance_data_crawler.market_data.infrastructure.persistence.postgresql.newspaper_repository import NewspaperRepository
from finance_data_crawler.market_data.application.use_case.crawl_newspaper import CrawlNewspaperUseCase
from finance_data_crawler.market_data.application.crawler.finance_statement_factory.crawl_finance_statement_factory import CrawlFinanceStatementFactory
from finance_data_crawler.market_data.infrastructure.persistence.postgresql.final_statement_repository import FinalStatementRepository
from finance_data_crawler.market_data.application.use_case.crawl_finance_statement import CrawlFinanceStatementUseCase

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
    "newspaper": 
        {
            "crawler": CrawlNewspaper,
            "extractor": NewspaperUrlRepository, #using to read news paper url from newspaper_url table
            "loader": NewspaperRepository,
            "use_case": CrawlNewspaperUseCase,
        },
    "income_statement_type_one": {
        "crawler": lambda headless=True: CrawlFinanceStatementFactory.create("income_statement_type_one", headless=headless),
        "loader": FinalStatementRepository,
        "loader_kwargs": {"model_path": "finance_data_crawler.shared.infrastructure.db.models.IncomeStatementType1"},
        "use_case": CrawlFinanceStatementUseCase,
    },
    "income_statement_type_four": {
        "crawler": lambda headless=True: CrawlFinanceStatementFactory.create("income_statement_type_four", headless=headless),
        "loader": FinalStatementRepository,
        "loader_kwargs": {"model_path": "finance_data_crawler.shared.infrastructure.db.models.IncomeStatementTypeFour"},
        "use_case": CrawlFinanceStatementUseCase,
    },
    "balance_sheet_type_one": {
        "crawler": lambda headless=True: CrawlFinanceStatementFactory.create("balance_sheet_type_one", headless=headless),
        "loader": FinalStatementRepository,
        "loader_kwargs": {"model_path": "finance_data_crawler.shared.infrastructure.db.models.BalanceSheetTypeOne"},
        "use_case": CrawlFinanceStatementUseCase,
    },
    "balance_sheet_type_four": {
        "crawler": lambda headless=True: CrawlFinanceStatementFactory.create("balance_sheet_type_four", headless=headless),
        "loader": FinalStatementRepository,
        "loader_kwargs": {"model_path": "finance_data_crawler.shared.infrastructure.db.models.BalanceSheetTypeFour"},
        "use_case": CrawlFinanceStatementUseCase,
    },
    "cash_flow_statement_type_one": {
        "crawler": lambda headless=True: CrawlFinanceStatementFactory.create("cash_flow_statement_type_one", headless=headless),
        "loader": FinalStatementRepository,
        "loader_kwargs": {"model_path": "finance_data_crawler.shared.infrastructure.db.models.CashFlowStatementTypeOne"},
        "use_case": CrawlFinanceStatementUseCase,
    },
    "cash_flow_statement_type_four": {
        "crawler": lambda headless=True: CrawlFinanceStatementFactory.create("cash_flow_statement_type_four", headless=headless),
        "loader": FinalStatementRepository,
        "loader_kwargs": {"model_path": "finance_data_crawler.shared.infrastructure.db.models.CashFlowStatementTypeFour"},
        "use_case": CrawlFinanceStatementUseCase,
    },
    "financial_statistics_overview_type_four": {
        "crawler": lambda headless=True: CrawlFinanceStatementFactory.create("financial_statistics_overview_type_four", headless=headless),
        "loader": FinalStatementRepository,
        "loader_kwargs": {"model_path": "finance_data_crawler.shared.infrastructure.db.models.FinancialStatisticsOverviewTypeFour"},
        "use_case": CrawlFinanceStatementUseCase,
    },
    "financial_statistics_overview_type_one": {
        "crawler": lambda headless=True: CrawlFinanceStatementFactory.create("financial_statistics_overview_type_one", headless=headless),
        "loader": FinalStatementRepository,
        "loader_kwargs": {"model_path": "finance_data_crawler.shared.infrastructure.db.models.FinancialStatisticsOverviewTypeOne"},
        "use_case": CrawlFinanceStatementUseCase,
    },
}

async def run_crawler(
    url: str,
    conn_id: str = None,
):
    configure_postgres_env_from_airflow_connection(conn_id)
    
    await init_db_schema()

    config = load_yaml_config(url, PROJECT_ROOT)

    data_type = config.get("data_type") #using for finance statement - cause we apply yield for this project
    crawler_type = config.get("kind")

    crawler_cls = CRAWLER_CLASS[crawler_type]["crawler"]
    loader_cls = CRAWLER_CLASS[crawler_type]["loader"]
    use_case_cls = CRAWLER_CLASS[crawler_type]["use_case"]
    loader_kwargs = CRAWLER_CLASS[crawler_type].get("loader_kwargs", {})

    extractor_cls = CRAWLER_CLASS[crawler_type].get("extractor", None) #Using if we need to read data from postgresql
    
    crawler = crawler_cls(headless=True)
    query_to_db = config.get("query_to_db", False)
    
    if query_to_db: #Determine whether dag need too query to db or not
        async for db in async_session_scope():
            extractor = extractor_cls(session=db)
            loader = loader_cls(session=db, **loader_kwargs) if loader_kwargs else loader_cls(session=db)
            use_case = use_case_cls(
                extractor=extractor,
                crawler=crawler,
                loader=loader
            )
            await use_case.execute()
    else:
        async for db in async_session_scope():
            loader = loader_cls(session=db, **loader_kwargs) if loader_kwargs else loader_cls(session=db)
            use_case = use_case_cls(crawler, loader)
            
            urls = config.get("urls", [])
            
            if data_type == "finance_statement":
                result = await use_case.execute(urls)
            else:
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
