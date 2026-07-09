"""
Base entity (domain) and base PostgreSQL repository (CRUD).

- BaseEntity: Pydantic model với id (UUID), from_postgre (_id → id). Dùng cho domain/API.
- BasePostgresRepository: CRUD trên SQLAlchemy model (create, get_by_id, get_all, update, delete).
"""
from __future__ import annotations

import uuid
from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from finance_data_crawler.shared.infrastructure.db.connection import get_async_session

ModelType = TypeVar("ModelType")


class BasePostgresRepository(Generic[ModelType]):
    """
    Base repository CRUD cho một bảng (SQLAlchemy declarative model).
    Subclass: gán model_class = YourTable, gọi create/get_by_id/update/delete.
    """

    model_class: type[ModelType]

    def __init__(self, session: AsyncSession | None = None) -> None:
        self._session = session

    @property
    def session(self) -> AsyncSession:
        if self._session is None:
            self._session = get_async_session()
        return self._session

    async def create(self, **kwargs: object) -> ModelType:
        """Tạo một bản ghi."""
        instance = self.model_class(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def get_by_id(self, id_value: int | str | uuid.UUID) -> ModelType | None:
        """Lấy một bản ghi theo primary key (cột `id`)."""
        stmt = select(self.model_class).where(self.model_class.id == id_value)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        *,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[ModelType]:
        """Lấy danh sách, tùy chọn limit/offset."""
        stmt = select(self.model_class).offset(offset)
        if limit is not None:
            stmt = stmt.limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update(self, instance: ModelType, **kwargs: object) -> ModelType:
        """Cập nhật instance (các thuộc tính trong kwargs)."""
        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def delete(self, instance: ModelType) -> None:
        """Xóa một bản ghi."""
        await self.session.delete(instance)
        await self.session.flush()

    async def delete_by_id(self, id_value: int | str | uuid.UUID) -> bool:
        """Xóa theo id. Trả về True nếu đã xóa, False nếu không tìm thấy."""
        entity = await self.get_by_id(id_value)
        if entity is None:
            return False
        await self.delete(entity)
        return True

    