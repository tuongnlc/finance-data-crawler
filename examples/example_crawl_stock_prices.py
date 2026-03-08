import asyncio
from dotenv import load_dotenv
from src.shared.infrastructure.db.connection import async_session_scope, get_async_engine
from src.shared.infrastructure.db.models import Base

from src.market_data.application.crawler.crawl_stock_price import CrawlStockPrice
from src.market_data.application.use_case.crawl_stock_price import CrawlStockPriceUseCase
from src.market_data.infrastructure.persistence.postgresql import StockPriceRepository


async def main():
    load_dotenv()
    engine = get_async_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    crawler = CrawlStockPrice(headless=False)
    async for db in async_session_scope():
        loader = StockPriceRepository(session=db)
        use_case = CrawlStockPriceUseCase(crawler, loader)
        result = await use_case.execute("https://simplize.vn/co-phieu/TCB/lich-su-gia")
        print(result)

if __name__ == "__main__":
    asyncio.run(main())
