import asyncio
from typing import Any
from src.market_data.domain.repository import CompanyNameRepositoryProtocol
from src.market_data.application.ports.crawl_data_port import CrawlDataPort


class CrawlStockPriceUseCase:
    def __init__(self, 
            crawler: CrawlDataPort, 
            # loader: CompanyNameRepositoryProtocol
        ):
        self.crawler = crawler
        # self.loader = loader

    async def execute(self, link: str, **kwargs: Any) -> Any:
        return await self.crawler.crawl(link, **kwargs)