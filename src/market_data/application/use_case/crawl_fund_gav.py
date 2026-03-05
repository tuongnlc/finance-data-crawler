import asyncio
from typing import Any
from src.market_data.domain.repository import FundGavRepositoryProtocol
from src.market_data.application.ports.crawl_data_port import CrawlDataPort


class CrawlFundGavUseCase:
    def __init__(self, crawler: CrawlDataPort, loader: FundGavRepositoryProtocol):
        self.crawler = crawler
        self.loader = loader

    async def execute(self, link: str, **kwargs: Any) -> dict[str, int]:
        pages = 0
        created = 0
        processed = 0

        # Xóa dữ liệu cũ trước khi bắt đầu crawl mới (truncate)
        try:
            print("Truncating old data before crawling...")
            await self.loader.delete_all()
            session = getattr(self.loader, "session", None)
            if session is not None:
                await session.commit()
        except Exception as e:
            print(f"Lỗi khi truncate database: {e}")

        async for fund_gavs in self.crawler.crawl_pages(link, **kwargs):
            pages += 1
            if not fund_gavs:
                continue
            
            for fund_gav in fund_gavs:
                try:
                    await self.loader.create(**fund_gav)
                    created += 1
                except Exception as e:
                    print(f"Lỗi khi lưu fund_gav: {e}")
                processed += 1
            
            try:
                session = getattr(self.loader, "session", None)
                if session is not None:
                    await session.commit()
            except Exception as e:
                print(f"Lỗi khi commit: {e}")

        return {"pages": pages, "created": created, "processed": processed}
        
    
    
