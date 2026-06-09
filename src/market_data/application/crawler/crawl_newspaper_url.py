from typing import Any, AsyncIterator
from src.shared.application.crawler.base import BasePlaywrightCrawler
from playwright.async_api import async_playwright
import asyncio



class CrawlNewspaperUrl(BasePlaywrightCrawler):
    def __init__(self, headless: bool = False):
        super().__init__(headless=headless)

    async def _extract_single_page(self, url: str, page: Any) -> AsyncIterator[dict]:
        async with async_playwright() as p:
            await page.goto(url, wait_until="domcontentloaded")
            await asyncio.sleep(2)   
            
            links = await page.eval_on_selector_all(
                "h2 a, h3 a, h4 a", 
                "elements => elements.map(el => ({text: el.innerText, href: el.href, source: window.location.href}))"
            )
                     
        return links

    async def extract(self, link: str) -> AsyncIterator[dict]:
        newspaper_urls = []
        try:
            newspaper_url = await self._extract_single_page(link, page=self.page)
            newspaper_urls.extend(newspaper_url)
        except Exception as e:
            raise e
        return newspaper_urls

#etst function here 
async def test_crawl_newspaper_url():
    crawler = CrawlNewspaperUrl()
    urls = await crawler.run("https://cafef.vn/thi-truong-chung-khoan.chn")
    # assert len(urls) > 0

if __name__ == "__main__":
    asyncio.run(test_crawl_newspaper_url())
