from typing import Any
from finance_data_crawler.shared.application.crawler.base import BasePlaywrightCrawler


class CrawlForeignTrade(BasePlaywrightCrawler):
    def __init__(self, headless: bool = True) -> None:
        super().__init__(headless=headless)

    async def crawl_pages(self, link: str, **kwargs: Any) -> list[dict[str, Any]]:
        await self._init_crawler()
        try:
            await self.page.goto(link, wait_until="domcontentloaded", timeout=self.navigation_timeout_ms)
            await self.page.wait_for_timeout(2000)

            # Wait for table rows to appear
            await self.page.wait_for_selector("tr.simplize-table-row")
            
            # Use a dictionary to store unique records by date
            foreign_trades = []

            rows = self.page.locator("tr.simplize-table-row")
            count = await rows.count()
            for i in range(count):
                row = rows.nth(i)
                cells = row.locator("td")
                
                # Check if we have enough cells
                if await cells.count() >= 8:
                    date_text = await cells.nth(0).inner_text()
                    date_text = date_text.strip()
                    
                    # Only process if we haven't seen this date
                    if date_text not in foreign_trades:
                        foreign_room_text = await cells.nth(1).inner_text()
                        buy_volume_text = await cells.nth(2).inner_text()
                        sell_volume_text = await cells.nth(3).inner_text()
                        
                        record = {
                            "date": date_text,
                            "foreign_room": foreign_room_text.strip(),
                            "buy_volume": buy_volume_text.strip(),
                            "sell_volume": sell_volume_text.strip()
                        }
                        foreign_trades.append(record)
            yield foreign_trades
        finally:
            await self._close_crawler()

    async def extract(self, link: str, **kwargs: Any):
        async for batch in self.crawl_pages(link, **kwargs):
            yield batch