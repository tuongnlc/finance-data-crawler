from finance_data_crawler.market_data.application.use_case.crawl_fund_gav import CrawlFundGavUseCase
from finance_data_crawler.market_data.application.crawler.crawl_fund_gav import CrawlFundGav
from finance_data_crawler.market_data.infrastructure.persistence.postgresql.fund_gav_repository import FundGavRepository
import asyncio

from dotenv import load_dotenv  # thêm

load_dotenv()

crawler = CrawlFundGav(
    headless=False,
)
loader = FundGavRepository()


fund_gav_crawler = CrawlFundGavUseCase(
    crawler=crawler,
    loader=loader,
)


async def main():
    await fund_gav_crawler.execute(
        link="https://fmarket.vn/trade/account/investor/market/fund",
    )

if __name__ == "__main__":
    asyncio.run(main())