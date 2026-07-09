from finance_data_crawler.shared.application.crawler.base import BasePlaywrightCrawler
from typing import Any, Callable, ClassVar, TypeVar
from finance_data_crawler.market_data.application.crawler.finance_statement_factory.crawl_finance_income_type_one import CrawlIncomeStatementTypeOne
from finance_data_crawler.market_data.application.crawler.finance_statement_factory.crawl_finance_income_type_four import CrawlIncomeStatementTypeFour   
from finance_data_crawler.market_data.application.crawler.finance_statement_factory.crawl_balance_sheet_type_one import CrawlBalanceSheetTypeOne
from finance_data_crawler.market_data.application.crawler.finance_statement_factory.crawl_balance_sheet_type_four import CrawlBalanceSheetTypeFour
from finance_data_crawler.market_data.application.crawler.finance_statement_factory.crawl_cash_flow_statement_type_one import CrawlCashFlowStatementTypeOne
from finance_data_crawler.market_data.application.crawler.finance_statement_factory.crawl_cash_flow_statement_type_four import CrawlCashFlowStatementTypeFour
from finance_data_crawler.market_data.application.crawler.finance_statement_factory.crawl_financial_statistics_overview_type_four import CrawlFinancialStatisticsOverviewTypeFour
from finance_data_crawler.market_data.application.crawler.finance_statement_factory.crawl_financial_statistics_overview_type_one import CrawlFinancialStatisticsOverviewTypeOne



TProduct = TypeVar("TProduct", bound=BasePlaywrightCrawler)

class CrawlFinanceStatementFactory:
    _registry: ClassVar[dict[str, Callable[[bool], BasePlaywrightCrawler]]] = {
        "income_statement_type_one": lambda headless: CrawlIncomeStatementTypeOne(headless=headless),
        "income_statement_type_four": lambda headless: CrawlIncomeStatementTypeFour(headless=headless),
        "balance_sheet_type_one": lambda headless: CrawlBalanceSheetTypeOne(headless=headless),
        "balance_sheet_type_four": lambda headless: CrawlBalanceSheetTypeFour(headless=headless),
        "cash_flow_statement_type_one": lambda headless: CrawlCashFlowStatementTypeOne(headless=headless),
        "cash_flow_statement_type_four": lambda headless: CrawlCashFlowStatementTypeFour(headless=headless),
        "financial_statistics_overview_type_four": lambda headless: CrawlFinancialStatisticsOverviewTypeFour(headless=headless),
        "financial_statistics_overview_type_one": lambda headless: CrawlFinancialStatisticsOverviewTypeOne(headless=headless),
    }

    @classmethod
    def register(cls, crawler_type: str, builder: Callable[[bool], TProduct]) -> None:
        if not crawler_type:
            raise ValueError("crawler_type must be a non-empty string")
        cls._registry[crawler_type] = builder

    @classmethod
    def create(cls, crawler_type: str, *, headless: bool = True) -> BasePlaywrightCrawler:
        try:
            builder = cls._registry[crawler_type]
        except KeyError as e:
            raise ValueError(f"Unsupported crawler_type={crawler_type}. Supported={list(cls._registry)}") from e
        return builder(headless)
