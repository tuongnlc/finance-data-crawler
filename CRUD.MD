# CRUD với DDD (Domain-Driven Design)

Tài liệu mô tả cách thực hiện CRUD trong project theo kiến trúc DDD: **domain** định nghĩa port (interface), **infrastructure** cung cấp adapter (implementation).

---

## 1. Tổng quan kiến trúc

```
┌─────────────────────────────────────────────────────────────────┐
│  Application / Use case                                         │
│  (nhận repository qua dependency injection, gọi create/get/...)  │
└───────────────────────────────┬─────────────────────────────────┘
                                │ phụ thuộc vào
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  Domain (bounded context, e.g. market_data)                      │
│  • Entity (Pydantic)                                             │
│  • Repository Protocol (port) – chỉ khai báo contract           │
└───────────────────────────────┬─────────────────────────────────┘
                                │ implement
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  Infrastructure                                                  │
│  • Repository implementation (adapter) – PostgreSQL, SQLAlchemy │
│  • Kế thừa BasePostgresRepository, gán model_class               │
└─────────────────────────────────────────────────────────────────┘
```

- **Domain** không biết PostgreSQL/SQLAlchemy; chỉ biết "có chỗ lưu/đọc" với các method nhất định.
- **Infrastructure** implement chi tiết; có thể thay bằng adapter khác (Fake, MongoDB...) mà use case không đổi.

---

## 2. Các layer CRUD

### 2.1. Domain – Port (interface)

**Vị trí:** `src/<bounded_context>/domain/repository.py`

Định nghĩa **Protocol** (contract) cho repository: tên method, tham số, kiểu trả về. Không chứa logic, không import ORM.

**Ví dụ:** `src/market_data/domain/repository.py`

```python
from typing import Protocol, runtime_checkable
import uuid

@runtime_checkable
class CompanyNameRepositoryProtocol(Protocol):
    async def create(self, *, id: uuid.UUID | None, stock_id: str, company_name: str, business_sector: str) -> object: ...
    async def get_by_id(self, id_value: uuid.UUID | str) -> object | None: ...
    async def get_by_stock_id(self, stock_id: str) -> object | None: ...
```

Use case / application layer nhận `CompanyNameRepositoryProtocol` (type hint) và gọi các method trên; lúc chạy truyền vào implementation thật (PostgreSQL) hoặc Fake (test).

### 2.2. Infrastructure – Adapter (implementation)

**Vị trí:** `src/<bounded_context>/infrastructure/persistence/postgresql/<tên>_repository.py`

- Kế thừa `BasePostgresRepository[YourModel]`.
- Gán `model_class = YourModel` (SQLAlchemy model từ `src/shared/infrastructure/db/models.py`).
- Có thể thêm method đặc thù (vd: `get_by_stock_id`).

**Ví dụ:** `src/market_data/infrastructure/persistence/postgresql/company_name_repository.py`

```python
from src.shared.infrastructure.db.models import CompanyName
from src.shared.infrastructure.persistence.postgresql.repository import BasePostgresRepository

class CompanyNameRepository(BasePostgresRepository[CompanyName]):
    model_class = CompanyName

    async def get_by_stock_id(self, stock_id: str) -> CompanyName | None:
        stmt = select(CompanyName).where(CompanyName.stock_id == stock_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
```

### 2.3. Base repository – API chung

**Vị trí:** `src/shared/infrastructure/persistence/postgresql/repository.py`

`BasePostgresRepository[ModelType]` cung cấp sẵn:

| Method | Mô tả |
|--------|--------|
| `create(**kwargs)` | Tạo bản ghi; trả về instance đã refresh |
| `get_by_id(id_value)` | Lấy theo primary key `id`; trả về `None` nếu không có |
| `get_all(limit=None, offset=0)` | Lấy danh sách (có phân trang) |
| `update(instance, **kwargs)` | Cập nhật các thuộc tính trong `kwargs` |
| `delete(instance)` | Xóa bản ghi |
| `delete_by_id(id_value)` | Xóa theo id; trả về `True`/`False` |

Subclass chỉ cần khai báo `model_class` là dùng được toàn bộ; có thể override hoặc thêm method (vd: `get_by_stock_id`).

---

## 3. Thêm repository mới (theo DDD)

1. **Domain – Port**  
   Trong `src/<bounded_context>/domain/repository.py`, thêm một `Protocol` mới với các method cần thiết (create, get_by_id, get_by_xxx, ...).

2. **Shared – Model**  
   Trong `src/shared/infrastructure/db/models.py`, thêm SQLAlchemy model (bảng) nếu chưa có; tạo migration nếu cần.

3. **Infrastructure – Adapter**  
   Tạo file `src/<bounded_context>/infrastructure/persistence/postgresql/<tên>_repository.py`, class kế thừa `BasePostgresRepository[Model]`, gán `model_class`, thêm method đặc thù nếu cần.

4. **Export**  
   Trong `src/<bounded_context>/infrastructure/persistence/postgresql/__init__.py`, export class repository mới.

---

## 4. Ví dụ sử dụng CRUD

Session và engine lấy từ `src.shared.infrastructure.db.connection` (vd: `async_session_scope`, `get_async_engine`). Repository nhận `session` để dùng chung transaction.

### Create

```python
from src.market_data.infrastructure.persistence.postgresql import CompanyNameRepository
from src.shared.infrastructure.db.connection import async_session_scope
import uuid

async for db in async_session_scope():
    repo = CompanyNameRepository(session=db)
    record = await repo.create(
        id=uuid.uuid4(),
        stock_id="VN30",
        company_name="Công ty CP VN30",
        business_sector="Tài chính",
    )
    print(record.id, record.stock_id)  # commit khi thoát scope
```

### Read (by id)

```python
record = await repo.get_by_id(record.id)
if record:
    print(record.company_name)
```

### Read (by custom field)

```python
record = await repo.get_by_stock_id("VN30")
```

### Read (list)

```python
items = await repo.get_all(limit=10, offset=0)
```

### Update

```python
updated = await repo.update(record, company_name="Tên mới", business_sector="Ngành mới")
```

### Delete

```python
await repo.delete(record)
# hoặc
deleted = await repo.delete_by_id(record.id)  # True/False
```

---

## 5. Tóm tắt vị trí file

| Thành phần | Đường dẫn |
|------------|-----------|
| Repository port (Protocol) | `src/<bounded_context>/domain/repository.py` |
| Repository implementation | `src/<bounded_context>/infrastructure/persistence/postgresql/<tên>_repository.py` |
| Base CRUD (shared) | `src/shared/infrastructure/persistence/postgresql/repository.py` |
| SQLAlchemy models | `src/shared/infrastructure/db/models.py` |
| Example | `examples/insert_one_record.py` |

Use case / application code nên type-hint theo **Protocol** (port) và nhận **implementation** qua constructor hoặc DI; không import trực tiếp lớp adapter trong domain.
