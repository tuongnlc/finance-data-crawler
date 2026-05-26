from src.shared.application.crawler.base import BasePlaywrightCrawler
from typing import Any, Callable, ClassVar, TypeVar
from src.market_data.application.crawler.finance_statement_factory.crawl_finance_income_type_one import CrawlIncomeStatementTypeOne
from src.market_data.application.crawler.finance_statement_factory.crawl_finance_income_type_two import CrawlIncomeStatementTypeTwo



TProduct = TypeVar("TProduct", bound=BasePlaywrightCrawler)

class CrawlFinanceStatementFactory:
    _registry: ClassVar[dict[str, Callable[[bool], BasePlaywrightCrawler]]] = {
        "income_statement_type_one": lambda headless: CrawlIncomeStatementTypeOne(headless=headless),
        "income_statement_type_two": lambda headless: CrawlIncomeStatementTypeTwo(headless=headless),
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
