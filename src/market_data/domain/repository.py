"""
Repository ports (interfaces) cho bounded context market_data.

Domain layer chỉ khai báo contract; implementation nằm ở infrastructure.
"""
from __future__ import annotations

import uuid
from typing import Protocol, runtime_checkable
from datetime import date


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
        capitalization: int | None = None,
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
        report_month: int,
    ) -> object:
        """Tạo một bản ghi FundGav. Trả về instance (ORM hoặc domain entity)."""
        ...

    async def get_by_id(self, id_value: uuid.UUID | str) -> object | None:
        """Lấy theo primary key."""
        ...

    async def get_by_fund_id(self, fund_id: str) -> object | None:
        """Lấy theo fund_id (nếu cần cho domain)."""
        ...

    async def delete_before_load(self, report_month: int) -> None:
        """Xóa tất cả bản ghi FundGav cua tháng hien tai."""
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

    async def upsert_by_date_and_stock_id(
        self,
        *,
        stock_id: str,
        date: str,
        open_price: float,
        high_price: float,
        low_price: float,
        close_price: float,
        volume: int,
    ) -> object:
        """Upsert (insert or update) một bản ghi StockPrice theo stock_id và date. Trả về instance (ORM hoặc domain entity)."""
        ...

class ForeignTradeRepositoryProtocol(Protocol):
    """Port: interface lưu / đọc ForeignTrade. Implementation là PostgreSQL adapter."""
    async def create(
        self,
        *,
        id: uuid.UUID | None = None,
        stock_id: str,
        date: str,
        foreign_room: str,
        buy_volume: int,
        sell_volume: int,
    ) -> object:
        """Tạo một bản ghi ForeignTrade. Trả về instance (ORM hoặc domain entity)."""
        ...

    async def get_by_id(self, id_value: uuid.UUID | str) -> object | None:
        """Lấy theo primary key."""
        ...

    async def get_by_stock_id(self, stock_id: str) -> object | None:
        """Lấy theo stock_id (nếu cần cho domain)."""
        ...

    async def upsert_by_date_and_stock_id(
        self,
        *,
        stock_id: str,
        date: str,
        foreign_room: str,
        buy_volume: int,
        sell_volume: int
    ) -> object:
        """Upsert (insert or update) một bản ghi ForeignTrade theo stock_id và date. Trả về instance (ORM hoặc domain entity)."""
        ...


### Protocol for Stock-Index Repository
class StockIndexRepositoryProtocol(Protocol):
    """Port: interface lưu / đọc StockIndex. Implementation là PostgreSQL adapter."""
    async def create(
        self,
        *,
        id: uuid.UUID | None = None,
        trading_date: str,
        open_index_value: float,
        highest_index_value: float,
        lowest_index_value: float,
        close_index_value: float,
        volume: int,
        index_type: str,
    ) -> object:
        """Tạo một bản ghi StockIndex. Trả về instance (ORM hoặc domain entity)."""
        ...

    async def upsert_by_trading_date(
        self,
        *,
        trading_date: str,
        open_index_value: float,
        highest_index_value: float,
        lowest_index_value: float,
        close_index_value: float,
        volume: int,
        index_type: str,
    ) -> object:
        """Upsert (insert or update) một bản ghi VnIndex theo trading_date. Trả về instance (ORM hoặc domain entity)."""
        ...


### Protocol for Newspaper-Url Repository
class NewspaperUrlRepositoryProtocol(Protocol):
    """Port: interface write / read NewspaperUrl"""
    async def upsert_by_newspaper_url(
        self,
        *,
        newspaper_url: str,
        source: str,
        is_crawled: int,
        created_at: date,
    ) -> object:
        """Upsert (insert or update) NewspaperUrl based on newspaper_url."""
        ...

    async def query_urls_by_is_crawled(
        self
    ) -> list[str]:
        """Query NewspaperUrl that not crawled"""


### Protocol for Newspaper Repository
class NewspaperRepositoryProtocol(Protocol):
    """Port: interface write / read Newspaper"""
    async def upsert_by_newspaper_url(
        self,
        *,
        id: uuid.UUID | None = None,
        title: str,
        url: str,
        publish_date: str,
        content: str,
        summary: str,
        is_embedded: int,
        created_at: date,
    ) -> object:
        """Upsert (insert or update) Newspaper based on newspaper_url."""
        ...