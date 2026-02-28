import asyncio
from src.market_data.application.crawler.crawl_company_name import CrawlCompanyName


async def main():
    crawler = CrawlCompanyName(headless=False)  # headless=False để mở cửa sổ browser
    await crawler.run("https://simplize.vn/co-phieu")


if __name__ == "__main__":
    asyncio.run(main())