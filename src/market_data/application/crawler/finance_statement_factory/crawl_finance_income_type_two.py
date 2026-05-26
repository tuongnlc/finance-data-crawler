from src.shared.application.crawler.base import BasePlaywrightCrawler


class CrawlIncomeStatementTypeTwo(BasePlaywrightCrawler):
    def __init__(self, headless: bool = True) -> None:
        super().__init__(headless=headless)

    async def execute(self):
        pass