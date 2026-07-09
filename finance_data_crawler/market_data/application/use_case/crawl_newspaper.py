from typing import Any
from urllib.parse import urlparse
from finance_data_crawler.market_data.application.ports.crawl_data_port import CrawlDataPort
from finance_data_crawler.market_data.domain.repository import NewspaperRepositoryProtocol
from finance_data_crawler.market_data.domain.repository import NewspaperUrlRepositoryProtocol

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
            newspaper_title = newspaper['newspaper_title']
            newspaper_url = newspaper['newspaper_url']
            publish_date = newspaper['publish_date'].date() if newspaper['publish_date'] else None
            newspaper_content = newspaper['newspaper_content']
            newspaper_summary = newspaper['newspaper_summary']
            is_load_to_qdrant = 0
            created_at = datetime.now().date()

            await self.loader.upsert_by_newspaper_url(
                newspaper_title=newspaper_title,
                newspaper_url=newspaper_url,
                publish_date=publish_date,
                newspaper_content=newspaper_content,
                newspaper_summary=newspaper_summary,
                is_load_to_qdrant=is_load_to_qdrant,
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
