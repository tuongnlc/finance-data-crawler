import asyncio
from dotenv import load_dotenv
from src.market_data.application.crawler.crawl_fund_gav import CrawlFundGav
from src.market_data.application.use_case.crawl_fund_gav import CrawlFundGavUseCase
from src.market_data.infrastructure.persistence.postgresql import FundGavRepository
from src.shared.infrastructure.db.connection import async_session_scope, get_async_engine
from src.shared.infrastructure.db.models import Base


async def main():
    load_dotenv()
    engine = get_async_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    crawler = CrawlFundGav(headless=False)
    async for db in async_session_scope():
        loader = FundGavRepository(session=db)
        use_case = CrawlFundGavUseCase(crawler, loader)
        result = await use_case.execute("https://fmarket.vn/trade/account/investor/market/fund")
        print(result)

if __name__ == "__main__":
    asyncio.run(main())
