"""
Code mẫu: ghi một record vào PostgreSQL.

Chạy:
  cd /path/to/finance-data-crawler
  python -m examples.insert_one_record

Cần: .env có POSTGRES_* và DB đã chạy. Bảng company_name sẽ được tạo nếu chưa có.
"""
import asyncio
import uuid

from dotenv import load_dotenv

# Load biến môi trường từ file .env (POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, ...)
load_dotenv()

from src.market_data.infrastructure.persistence.postgresql import (
    CompanyNameRepository,
)
from src.shared.infrastructure.db.connection import (
    async_session_scope,
    get_async_engine,
)
from src.shared.infrastructure.db.models import Base


async def main() -> None:
    engine = get_async_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async for db in async_session_scope():
        repo = CompanyNameRepository(session=db)

        # CREATE
        record = await repo.create(
            id=uuid.uuid4(),
            stock_id="VNTEST",
            company_name="Công ty Test",
            business_sector="Công nghệ",
        )
        print("CREATE:", record.id, record.stock_id, record.company_name)

        # READ by id
        got = await repo.get_by_id(record.id)
        print("READ (by id):", got.id if got else None)

        # READ list
        items = await repo.get_all(limit=5)
        print("READ (list):", len(items))

        # UPDATE
        updated = await repo.update(record, company_name="Công ty Đổi Tên")
        print("UPDATE:", updated.company_name)

        # DELETE
        deleted = await repo.delete_by_id(record.id)
        print("DELETE:", deleted)


if __name__ == "__main__":
    asyncio.run(main())
