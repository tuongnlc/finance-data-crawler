"""
Code mẫu: ghi một record vào PostgreSQL.

Chạy:
  cd /path/to/finance-data-crawler
  python -m examples.insert_one_record

Cần: .env có POSTGRES_* và DB đã chạy. Bảng symbols sẽ được tạo nếu chưa có.
"""
import asyncio
import uuid

from dotenv import load_dotenv

# Load biến môi trường từ file .env (POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, ...)
load_dotenv()

from src.shared.infrastructure.db.connection import (
    async_session_scope,
    get_async_engine,
)
from src.shared.infrastructure.db.models import Base, SymbolModel
from src.shared.infrastructure.persistence.postgresql.repository import (
    BasePostgresRepository,
)


class SymbolRepository(BasePostgresRepository[SymbolModel]):
    model_class = SymbolModel


async def create_tables_if_not_exist() -> None:
    """Tạo bảng symbols nếu chưa có."""
    engine = get_async_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def main() -> None:
    await create_tables_if_not_exist()

    async for db in async_session_scope():
        repo = SymbolRepository(session=db)
        
        # Ghi một record
        record = await repo.create(
            id=uuid.uuid4(),
            name="VN30",
        )
        print("Đã ghi record:", record.id, record.name, record.created_at)
        # Commit xảy ra khi thoát async_session_scope() thành công


if __name__ == "__main__":
    asyncio.run(main())
