import asyncio
from dotenv import load_dotenv
from src.market_data.application.crawler.crawl_company_name import CrawlCompanyName
from src.market_data.application.use_case.crawl_company_name import CrawlCompanyNameUseCase
from src.market_data.infrastructure.persistence.postgresql import CompanyNameRepository
from src.shared.infrastructure.db.connection import async_session_scope, get_async_engine
from src.shared.infrastructure.db.models import Base


async def main():
    load_dotenv()
    engine = get_async_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    crawler = CrawlCompanyName(headless=False)
    async for db in async_session_scope():
        repo = CompanyNameRepository(session=db)
        use_case = CrawlCompanyNameUseCase(crawler, repo)
        result = await use_case.execute("https://simplize.vn/co-phieu")
        print(result)

if __name__ == "__main__":
    asyncio.run(main())
