"""
Adapter: Implement VNIndexRepository with PostgreSQL (SQLAlchemy).

Implement port market_data.domain.repository.VNIndexRepositoryProtocol.
"""
from __future__ import annotations
from datetime import datetime, date as date_type
from sqlalchemy import select
# from finance_data_crawler.shared.infrastructure.db.models import VnIndex
from finance_data_crawler.shared.infrastructure.db.models import StockIndex
from finance_data_crawler.shared.infrastructure.persistence.postgresql.repository import (
    BasePostgresRepository,
)

class StockIndexRepository(BasePostgresRepository[StockIndex]):
    """Repository cụ thể cho bảng stock_index. Dùng trong market_data use cases."""

    model_class = StockIndex

    async def get_by_date(self, date: str | date_type) -> StockIndex | None:
        """Lấy một bản ghi theo date."""
        # Ensure date is a date object
        if isinstance(date, str):
            try:
                # Try ISO format YYYY-MM-DD
                trading_date = datetime.strptime(date, "%Y-%m-%d").date()
            except ValueError:
                # Try DD/MM/YYYY
                trading_date = datetime.strptime(date, "%d/%m/%Y").date()
        else:
            trading_date = date

        stmt = select(StockIndex).where(StockIndex.trading_date == trading_date)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def upsert_by_trading_date(
        self,
        *,
        trading_date: str | date_type,
        open_index_value: float,
        highest_index_value: float,
        lowest_index_value: float,
        close_index_value: float,
        volume: int,
        index_type: str,
    ) -> StockIndex:
        """Upsert (insert or update) một bản ghi StockIndex theo date. Trả về instance (ORM hoặc domain entity)."""
        
        # Ensure trading_date is a date object
        if isinstance(trading_date, str):
            try:
                # Try ISO format YYYY-MM-DD
                trading_date = datetime.strptime(trading_date, "%Y-%m-%d").date()
            except ValueError:
                # Try DD/MM/YYYY
                trading_date = datetime.strptime(trading_date, "%d/%m/%Y").date()
        else:
            trading_date = trading_date

        stmt = select(StockIndex).where(
            StockIndex.trading_date == trading_date,
            StockIndex.index_type == index_type,
        )
        result = await self.session.execute(stmt)
        stock_index = result.scalar_one_or_none()
        if stock_index is None:
            stock_index = StockIndex(
                trading_date=trading_date,
                open_index_value=open_index_value,
                highest_index_value=highest_index_value,
                lowest_index_value=lowest_index_value,
                close_index_value=close_index_value,
                volume=volume,
                index_type=index_type,
            )
            self.session.add(stock_index)
        else:
            stock_index.open_index_value = open_index_value
            stock_index.highest_index_value = highest_index_value
            stock_index.lowest_index_value = lowest_index_value
            stock_index.close_index_value = close_index_value
            stock_index.volume = volume
            stock_index.index_type = index_type

        await self.session.commit()
        return stock_index
