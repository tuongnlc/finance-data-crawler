from src.shared.application.crawler.base import BasePlaywrightCrawler
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
import json

class CrawlCompanyName(BasePlaywrightCrawler):
    """Crawler Simplize lấy danh sách company name. Kế thừa BasePlaywrightCrawler."""

    async def handle_popup():
        pass

    async def scroll_page(self):
        await self.page.evaluate(
                """
                () => {
                    const el = document.scrollingElement || document.documentElement || document.body;
                    if (el) {
                        el.scrollTo({ top: 2300, behavior: 'auto' });
                    }
                }
                """
            )

    async def click_to_next_button(self):
        next_button = self.page.locator('li.simplize-pagination-next')
        await next_button.click()

    async def _extract_single_page(self):
        stocks_data = await self.page.evaluate('''() => {
            const rows = document.querySelectorAll('tr.simplize-table-row');
            return Array.from(rows).map(row => {
                // Lấy Stock ID (Mã CP)
                const stockId = row.querySelector('.css-8llhbn')?.innerText.trim();
                
                // Lấy Company Name (Tên công ty - từ attribute title)
                const companyName = row.querySelector('.css-skycj1')?.getAttribute('title') || 
                                    row.querySelector('.css-skycj1')?.innerText.trim();
                
                // Lấy Sector (Cột cuối cùng)
                const cells = row.querySelectorAll('td.simplize-table-cell');
                const sector = cells[cells.length - 1]?.innerText.trim();

                return {
                    "stock_id": stockId,
                    "company_name": companyName,
                    "Sector": sector
                };
            });
        }''')
        print(stocks_data)
        return stocks_data

    async def extract(self, link: str, **kwargs) -> list[dict]:
        # Step 1: Load page
        await self.page.goto(link, wait_until="domcontentloaded", timeout=30000)

        for i in range(5):
            # Step 2: Scroll page
            try:
                print(f"Crawl page {i}")
                await self.scroll_page()
                await self.page.wait_for_timeout(3000)
                
                # Step 3: extract data in json format
                await self.page.wait_for_selector('tr.simplize-table-row')
                await self._extract_single_page()
                await self.page.wait_for_timeout(3000)

                # Step 4: Click to next_button
                await self.click_to_next_button()
            except:
                if i == 41:
                    print("Reach the end of the page")
                else:
                    raise "error crawl page" 

        
