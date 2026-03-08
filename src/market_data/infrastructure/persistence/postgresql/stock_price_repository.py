"""
Adapter: triển khai StockPriceRepository bằng PostgreSQL (SQLAlchemy).

Implement port market_data.domain.repository.StockPriceRepositoryProtocol.
"""
from __future__ import annotations
from datetime import datetime, date as date_type
from sqlalchemy import select
from src.shared.infrastructure.db.models import StockPrice
from src.shared.infrastructure.persistence.postgresql.repository import (
    BasePostgresRepository,
)


class StockPriceRepository(BasePostgresRepository[StockPrice]):
    """Repository cụ thể cho bảng stock_price. Dùng trong market_data use cases."""

    model_class = StockPrice

    async def get_by_stock_id(self, stock_id: str) -> StockPrice | None:
        """Lấy một bản ghi theo stock_id."""
        stmt = select(StockPrice).where(StockPrice.stock_id == stock_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def upsert_by_date_and_stock_id(
        self,
        *,
        stock_id: str,
        date: str | date_type,
        open_price: float,
        high_price: float,
        low_price: float,
        close_price: float,
        volume: int,
    ) -> StockPrice:
        """Upsert (insert or update) một bản ghi StockPrice theo stock_id và date. Trả về instance (ORM hoặc domain entity)."""
        
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

        stmt = select(StockPrice).where(
            StockPrice.stock_id == stock_id, StockPrice.trading_date == trading_date
        )
        result = await self.session.execute(stmt)
        stock_price = result.scalar_one_or_none()
        if stock_price is None:
            stock_price = StockPrice(
                stock_id=stock_id,
                trading_date=trading_date,
                open_price=open_price,
                high_price=high_price,
                low_price=low_price,
                close_price=close_price,
                volume=volume,
            )
            self.session.add(stock_price)
        else:
            stock_price.open_price = open_price
            stock_price.high_price = high_price
            stock_price.low_price = low_price
            stock_price.close_price = close_price
            stock_price.volume = volume
        await self.session.flush()
        return stock_price
