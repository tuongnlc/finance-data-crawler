# Step 1: Crawl data
# Step 2: Save to postgres db



import asyncio
from typing import Any
from finance_data_crawler.market_data.domain.repository import CompanyNameRepositoryProtocol
from finance_data_crawler.market_data.application.ports.crawl_data_port import CrawlDataPort


class CrawlCompanyNameUseCase:
    def __init__(self, crawler: CrawlDataPort, loader: CompanyNameRepositoryProtocol):
        self.crawler = crawler
        self.loader = loader

    async def execute(self, link: str, **kwargs: Any) -> dict[str, int]:
        pages = 0
        created = 0
        processed = 0
        seen: set[str] = set()
        db_timeout: float = float(kwargs.pop("db_timeout", 10.0))

        async for batch in self.crawler.crawl_pages(link, **kwargs):
            pages += 1
            for item in batch or []:
                stock_id = (item or {}).get("stock_id")
                company_name = (item or {}).get("company_name")
                business_sector = (item or {}).get("business_sector") or (item or {}).get("Sector")
                capitalization = (item or {}).get("capitalization")

                if not stock_id or not company_name or not business_sector:
                    continue
                if stock_id in seen:
                    continue
                seen.add(stock_id)

                try:
                    existing = await asyncio.wait_for(
                        self.loader.get_by_stock_id(stock_id), timeout=db_timeout
                    )
                    if not existing:
                        await asyncio.wait_for(
                            self.loader.create(
                                stock_id=stock_id,
                                company_name=company_name,
                                business_sector=business_sector,
                                capitalization=capitalization,
                            ),
                            timeout=db_timeout,
                        )
                        created += 1
                    processed += 1
                except Exception:
                    continue
            try:
                session = getattr(self.loader, "session", None)
                if session is not None:
                    await session.commit()
            except Exception:
                pass
        return {"pages": pages, "created": created, "processed": processed}
    
    
