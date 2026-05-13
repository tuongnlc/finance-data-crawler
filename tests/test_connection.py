import asyncio
from sqlalchemy import text
from src.shared.infrastructure.db.connection import async_session_scope

from dotenv import load_dotenv 

load_dotenv()  

async def test_scope():
    print("--- Test với async_session_scope ---")
    try:
        async for db in async_session_scope():
            result = await db.execute(text("SELECT now();"))
            time = result.scalar_one()
            print(f"✅ Database Time: {time}")
    except Exception as e:
        print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    asyncio.run(test_scope())