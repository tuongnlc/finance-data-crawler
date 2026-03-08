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


class FundGavRepositoryProtocol(Protocol):
    """Port: interface lưu / đọc FundGav. Implementation là PostgreSQL adapter."""
    async def create(
        self,
        *,
        id: uuid.UUID | None = None,
        fund_id: str,
        stock_id: str,
        business_sector: str,
        gav: float,
    ) -> object:
        """Tạo một bản ghi FundNav. Trả về instance (ORM hoặc domain entity)."""
        ...

    async def get_by_id(self, id_value: uuid.UUID | str) -> object | None:
        """Lấy theo primary key."""
        ...

    async def get_by_fund_id(self, fund_id: str) -> object | None:
        """Lấy theo fund_id (nếu cần cho domain)."""
        ...


class StockPriceRepositoryProtocol(Protocol):
    """Port: interface lưu / đọc StockPrice. Implementation là PostgreSQL adapter."""
    async def create(
        self,
        *,
        id: uuid.UUID | None = None,
        stock_id: str,
        date: str,
        open_price: float,
        high_price: float,
        low_price: float,
        close_price: float,
        volume: int,
    ) -> object:
        """Tạo một bản ghi StockPrice. Trả về instance (ORM hoặc domain entity)."""
        ...

    async def get_by_id(self, id_value: uuid.UUID | str) -> object | None:
        """Lấy theo primary key."""
        ...

    async def get_by_stock_id(self, stock_id: str) -> object | None:
        """Lấy theo stock_id (nếu cần cho domain)."""
        ...