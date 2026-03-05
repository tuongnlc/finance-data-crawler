"""SQLAlchemy declarative models (bảng) dùng cho PostgreSQL."""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


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