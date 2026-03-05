"""
Repository ports (interfaces) cho bounded context market_data.

Domain layer chỉ khai báo contract; implementation nằm ở infrastructure.
"""
from __future__ import annotations

import uuid
from typing import Protocol, runtime_checkable


@runtime_checkable
class CompanyNameRepositoryProtocol(Protocol):
    """Port: interface lưu / đọc CompanyName. Implementation là PostgreSQL adapter."""

    async def create(
        self,
        *,
        id: uuid.UUID | None = None,
        stock_id: str,
        company_name: str,
        business_sector: str,
    ) -> object:
        """Tạo một bản ghi CompanyName. Trả về instance (ORM hoặc domain entity)."""
        ...

    async def get_by_id(self, id_value: uuid.UUID | str) -> object | None:
        """Lấy theo primary key."""
        ...

    async def get_by_stock_id(self, stock_id: str) -> object | None:
        """Lấy theo stock_id (nếu cần cho domain)."""
        ...
