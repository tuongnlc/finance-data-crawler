from typing import Any, AsyncIterator
from src.shared.application.crawler.base import BasePlaywrightCrawler
from playwright.async_api import async_playwright
import asyncio



class CrawlNewspaperUrl(BasePlaywrightCrawler):
    def __init__(self, headless: bool = True):
        super().__init__(headless=headless)

    async def _extract_single_page(self, url: str, page: Any) -> AsyncIterator[dict]:
        async with async_playwright() as p:
            # browser = await p.chromium.launch(headless=True)
            # page = await browser.new_page()
            await page.goto(url, wait_until="networkidle")
            
            # Selector này lấy thẻ 'a' nằm trong 'h2' HOẶC 'h3'
            links = await page.eval_on_selector_all(
                "h2 a, h3 a, h4 a", 
                "elements => elements.map(el => ({text: el.innerText, href: el.href}))"
            )            
        return links

    async def extract(self, link: list[str]) -> AsyncIterator[dict]:
        newspaper_urls = []
        try:
            for link in link:
                newspaper_urls.extend(await self._extract_single_page(link, page=self.page))
        except Exception as e:
            raise e
        print(newspaper_urls)
        return newspaper_urls

# #test_class_here
# if __name__ == '__main__':
#     crawler = CrawlNewspaperUrl()
#     asyncio.run(crawler.run(link=['https://vietstock.vn/chung-khoan.htm']))

