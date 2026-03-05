# CRUD với SQLAlchemy (Async)

Tài liệu hướng dẫn cách tổ chức và sử dụng CRUD trong dự án này bằng SQLAlchemy 2.x async, theo mô hình Repository.

## Tổng quan
- Kết nối cơ sở dữ liệu sử dụng SQLAlchemy async (asyncpg).
- Mỗi bảng có một SQLAlchemy model.
- BasePostgresRepository cung cấp sẵn các thao tác CRUD chung.
- Mỗi bounded context có repository adapter kế thừa BasePostgresRepository và gán model_class tương ứng.

## Cấu trúc chính
- Model: [models.py](file:///Users/tuongnguyen/Desktop/projects/finance_ai_platform/finance-data-crawler/src/shared/infrastructure/db/models.py)
- Kết nối DB: [connection.py](file:///Users/tuongnguyen/Desktop/projects/finance_ai_platform/finance-data-crawler/src/shared/infrastructure/db/connection.py)
- Base CRUD: [repository.py](file:///Users/tuongnguyen/Desktop/projects/finance_ai_platform/finance-data-crawler/src/shared/infrastructure/persistence/postgresql/repository.py)
- Adapter cụ thể: [company_name_repository.py](file:///Users/tuongnguyen/Desktop/projects/finance_ai_platform/finance-data-crawler/src/market_data/infrastructure/persistence/postgresql/company_name_repository.py)
- Ví dụ chạy nhanh: [insert_one_record.py](file:///Users/tuongnguyen/Desktop/projects/finance_ai_platform/finance-data-crawler/examples/insert_one_record.py)
- Alembic config: [alembic.ini](file:///Users/tuongnguyen/Desktop/projects/finance_ai_platform/finance-data-crawler/src/shared/infrastructure/db/alembic.ini), [migrations/](file:///Users/tuongnguyen/Desktop/projects/finance_ai_platform/finance-data-crawler/src/shared/infrastructure/db/migrations)

## Thiết lập môi trường
- Cài đặt:
  ```bash
  pip install -r requirements.txt
  ```
- Tạo .env với các biến:
  ```
  POSTGRES_DB=...
  POSTGRES_USER=...
  POSTGRES_PASSWORD=...
  POSTGRES_HOST=localhost
  POSTGRES_PORT=5432
  ```
- (Tùy chọn) Chạy Postgres bằng Docker:
  ```bash
  docker compose up -d postgres
  ```

## Khởi tạo schema
- Cách nhanh trong code: ví dụ đã gọi `Base.metadata.create_all`.
- Dùng Alembic:
  ```bash
  alembic -c src/shared/infrastructure/db/alembic.ini revision --autogenerate -m "message"
  alembic -c src/shared/infrastructure/db/alembic.ini upgrade head
  ```
  Alembic lấy DB URL từ biến môi trường (env.py đã load .env).

## Sử dụng CRUD
Ví dụ tạo bảng nếu chưa có, sau đó chạy CRUD đầy đủ:
```python
import uuid
from src.market_data.infrastructure.persistence.postgresql import CompanyNameRepository
from src.shared.infrastructure.db.connection import async_session_scope, get_async_engine
from src.shared.infrastructure.db.models import Base

async def run():
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

        # READ
        one = await repo.get_by_id(record.id)
        items = await repo.get_all(limit=10)

        # UPDATE
        updated = await repo.update(one, company_name="Công ty Đổi Tên")

        # DELETE
        deleted = await repo.delete_by_id(updated.id)
```

## API BasePostgresRepository
- create(**kwargs) → Model: tạo bản ghi, flush + refresh, chưa commit.
- get_by_id(id) → Model|None: lấy theo khóa chính.
- get_all(limit=None, offset=0) → list[Model]: lấy danh sách có phân trang.
- update(instance, **kwargs) → Model: chỉnh sửa thuộc tính, flush + refresh.
- delete(instance) → None: xóa instance hiện có và flush.
- delete_by_id(id) → bool: xóa theo id, trả về True nếu đã xóa.

Lưu ý: commit/rollback được quản lý bởi `async_session_scope`, commit khi thoát scope thành công.

## Tạo repository mới
1. Thêm model SQLAlchemy trong shared nếu chưa có.
2. Tạo adapter kế thừa BasePostgresRepository và gán `model_class`.
3. Thêm method đặc thù nếu cần, dùng `select(...)` với `self.session`.

Ví dụ:
```python
from sqlalchemy import select
from src.shared.infrastructure.persistence.postgresql.repository import BasePostgresRepository
from src.shared.infrastructure.db.models import CompanyName

class CompanyNameRepository(BasePostgresRepository[CompanyName]):
    model_class = CompanyName

    async def get_by_stock_id(self, stock_id: str) -> CompanyName | None:
        stmt = select(CompanyName).where(CompanyName.stock_id == stock_id)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()
```

## Lỗi thường gặp
- RuntimeWarning: coroutine 'AsyncSession.delete' was never awaited  
  Nguyên nhân: `AsyncSession.delete(...)` là coroutine và phải `await`.  
  Cách khắc phục: đảm bảo gọi trong hàm async và dùng `await self.session.delete(instance)`. Base repository đã thực hiện đúng; nếu bạn override, nhớ thêm `await`.

## Best practices
- Không log thông tin nhạy cảm (user/password DB).
- Gói commit theo use case bằng async_session_scope để đảm bảo transaction nhất quán.
- Dùng Alembic để quản lý schema trên môi trường thực tế.

