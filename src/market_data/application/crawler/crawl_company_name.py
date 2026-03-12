from typing import Any, AsyncIterator

from src.shared.application.crawler.base import BasePlaywrightCrawler


class CrawlCompanyName(BasePlaywrightCrawler):
    def __init__(self, headless: bool = True) -> None:
        super().__init__(headless=headless)
        self.scroll_limit = 42

    async def handle_popup(self) -> None:
        try:
            await self.page.wait_for_timeout(1000)
            await self.page.wait_for_selector("#is63", timeout=5000)
            try:
                await self.page.click("button.simplize-dialog-close", timeout=5000)
            except Exception:
                close_candidate = self.page.locator(
                    "#is63 button, #is63 [role='button'], #is63 [class*='close'], #is63 [class*='Close']"
                )
                if await close_candidate.count() > 0:
                    await close_candidate.first.click()
        except Exception:
            return

    async def scroll_page(self) -> None:
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

    async def click_to_next_button(self) -> None:
        next_button = self.page.locator("li.simplize-pagination-next")
        await next_button.click()

    async def _extract_single_page(self) -> list[dict[str, Any]]:
        stocks_data = await self.page.evaluate(
            """
            () => {
            const rows = document.querySelectorAll('tr.simplize-table-row');
            return Array.from(rows).map(row => {
                const stockId = row.querySelector('.css-8llhbn')?.innerText.trim();
                const companyName = row.querySelector('.css-skycj1')?.getAttribute('title') || 
                                    row.querySelector('.css-skycj1')?.innerText.trim();
                const cells = row.querySelectorAll('td.simplize-table-cell');
                const capitalization = cells[cells.length - 7]?.innerText.trim();
                const sector = cells[cells.length - 1]?.innerText.trim();
                

                return {
                    stock_id: stockId,
                    company_name: companyName,
                    capitalization: capitalization,
                    business_sector: sector,
                };
            });
            }
            """
        )
        return stocks_data

    async def crawl_pages(self, link: str, **kwargs: Any) -> AsyncIterator[list[dict[str, Any]]]:
        await self._init_crawler()
        try:
            await self.page.goto(link, wait_until="domcontentloaded", timeout=self.navigation_timeout_ms)
            await self.page.wait_for_timeout(2000)
            await self.handle_popup()

            for _ in range(self.scroll_limit):
                await self.scroll_page()
                await self.page.wait_for_timeout(3000)
                await self.page.wait_for_selector("tr.simplize-table-row")
                items = await self._extract_single_page()

                # convert capitalization to int: 1,125,080T to 1125080
                for item in items:
                    if item["capitalization"]:
                        item["capitalization"] = int(item["capitalization"].replace(",", "").replace("T", ""))
                print(items)
                yield items
                await self.page.wait_for_timeout(1500)

                try:
                    await self.click_to_next_button()
                    await self.page.wait_for_timeout(1500)
                except Exception:
                    break
        finally:
            await self._close_crawler()

    async def crawl(self, link: str, **kwargs: Any) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        async for batch in self.crawl_pages(link, **kwargs):
            results.extend(batch)
        return results

    async def extract(self, link: str, **kwargs: Any) -> list[dict[str, Any]]:
        return await self.crawl(link, **kwargs)
