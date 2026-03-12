from typing import Any, AsyncIterator
from src.shared.application.crawler.base import BasePlaywrightCrawler
import asyncio



class CrawlStockPrice(BasePlaywrightCrawler):
    def __init__(self, headless: bool = True) -> None:
        super().__init__(headless=headless)

    async def extract(self, link: str, **kwargs: Any) -> list[dict[str, Any]]:
        await self._init_crawler()
        try:
            await self.page.goto(link, wait_until="domcontentloaded", timeout=self.navigation_timeout_ms)
            await self.page.wait_for_timeout(2000)

            # Wait for table rows to appear
            await self.page.wait_for_selector("tr.simplize-table-row")
            
            # Use a dictionary to store unique records by date
            data = []
            
            # Locate the scrollable container (table body)
            scrollable_div = self.page.locator(".simplize-table-body")
            has_scrollable = await scrollable_div.count() > 0
            print(f"Scrollable div found: {has_scrollable}")

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
                    if date_text not in data:
                        open_price_text = await cells.nth(1).inner_text()
                        max_price_text = await cells.nth(2).inner_text()
                        min_price_text = await cells.nth(3).inner_text()
                        
                        
                        record = {
                            "date": date_text,
                            "foreign_room": open_price_text.strip(),
                            "buy_volume": max_price_text.strip(),
                            "sell_volume": min_price_text.strip()
                        }
                        data.append(record)
                print(data)
            return data
        finally:
            await self._close_crawler()

test_crawler = CrawlStockPrice(
    headless=True,
)

test_link = "https://simplize.vn/co-phieu/VCB/lich-su-gia#giao-dich-nha-dau-tu-nuoc-ngoai"

async def test_extract():
    data = await test_crawler.extract(test_link)
    print(f"Extracted {len(data)} records")
    
if __name__ == "__main__":
    asyncio.run(test_extract())