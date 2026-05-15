from typing import Any
from urllib.parse import urlparse
from src.market_data.application.ports.crawl_data_port import CrawlDataPort
from src.market_data.domain.repository import NewspaperRepositoryProtocol
from src.market_data.domain.repository import NewspaperUrlRepositoryProtocol

from datetime import datetime


class CrawlNewspaperUseCase:
    def __init__(self, 
            extractor: NewspaperUrlRepositoryProtocol,
            crawler: CrawlDataPort, 
            loader: NewspaperRepositoryProtocol
        ):
        self.extractor = extractor
        self.crawler = crawler
        self.loader = loader

    async def query_newspaper_url(self):
        newspaper_urls = await self.extractor.query_urls_by_is_crawled()
        return newspaper_urls

    async def execute(self) -> None:

        newspaper_urls = await self.query_newspaper_url()
        
        if len(newspaper_urls) == 0:
            print("No new url to crawl")
            return

        for url in newspaper_urls:
            print(f"Crawling: {url}")
            print(" ")
            newspaper = self.crawler.extract(link=url)

            print(f"Done crawl {url}")
            print(" ")
            newspaper_title = newspaper['title']
            newspaper_url = newspaper['url']
            publish_date = newspaper['publish_date'].date() if newspaper['publish_date'] else None
            newspaper_content = newspaper['content']
            newspaper_summary = newspaper['summary']
            is_embedded = 0
            created_at = datetime.now().date()

            await self.loader.upsert_by_newspaper_url(
                title=newspaper_title,
                url=newspaper_url,
                publish_date=publish_date,
                content=newspaper_content,
                summary=newspaper_summary,
                is_embedded=is_embedded,
                created_at=created_at,
            )
            print(f"Done load {url} to postgres")
            print(" ")

            #Upsert is_crawled to 1
            await self.extractor.upsert_by_newspaper_url(
                newspaper_url=url,
                is_crawled=1,
            )
            print(f"Done update is_crawled to 1 for {url}")
