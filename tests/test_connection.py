import asyncio
from sqlalchemy import text
from finance_data_crawler.shared.infrastructure.db.connection import async_session_scope, get_async_engine
from datetime import datetime
from finance_data_crawler.market_data.infrastructure.persistence.postgresql.newspaper_url_repository import NewspaperUrlRepository
import uuid



from dotenv import load_dotenv 

load_dotenv()  

newspaper_title = "Test Newspaper Title"
newspaper_url = "https://www.test.com"
source = "Test Source"
is_crawled = 0
created_at = datetime.now().date()

async def test_scope():
    print("--- Test với async_session_scope ---")
    try:
        async for db in async_session_scope():
            loader = NewspaperUrlRepository(session=db)
            await loader.upsert_by_newspaper_url(
                id=uuid.uuid4(),
                newspaper_title=newspaper_title,
                newspaper_url=newspaper_url,
                source=source,
                is_crawled=is_crawled,
                created_at=created_at,
            )
            # result = await db.execute(text("SELECT now();"))
            # time = result.scalar_one()
            # print(f"✅ Database Time: {time}")
    except Exception as e:
        print(f"❌ Lỗi: {e}")
    finally:
        await get_async_engine().dispose()

if __name__ == "__main__":
    asyncio.run(test_scope())
