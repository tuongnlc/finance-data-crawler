from typing import Any
from finance_data_crawler.shared.application.crawler.base import BasePlaywrightCrawler


class CrawlStockIndex(BasePlaywrightCrawler):
    def __init__(self, headless: bool = True) -> None:
        super().__init__(headless=headless)

    async def crawl_pages(
            self, 
            link: str,
            **kwargs: Any
        ) -> list[dict[str, Any]]:
        
        await self._init_crawler()
        try:
            await self.page.goto(link, wait_until="domcontentloaded", timeout=self.navigation_timeout_ms)
            await self.page.wait_for_timeout(2000)

            # Wait for table rows to appear
            await self.page.wait_for_selector("tr.simplize-table-row")
            
            # Use a dictionary to store unique records by date
            stock_index = []

            scrollable_div = self.page.locator(".simplize-table-body")
            has_scrollable = await scrollable_div.count() > 0
            print(f"Scrollable div found: {has_scrollable}")

            rows = self.page.locator("tr.simplize-table-row")
            count = await rows.count()
            for i in range(count):
                row = rows.nth(i)
                cells = row.locator("td")
                
                # Check if we have enough cells
                date_text = await cells.nth(0).inner_text()
                date_text = date_text.strip()
                
                # Only process if we haven't seen this date
                if 'VNINDEX' in link:
                    if date_text not in stock_index:
                        open_index_value = await cells.nth(3).inner_text()
                        highest_index_value = await cells.nth(4).inner_text()
                        lowest_index_value = await cells.nth(5).inner_text()
                        close_index_value = await cells.nth(6).inner_text()
                        volume_text = await cells.nth(8).inner_text()
                        
                        record = {
                            "trading_date": date_text,
                            "open_index_value": open_index_value.strip(),
                            "highest_index_value": highest_index_value.strip(),
                            "lowest_index_value": lowest_index_value.strip(),
                            "close_index_value": close_index_value.strip(),
                            "volume": volume_text.strip()
                        }
                        stock_index.append(record)
                else:
                    if date_text not in stock_index:
                        open_index_value = await cells.nth(1).inner_text()
                        highest_index_value = await cells.nth(2).inner_text()
                        lowest_index_value = await cells.nth(3).inner_text()
                        close_index_value = await cells.nth(4).inner_text()
                        volume_text = await cells.nth(6).inner_text()
                        
                        record = {
                            "trading_date": date_text,
                            "open_index_value": open_index_value.strip(),
                            "highest_index_value": highest_index_value.strip(),
                            "lowest_index_value": lowest_index_value.strip(),
                            "close_index_value": close_index_value.strip(),
                            "volume": volume_text.strip()
                        }
                        stock_index.append(record)
            print(stock_index)
            yield stock_index
        finally:
            await self._close_crawler()

    async def extract(self, link: str, **kwargs: Any):
        async for batch in self.crawl_pages(link, **kwargs):
            yield batch