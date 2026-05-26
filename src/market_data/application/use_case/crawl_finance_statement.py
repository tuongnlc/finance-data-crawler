# from market_data.application.crawler.finance_statement_factory.crawl_finance_statement_factory import CrawlFinanceStatementFactory
from src.market_data.domain.repository import FinanceStatementRepositoryProtocol
from src.market_data.application.ports.crawl_data_port import CrawlDataPort


class CrawlFinanceStatementUseCase:
    def __init__(self,
        crawler: CrawlDataPort,
        loader: FinanceStatementRepositoryProtocol,
    ):
        self.crawler = crawler
        self.loader = loader

    async def execute(self, links: list[str]):
        # link_list = [links] if isinstance(links, str) else links
        async for batch in self.crawler.extract(links):
            for item in batch:
                await self.loader.upsert_by_year_quarter_stock_id(
                    year=item["year"],
                    quarter=item["quarter"],
                    stock_id=item["stock_id"],
                    data=item
                )
