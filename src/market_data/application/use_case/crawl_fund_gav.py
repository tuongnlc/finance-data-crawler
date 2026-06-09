from typing import Any
from src.market_data.domain.repository import FundGavRepositoryProtocol
from src.market_data.application.ports.crawl_data_port import CrawlDataPort
from datetime import datetime


class CrawlFundGavUseCase:
    """
        Crawl fund gav from fmarket.vn

        Each month we go to fmarket.vn crawl data then save to database

        Here is the logic to extract data in this month:
        - current_month = datetime.now().month
        - report_month = current_month - 1 

    """
    def __init__(self, crawler: CrawlDataPort, loader: FundGavRepositoryProtocol):
        self.crawler = crawler
        self.loader = loader

    async def execute(self, link: str, **kwargs: Any) -> dict[str, int]:
        pages = 0
        created = 0
        processed = 0

        # Get report month
        current_month = datetime.now().month
        report_month = current_month - 1 

        # Xóa dữ liệu cũ trước khi bắt đầu crawl mới (truncate)
        try:
            print(f"Delete old data before loading month {report_month}...")
            await self.loader.delete_before_load(report_month)
        except Exception as e:
            print(f"Lỗi khi delete old data: {e}")

        async for fund_gavs in self.crawler.crawl_pages(link, **kwargs):
            pages += 1
            if not fund_gavs:
                continue
            
            for fund_gav in fund_gavs:
                # get current month
                fund_gav["month"] = report_month
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

    
