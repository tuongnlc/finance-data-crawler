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

    async for db in async_session_scope():
        repo = CompanyNameRepository(session=db)
        
        # Ghi một record
        record = await repo.create(
            id=uuid.uuid4(),
            stock_id="test",
            company_name="test",
            business_sector="test",
        )
        print("Đã ghi record:", record.id, record.stock_id, record.company_name)
        # Commit xảy ra khi thoát async_session_scope() thành công


if __name__ == "__main__":
    asyncio.run(main())
