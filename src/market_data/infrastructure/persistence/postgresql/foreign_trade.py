"""
Adapter: triển khai StockPriceRepository bằng PostgreSQL (SQLAlchemy).

Implement port market_data.domain.repository.StockPriceRepositoryProtocol.
"""
from __future__ import annotations
from datetime import datetime, date as date_type
from sqlalchemy import select
from src.shared.infrastructure.db.models import ForeignTrade
from src.shared.infrastructure.persistence.postgresql.repository import (
    BasePostgresRepository,
)


class ForeignTradeRepository(BasePostgresRepository[ForeignTrade]):
    """Repository cụ thể cho bảng foreign_trade. Dùng trong market_data use cases."""   

    model_class = ForeignTrade

    async def get_by_stock_id(self, stock_id: str) -> ForeignTrade | None:
        """Lấy một bản ghi theo stock_id."""
        stmt = select(ForeignTrade).where(ForeignTrade.stock_id == stock_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def upsert_by_date_and_stock_id(
        self,
        *,
        stock_id: str,
        date: str | date_type,
        foreign_room: int,
        buy_volume: int,
        sell_volume: int,
    ) -> ForeignTrade:
        """Upsert (insert or update) một bản ghi ForeignTrade theo stock_id và date. Trả về instance (ORM hoặc domain entity)."""       
        
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

        stmt = select(ForeignTrade).where(
            ForeignTrade.stock_id == stock_id, ForeignTrade.trading_date == trading_date
        )
        result = await self.session.execute(stmt)
        stock_price = result.scalar_one_or_none()
        if stock_price is None:
            stock_price = ForeignTrade(
                stock_id=stock_id,
                trading_date=trading_date,
                foreign_room=foreign_room,
                buy_volume=buy_volume,
                sell_volume=sell_volume,
            )
            self.session.add(stock_price)
        else:
            stock_price.foreign_room = foreign_room
            stock_price.buy_volume = buy_volume
            stock_price.sell_volume = sell_volume
        await self.session.flush()
        return stock_price
