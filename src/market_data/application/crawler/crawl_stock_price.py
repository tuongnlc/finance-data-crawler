from typing import Any
from src.shared.application.crawler.base import BasePlaywrightCrawler


class CrawlStockPrice(BasePlaywrightCrawler):
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
            stock_prices = []

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
                    if date_text not in stock_prices:
                        open_price_text = await cells.nth(1).inner_text()
                        max_price_text = await cells.nth(2).inner_text()
                        min_price_text = await cells.nth(3).inner_text()
                        close_price_text = await cells.nth(4).inner_text()
                        volume_text = await cells.nth(7).inner_text()
                        
                        record = {
                            "date": date_text,
                            "open_price": open_price_text.strip(),
                            "max_price": max_price_text.strip(),
                            "min_price": min_price_text.strip(),
                            "close_price": close_price_text.strip(),
                            "volume": volume_text.strip()
                        }
                        stock_prices.append(record)
            yield stock_prices
        finally:
            await self._close_crawler()

    async def extract(self, link: str, **kwargs: Any):
        async for batch in self.crawl_pages(link, **kwargs):
            yield batch