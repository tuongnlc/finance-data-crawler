"""SQLAlchemy declarative models (bảng) dùng cho PostgreSQL."""
import uuid
from sqlalchemy import DateTime, String, func, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import date


class Base(DeclarativeBase):
    pass


class CompanyName(Base):
    """
        Company data including: stock_id, company_name, business_sector
    """
    __tablename__ = 'company_name'
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    stock_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    business_sector: Mapped[str] = mapped_column(String(255), nullable=False, index=True)


class FundGav(Base):
    """
        Fund Nav data including: fund_id, stock_id, business_sector, gav
    """
    __tablename__ = 'fund_gav'
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    fund_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    stock_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    business_sector: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    gav: Mapped[float] = mapped_column(nullable=False)


class StockPrice(Base):
    """
        Stock price data including: stock_id, date, open_price, high_price, low_price, close_price, volume
    """
    __tablename__ = 'stock_price'
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    stock_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    trading_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    open_price: Mapped[float] = mapped_column(nullable=False)
    high_price: Mapped[float] = mapped_column(nullable=False)
    low_price: Mapped[float] = mapped_column(nullable=False)
    close_price: Mapped[float] = mapped_column(nullable=False)
    volume: Mapped[int] = mapped_column(nullable=False)


class ForeignTrade(Base):
    """
        Foreign trade data including: stock_id, date, foreign_room, buy_volume, sell_volume
    """
    __tablename__ = 'foreign_trade'
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    stock_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    trading_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    foreign_room: Mapped[int] = mapped_column(nullable=True, index=True)
    buy_volume: Mapped[int] = mapped_column(nullable=True)
    sell_volume: Mapped[int] = mapped_column(nullable=True)