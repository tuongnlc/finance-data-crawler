from typing import Any
from urllib.parse import urlparse
from finance_data_crawler.market_data.application.ports.crawl_data_port import CrawlDataPort
from finance_data_crawler.market_data.domain.repository import NewspaperUrlRepositoryProtocol
from datetime import datetime

import asyncio

class CrawlNewspaperUrlUseCase:
    def __init__(self, 
            crawler: CrawlDataPort, 
            loader: NewspaperUrlRepositoryProtocol
        ):
        self.crawler = crawler
        self.loader = loader

    async def execute(self, link: str) -> None:
        newspaper_urls = await self.crawler.run(link=link)

        #Write data to db
        for url in newspaper_urls:
            newspaper_title = url['text']
            newspaper_url = url['href']
            source = url['source']
            is_crawled = 0
            created_at = datetime.now().date()

            await self.loader.upsert_by_newspaper_url(
                newspaper_title=newspaper_title,
                newspaper_url=newspaper_url,
                source=source,
                is_crawled=is_crawled,
                created_at=created_at,
            )
