"""SQLAlchemy declarative models (bảng) dùng cho PostgreSQL."""
import uuid
from sqlalchemy import DateTime, String, func, Date, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import date
from sqlalchemy import BigInteger


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
    capitalization: Mapped[int] = mapped_column(nullable=True)
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
    month: Mapped[int] = mapped_column(nullable=True)


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
    foreign_room: Mapped[int] = mapped_column(BigInteger, nullable=True, index=True)
    buy_volume: Mapped[int] = mapped_column(BigInteger, nullable=True)
    sell_volume: Mapped[int] = mapped_column(BigInteger, nullable=True)


class StockIndex(Base):
    """
        Stock index data including: stock_id, date, index_value
    """
    __tablename__ = 'stock_index'
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    trading_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    open_index_value: Mapped[int] = mapped_column(nullable=False)
    highest_index_value: Mapped[int] = mapped_column(nullable=False)
    lowest_index_value: Mapped[int] = mapped_column(nullable=False)
    close_index_value: Mapped[int] = mapped_column(nullable=False)
    volume: Mapped[int] = mapped_column(BigInteger, nullable=False)
    index_type: Mapped[str] = mapped_column(String(255), nullable=False, index=True)


# Models for crawl market_news
class NewspaperUrl(Base):
    """
        Newspaper url data including: url, title, content, date, source, is_crawled
    """
    __tablename__ = 'newspaper_url'
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    newspaper_title: Mapped[str] = mapped_column(String(255))
    newspaper_url: Mapped[str] = mapped_column(String(255), index=True)
    source: Mapped[str] = mapped_column(String(255))
    is_crawled: Mapped[int] = mapped_column(nullable=False, default=0)
    created_at: Mapped[date] = mapped_column(Date, nullable=False)


class Newspaper(Base):
    """
        Newspaper data including: id, newspaper_title, newspaper_url, publish_date, content, summary, is_load_to_qdrant
    """
    __tablename__ = 'newspaper'
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    newspaper_title: Mapped[str] = mapped_column(Text)
    newspaper_url: Mapped[str] = mapped_column(String(255))
    publish_date: Mapped[date] = mapped_column(Date, nullable=True)
    newspaper_content: Mapped[str] = mapped_column(Text, nullable=True)
    newspaper_summary: Mapped[str] = mapped_column(Text)
    is_load_to_qdrant: Mapped[int] = mapped_column(nullable=False, default=0)
    created_at: Mapped[date] = mapped_column(Date, nullable=False)


# Models for crawl bctc
class IncomeStatementType1(Base):
    """
        Income statement type 1 for product company like HPG, MWG, VNM ...

        Total: 21 columns
    """
    __tablename__ = 'fs_income_statement_type_one'
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    stock_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    year: Mapped[int] = mapped_column(nullable=False, index=True)
    quarter: Mapped[str] = mapped_column(nullable=False, index=True)
    gross_revenue: Mapped[int] = mapped_column(nullable=False, comment='1. Tổng doanh thu hoạt động kinh doanh')
    revenue_deductions: Mapped[int] = mapped_column(nullable=False, comment='2. Các khoản giảm trừ doanh thu')
    net_revenue: Mapped[int] = mapped_column(nullable=False, comment='3. Doanh thu thuần (1)-(2)')
    cost_of_goods_sold: Mapped[int] = mapped_column(nullable=False, comment='4. Giá vốn hàng bán')
    gross_profit: Mapped[int] = mapped_column(nullable=False, comment='5. Lợi nhuận gộp (3)-(4)')
    financial_income: Mapped[int] = mapped_column(nullable=False, comment='6. Doanh thu hoạt động tài chính')
    financial_expenses: Mapped[int] = mapped_column(nullable=False, comment='7. Chi phí tài chính')
    interest_expense: Mapped[int] = mapped_column(nullable=False, comment='Trong đó: Chi phí lãi vay')
    jv_associates_profit: Mapped[int] = mapped_column(nullable=False, comment='8. Phần lợi nhuận hoặc lỗ trong công ty liên kết liên doanh')
    selling_expenses: Mapped[int] = mapped_column(nullable=False, comment='9. Chi phí bán hàng')
    general_and_administrative_expenses: Mapped[int] = mapped_column(nullable=False, comment='10. Chi phí quản lý doanh nghiệp')
    net_operating_profit: Mapped[int] = mapped_column(nullable=False, comment='11. Lợi nhuận thuần từ hoạt động kinh doanh (5)+(6)-(7)+(8)-(9)-(10)')
    other_income: Mapped[int] = mapped_column(nullable=False, comment='12. Thu nhập khác')
    other_expenses: Mapped[int] = mapped_column(nullable=False, comment='13. Chi phí khác')
    other_profit: Mapped[int] = mapped_column(nullable=False, comment='14. Lợi nhuận khác (12)-(13)')
    total_accounting_profit_before_tax: Mapped[int] = mapped_column(nullable=False, comment='15. Tổng lợi nhuận kế toán trước thuế (11)+(14)')
    current_corporate_income_tax_expense: Mapped[int] = mapped_column(nullable=False, comment='16. Chi phí thuế TNDN hiện hành')
    deferred_corporate_income_tax_expense: Mapped[int] = mapped_column(nullable=False, comment='17. Chi phí thuế TNDN hoãn lại')
    corporate_income_tax_expense: Mapped[int] = mapped_column(nullable=False, comment='18. Chi phí thuế TNDN (16)+(17)')
    net_profit_after_corporate_income_tax: Mapped[int] = mapped_column(nullable=False, comment='19. Lợi nhuận sau thuế thu nhập doanh nghiệp (15)-(18)')
    non_controlling_interests: Mapped[int] = mapped_column(nullable=False, comment='20. Lợi nhuận sau thuế của cổ đông không kiểm soát')
    net_profit_parent: Mapped[int] = mapped_column(nullable=False, comment='21. Lợi nhuận sau thuế của cổ đông của công ty mẹ (19)-(20)')
