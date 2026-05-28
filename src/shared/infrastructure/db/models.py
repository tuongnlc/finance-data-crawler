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


class IncomeStatementTypeFour(Base):
    """
        Income statement type 4 for bank like ACB, TCB, CTG ...
    """
    __tablename__ = 'fs_income_statement_type_four'
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    stock_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    year: Mapped[int] = mapped_column(nullable=False, index=True)
    quarter: Mapped[str] = mapped_column(nullable=False, index=True)
    net_interest_income: Mapped[int] = mapped_column(nullable=False, comment='Thu nhập lãi thuần')
    interest_and_similar_income: Mapped[int] = mapped_column(nullable=False, comment='Thu nhập từ lãi và các khoản thu nhập tương tự')
    interest_and_similar_expenses: Mapped[int] = mapped_column(nullable=False, comment='Chi phí lãi và các chi phí tương tự')
    net_fee_and_commission_income: Mapped[int] = mapped_column(nullable=False, comment='Lãi/Lỗ thuần từ hoạt động dịch vụ')
    fee_and_commission_income: Mapped[int] = mapped_column(nullable=False, comment='Thu nhập từ hoạt động dịch vụ')
    fee_and_commission_expenses: Mapped[int] = mapped_column(nullable=False, comment='Chi phí hoạt động dịch vụ')
    net_gain_loss_from_foreign_currency_and_gold_dealings: Mapped[int] = mapped_column(nullable=False, comment='Lãi/Lỗ thuần từ hoạt động kinh doanh ngoại hối')
    net_gain_loss_from_trading_securities: Mapped[int] = mapped_column(nullable=False, comment='Lãi/Lỗ thuần từ mua bán chứng khoán kinh doanh')
    net_gain_loss_from_investment_securities: Mapped[int] = mapped_column(nullable=False, comment='Lãi/Lỗ thuần từ mua bán chứng khoán đầu tư')
    net_gain_loss_from_other_operating_activities: Mapped[int] = mapped_column(nullable=False, comment='Lãi/Lỗ thuần từ hoạt động khác')
    other_operating_income: Mapped[int] = mapped_column(nullable=False, comment='Thu nhập từ hoạt động khác')
    other_operating_expenses: Mapped[int] = mapped_column(nullable=False, comment='Chi phí hoạt động khác')
    income_from_long_term_investments: Mapped[int] = mapped_column(nullable=False, comment='Thu nhập từ hoạt động góp vốn mua cổ phần')
    operating_expenses: Mapped[int] = mapped_column(nullable=False, comment='Chi phí hoạt động')
    net_operating_profit_before_provision_for_credit_losses: Mapped[int] = mapped_column(nullable=False, comment='Lợi nhuận từ HDKD trước chi phí dự phòng rủi ro tín dụng')
    provision_expenses_for_credit_losses: Mapped[int] = mapped_column(nullable=False, comment='Chi phí dự phòng rủi ro tín dụng')
    total_accounting_profit_before_tax: Mapped[int] = mapped_column(nullable=False, comment='Tổng lợi nhuận trước thuế')
    corporate_income_tax_expense: Mapped[int] = mapped_column(nullable=False, comment='Chi phí thuế TNDN')
    current_corporate_income_tax_expense: Mapped[int] = mapped_column(nullable=False, comment='Chi phí thuế thu nhập hiện hành')
    deferred_corporate_income_tax_expense: Mapped[int] = mapped_column(nullable=False, comment='Chi phí thuế TNDN giữ lại')
    net_profit_after_corporate_income_tax: Mapped[int] = mapped_column(nullable=False, comment='Lợi nhuận sau thuế thu nhập doanh nghiệp')
    non_controlling_interests_and_preferred_dividends: Mapped[int] = mapped_column(nullable=False, comment='Lợi ích của cổ đông thiểu số và cổ tức ưu đãi')
    net_profit_parent: Mapped[int] = mapped_column(nullable=False, comment='LNST sau khi điều chỉnh Lợi ích của CĐTS và Cổ tức ưu đãi')


class BalanceSheetTypeOne(Base):
    """
        Balance sheet type 1 for product company like HPG, ACBm ....
    """
    __tablename__ = 'fs_balance_sheet_type_one'
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    stock_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    year: Mapped[int] = mapped_column(nullable=False, index=True)
    quarter: Mapped[str] = mapped_column(nullable=False, index=True)

    # ==================== TÀI SẢN (ASSETS) ====================
    current_assets: Mapped[int] = mapped_column(nullable=False, comment='A. Tài sản lưu động và đầu tư ngắn hạn')
    cash_and_cash_equivalents: Mapped[int] = mapped_column(nullable=False, comment='I. Tiền và các khoản tương đương tiền')
    cash: Mapped[int] = mapped_column(nullable=False, comment='1. Tiền')
    cash_equivalents: Mapped[int] = mapped_column(nullable=False, comment='2. Các khoản tương đương tiền')
    short_term_financial_investments: Mapped[int] = mapped_column(nullable=False, comment='II. Các khoản đầu tư tài chính ngắn hạn')
    trading_securities: Mapped[int] = mapped_column(nullable=False, comment='1. Chứng khoán kinh doanh')
    provision_for_diminution_in_value_of_trading_securities: Mapped[int] = mapped_column(nullable=False, comment='2. Dự phòng giảm giá chứng khoán kinh doanh')
    held_to_maturity_investments_short_term: Mapped[int] = mapped_column(nullable=False, comment='3. Đầu tư nắm giữ đến ngày đáo hạn')
    short_term_receivables: Mapped[int] = mapped_column(nullable=False, comment='III. Các khoản phải thu ngắn hạn')
    short_term_trade_receivables: Mapped[int] = mapped_column(nullable=False, comment='1. Phải thu ngắn hạn của khách hàng')
    short_term_advances_to_suppliers: Mapped[int] = mapped_column(nullable=False, comment='2. Trả trước cho người bán')
    short_term_internal_receivables: Mapped[int] = mapped_column(nullable=False, comment='3. Phải thu nội bộ ngắn hạn')
    receivables_construction_contract_progress: Mapped[int] = mapped_column(nullable=False, comment='4. Phải thu theo tiến độ hợp đồng xây dựng')
    short_term_loan_receivables: Mapped[int] = mapped_column(nullable=False, comment='5. Phải thu về cho vay ngắn hạn')
    other_short_term_receivables: Mapped[int] = mapped_column(nullable=False, comment='6. Phải thu ngắn hạn khác')
    provision_for_short_term_doubtful_debts: Mapped[int] = mapped_column(nullable=False, comment='7. Dự phòng phải thu ngắn hạn khó đòi')
    inventories: Mapped[int] = mapped_column(nullable=False, comment='IV. Tổng hàng tồn kho')
    gross_inventories: Mapped[int] = mapped_column(nullable=False, comment='1. Hàng tồn kho')
    provision_for_decline_in_value_of_inventories: Mapped[int] = mapped_column(nullable=False, comment='2. Dự phòng giảm giá hàng tồn kho')
    other_current_assets: Mapped[int] = mapped_column(nullable=False, comment='V. Tài sản ngắn hạn khác')
    short_term_prepaid_expenses: Mapped[int] = mapped_column(nullable=False, comment='1. Chi phí trả trước ngắn hạn')
    deductible_value_added_tax: Mapped[int] = mapped_column(nullable=False, comment='2. Thuế giá trị gia tăng được khấu trừ')
    taxes_and_other_receivables_from_state_budget: Mapped[int] = mapped_column(nullable=False, comment='3. Thuế và các khoản phải thu Nhà nước')
    government_bond_repo_transactions_short_term: Mapped[int] = mapped_column(nullable=False, comment='4. Giao dịch mua bán lại trái phiếu chính phủ')
    other_current_assets_items: Mapped[int] = mapped_column(nullable=False, comment='5. Tài sản ngắn hạn khác')

    non_current_assets: Mapped[int] = mapped_column(nullable=False, comment='B. Tài sản cố định và đầu tư dài hạn')
    long_term_receivables: Mapped[int] = mapped_column(nullable=False, comment='I. Các khoản phải thu dài hạn')
    long_term_trade_receivables: Mapped[int] = mapped_column(nullable=False, comment='1. Phải thu dài hạn của khách hàng')
    working_capital_provided_to_subordinates: Mapped[int] = mapped_column(nullable=False, comment='2. Vốn kinh doanh tại các đơn vị trực thuộc')
    long_term_internal_receivables: Mapped[int] = mapped_column(nullable=False, comment='3. Phải thu dài hạn nội bộ')
    long_term_loan_receivables: Mapped[int] = mapped_column(nullable=False, comment='4. Phải thu về cho vay dài hạn')
    other_long_term_receivables: Mapped[int] = mapped_column(nullable=False, comment='5. Phải thu dài hạn khác')
    provision_for_long_term_doubtful_debts: Mapped[int] = mapped_column(nullable=False, comment='6. Dự phòng phải thu dài hạn khó đòi')
    fixed_assets: Mapped[int] = mapped_column(nullable=False, comment='II. Tài sản cố định')
    tangible_fixed_assets: Mapped[int] = mapped_column(nullable=False, comment='1. Tài sản cố định hữu hình')
    tangible_fixed_assets_cost: Mapped[int] = mapped_column(nullable=False, comment='Nguyên giá')
    tangible_fixed_assets_accumulated_depreciation: Mapped[int] = mapped_column(nullable=False, comment='Giá trị hao mòn lũy kế')
    finance_lease_fixed_assets: Mapped[int] = mapped_column(nullable=False, comment='2. Tài sản cố định thuê tài chính')
    finance_lease_fixed_assets_cost: Mapped[int] = mapped_column(nullable=False, comment='Nguyên giá (2)')
    finance_lease_fixed_assets_accumulated_depreciation: Mapped[int] = mapped_column(nullable=False, comment='Giá trị hao mòn lũy kế (2)')
    intangible_fixed_assets: Mapped[int] = mapped_column(nullable=False, comment='3. Tài sản cố định vô hình')
    intangible_fixed_assets_cost: Mapped[int] = mapped_column(nullable=False, comment='Nguyên giá (3)')
    intangible_fixed_assets_accumulated_amortization: Mapped[int] = mapped_column(nullable=False, comment='Giá trị hao mòn lũy kế (3)')
    investment_properties: Mapped[int] = mapped_column(nullable=False, comment='III. Bất động sản đầu tư')
    investment_properties_cost: Mapped[int] = mapped_column(nullable=False, comment='Nguyên giá (4)')
    investment_properties_accumulated_depreciation: Mapped[int] = mapped_column(nullable=False, comment='Giá trị hao mòn lũy kế (4)')
    long_term_assets_in_progress: Mapped[int] = mapped_column(nullable=False, comment='IV. Tài sản dở dang dài hạn')
    long_term_work_in_progress: Mapped[int] = mapped_column(nullable=False, comment='1. Chi phí sản xuất, kinh doanh dở dang dài hạn')
    construction_in_progress: Mapped[int] = mapped_column(nullable=False, comment='2. chi phí xây dựng cơ bản dở dang')
    long_term_financial_investments: Mapped[int] = mapped_column(nullable=False, comment='V. Các khoản đầu tư tài chính dài hạn')
    investments_in_subsidiaries: Mapped[int] = mapped_column(nullable=False, comment='1. Đầu tư vào công ty con')
    investments_in_associates_and_joint_ventures: Mapped[int] = mapped_column(nullable=False, comment='2. Đầu tư vào công ty liên kết, liên doanh')
    equity_investments_in_other_entities: Mapped[int] = mapped_column(nullable=False, comment='3. Đầu tư khác vào công cụ vốn')
    provision_for_long_term_financial_investments: Mapped[int] = mapped_column(nullable=False, comment='4. Dự phòng giảm giá đầu tư tài chính dài hạn')
    held_to_maturity_investments_long_term: Mapped[int] = mapped_column(nullable=False, comment='5. Đầu tư nắm giữ đến ngày đáo hạn')
    other_non_current_assets: Mapped[int] = mapped_column(nullable=False, comment='VI. Tổng tài sản dài hạn khác')
    long_term_prepaid_expenses: Mapped[int] = mapped_column(nullable=False, comment='1. Chi phí trả trước dài hạn')
    deferred_corporate_income_tax_assets: Mapped[int] = mapped_column(nullable=False, comment='2. Tài sản Thuế thu nhập hoãn lại')
    other_long_term_asset_items: Mapped[int] = mapped_column(nullable=False, comment='3. Tài sản dài hạn khác')
    goodwill: Mapped[int] = mapped_column(nullable=False, comment='VII. Lợi thế thương mại')
    total_assets: Mapped[int] = mapped_column(nullable=False, comment='TỔNG CỘNG TÀI SẢN')

    # ==================== NGUỒN VỐN (LIABILITIES AND EQUITY) ====================
    total_liabilities: Mapped[int] = mapped_column(nullable=False, comment='A. Nợ phải trả')
    current_liabilities: Mapped[int] = mapped_column(nullable=False, comment='I. Nợ ngắn hạn')
    short_term_borrowings_and_finance_lease_liabilities: Mapped[int] = mapped_column(nullable=False, comment='1. Vay và nợ thuê tài chính ngắn hạn')
    current_portion_of_long_term_borrowings_and_liabilities: Mapped[int] = mapped_column(nullable=False, comment='2. Vay và nợ dài hạn đến hạn phải trả')
    short_term_trade_payables: Mapped[int] = mapped_column(nullable=False, comment='3. Phải trả người bán ngắn hạn')
    short_term_advances_from_customers: Mapped[int] = mapped_column(nullable=False, comment='4. Người mua trả tiền trước')
    statutory_obligations_and_taxes_payable: Mapped[int] = mapped_column(nullable=False, comment='5. Thuế và các khoản phải nộp nhà nước')
    payables_to_employees: Mapped[int] = mapped_column(nullable=False, comment='6. Phải trả người lao động')
    short_term_accrued_expenses: Mapped[int] = mapped_column(nullable=False, comment='7. Chi phí phải trả ngắn hạn')
    short_term_internal_payables: Mapped[int] = mapped_column(nullable=False, comment='8. Phải trả nội bộ ngắn hạn')
    payables_construction_contract_progress: Mapped[int] = mapped_column(nullable=False, comment='9. Phải trả theo tiến độ kế hoạch hợp đồng xây dựng')
    short_term_unearned_revenue: Mapped[int] = mapped_column(nullable=False, comment='10. Doanh thu chưa thực hiện ngắn hạn')
    other_short_term_payables: Mapped[int] = mapped_column(nullable=False, comment='11. Phải trả ngắn hạn khác')
    short_term_provisions: Mapped[int] = mapped_column(nullable=False, comment='12. Dự phòng phải trả ngắn hạn')
    bonus_and_welfare_fund: Mapped[int] = mapped_column(nullable=False, comment='13. Quỹ khen thưởng phúc lợi')
    price_stabilization_fund: Mapped[int] = mapped_column(nullable=False, comment='14. Quỹ bình ổn giá')
    government_bond_repo_transactions_liabilities: Mapped[int] = mapped_column(nullable=False, comment='15. Giao dịch mua bán lại trái phiếu chính phủ')
    
    non_current_liabilities: Mapped[int] = mapped_column(nullable=False, comment='II. Nợ dài hạn')
    long_term_trade_payables: Mapped[int] = mapped_column(nullable=False, comment='1. Phải trả người bán dài hạn')
    long_term_accrued_expenses: Mapped[int] = mapped_column(nullable=False, comment='2. Chi phí phải trả dài hạn')
    internal_payables_on_working_capital: Mapped[int] = mapped_column(nullable=False, comment='3. Phải trả nội bộ về vốn kinh doanh')
    long_term_internal_payables: Mapped[int] = mapped_column(nullable=False, comment='4. Phải trả nội bộ dài hạn')
    other_long_term_payables: Mapped[int] = mapped_column(nullable=False, comment='5. Phải trả dài hạn khác')
    long_term_borrowings_and_finance_lease_liabilities: Mapped[int] = mapped_column(nullable=False, comment='6. Vay và nợ thuê tài chính dài hạn')
    convertible_bonds: Mapped[int] = mapped_column(nullable=False, comment='7. Trái phiếu chuyển đổi')
    deferred_corporate_income_tax_liabilities: Mapped[int] = mapped_column(nullable=False, comment='8. Thuế thu nhập hoãn lại phải trả')
    provision_for_severance_allowances: Mapped[int] = mapped_column(nullable=False, comment='9. Dự phòng trợ cấp mất việc làm')
    long_term_provisions: Mapped[int] = mapped_column(nullable=False, comment='10. Dự phòng phải trả dài hạn')
    long_term_unearned_revenue: Mapped[int] = mapped_column(nullable=False, comment='11. Doanh thu chưa thực hiện dài hạn')
    science_and_technology_development_fund: Mapped[int] = mapped_column(nullable=False, comment='12. Quỹ phát triển khoa học và công nghệ')

    total_equity: Mapped[int] = mapped_column(nullable=False, comment='B. Nguồn vốn chủ sở hữu')
    owners_equity: Mapped[int] = mapped_column(nullable=False, comment='I. Vốn chủ sở hữu')
    contributed_charter_capital: Mapped[int] = mapped_column(nullable=False, comment='1. Vốn đầu tư của chủ sở hữu')
    share_premium: Mapped[int] = mapped_column(nullable=False, comment='2. Thặng dư vốn cổ phần')
    convertible_bond_options: Mapped[int] = mapped_column(nullable=False, comment='3. Quyền chọn chuyển đổi trái phiếu')
    other_owners_equity: Mapped[int] = mapped_column(nullable=False, comment='4. Vốn khác của chủ sở hữu')
    treasury_shares: Mapped[int] = mapped_column(nullable=False, comment='5. Cổ phiếu quỹ')
    asset_revaluation_differences: Mapped[int] = mapped_column(nullable=False, comment='6. Chênh lệch đánh giá lại tài sản')
    foreign_exchange_differences: Mapped[int] = mapped_column(nullable=False, comment='7. Chênh lệch tỷ giá hối đoái')
    investment_and_development_fund: Mapped[int] = mapped_column(nullable=False, comment='8. Quỹ đầu tư phát triển')
    financial_reserve_fund: Mapped[int] = mapped_column(nullable=False, comment='9. Quỹ dự phòng tài chính')
    other_funds_belonging_to_equity: Mapped[int] = mapped_column(nullable=False, comment='10. Quỹ khác thuộc vốn chủ sở hữu')
    undistributed_earnings_after_tax: Mapped[int] = mapped_column(nullable=False, comment='11. Lợi nhuận sau thuế chưa phân phối')
    accumulated_retained_earnings_up_to_previous_period: Mapped[int] = mapped_column(nullable=False, comment='LNST chưa phân phối lũy kế đến cuối kỳ trước')
    retained_earnings_for_current_period: Mapped[int] = mapped_column(nullable=False, comment='LNST chưa phân phối kỳ này')
    capital_expenditure_fund: Mapped[int] = mapped_column(nullable=False, comment='12. Nguồn vốn đầu tư xây dựng cơ bản')
    enterprise_rearrangement_support_fund: Mapped[int] = mapped_column(nullable=False, comment='13. Quỹ hỗ trợ sắp xếp doanh nghiệp')
    non_controlling_interests: Mapped[int] = mapped_column(nullable=False, comment='14. Lợi ích của cổ đông không kiểm soát')
    other_resources_and_funds: Mapped[int] = mapped_column(nullable=False, comment='II. Nguồn kinh phí và quỹ khác')
    non_business_expenditure_source: Mapped[int] = mapped_column(nullable=False, comment='1. Nguồn kinh phí')
    expenditure_source_formed_fixed_assets: Mapped[int] = mapped_column(nullable=False, comment='2. Nguồn kinh phí đã hình thành tài sản cố định')
    job_loss_allowance_reserve_fund: Mapped[int] = mapped_column(nullable=False, comment='3. Quỹ dự phòng trợ cấp mất việc làm')
    total_liabilities_and_equity: Mapped[int] = mapped_column(nullable=False, comment='TỔNG CỘNG NGUỒN VỐN')


class BalanceSheetTypeFour(Base):
    __tablename__ = 'fs_balance_sheet_type_four'
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    # Thông tin cơ bản
    stock_id: Mapped[str] = mapped_column(nullable=False, comment='Mã cổ phiếu')
    year: Mapped[int] = mapped_column(nullable=False, comment='Năm tài chính')
    quarter: Mapped[str] = mapped_column(nullable=False, comment='Quý')

    # ==================== TÀI SẢN (ASSETS) ====================
    cash_gold_and_valuables: Mapped[int] = mapped_column(nullable=False, comment='I. Tiền mặt, chứng từ có giá trị, ngoại tệ, kim loại quý, đá quý')
    balances_with_the_sbv: Mapped[int] = mapped_column(nullable=False, comment='II. Tiền gửi tại NHNN')
    treasury_bills_and_eligible_short_term_valuable_papers: Mapped[int] = mapped_column(nullable=False, comment='III. Tín phiếu kho bạc và các giấy tờ có giá ngắn hạn đủ tiêu chuẩn khác')
    total_placements_with_and_loans_to_other_cis: Mapped[int] = mapped_column(BigInteger, nullable=False, comment='IV. Tiền, vàng gửi tại các TCTD khác và cho vay các TCTD khác')
    placements_with_other_credit_institutions: Mapped[int] = mapped_column(BigInteger, nullable=False, comment='1. Tiền, Vàng gửi tại các TCTD khác')
    loans_to_other_credit_institutions: Mapped[int] = mapped_column(nullable=False, comment='2. Cho vay các TCTD khác')
    allowance_for_loans_to_other_credit_institutions: Mapped[int] = mapped_column(nullable=False, comment='3. Dự phòng rủi ro cho vay các TCTD khác')
    total_trading_securities: Mapped[int] = mapped_column(nullable=False, comment='V. Chứng khoán kinh doanh')
    trading_securities_gross: Mapped[int] = mapped_column(nullable=False, comment='1. Chứng khoán kinh doanh')
    allowance_for_diminution_in_value_of_trading_securities: Mapped[int] = mapped_column(nullable=False, comment='2. Dự phòng giảm giá chứng khoán kinh doanh')
    derivative_financial_instruments_and_other_assets: Mapped[int] = mapped_column(nullable=False, comment='VI. Các công cụ tài chính phái sinh và các tài sản tài chính khác')
    total_loans_to_customers: Mapped[int] = mapped_column(BigInteger, nullable=False, comment='VII. Cho vay khách hàng')
    loans_to_customers_gross: Mapped[int] = mapped_column(BigInteger, nullable=False, comment='1. Cho vay khách hàng')
    allowance_for_loans_to_customers: Mapped[int] = mapped_column(nullable=False, comment='2. Dự phòng rủi ro cho vay khách hàng')
    total_investment_securities: Mapped[int] = mapped_column(nullable=False, comment='VIII. Chứng khoán đầu tư')
    available_for_sale_investment_securities: Mapped[int] = mapped_column(nullable=False, comment='1. Chứng khoán đầu tư sẵn sàng để bán')
    held_to_maturity_investment_securities: Mapped[int] = mapped_column(nullable=False, comment='2. Chứng khoán đầu tư giữ đến ngày đáo hạn')
    allowance_for_diminution_in_value_of_investment_securities: Mapped[int] = mapped_column(nullable=False, comment='3. Dự phòng giảm giá chứng khoán đầu tư')
    total_long_term_investments: Mapped[int] = mapped_column(nullable=False, comment='IX. Góp vốn đầu tư dài hạn')
    investments_in_subsidiaries: Mapped[int] = mapped_column(nullable=False, comment='1. Đầu tư vào công ty con')
    investments_in_joint_ventures: Mapped[int] = mapped_column(nullable=False, comment='2. Góp vốn liên doanh')
    investments_in_associates: Mapped[int] = mapped_column(nullable=False, comment='3. Đầu tư vào công ty liên kết')
    other_long_term_investments: Mapped[int] = mapped_column(nullable=False, comment='4. Đầu tư dài hạn khác')
    allowance_for_diminution_in_value_of_long_term_investments: Mapped[int] = mapped_column(nullable=False, comment='5. Dự phòng giảm giá đầu tư dài hạn')
    total_fixed_assets: Mapped[int] = mapped_column(nullable=False, comment='X. Tài sản cố định')
    tangible_fixed_assets: Mapped[int] = mapped_column(nullable=False, comment='1. Tài sản cố định hữu hình')
    tangible_fixed_assets_cost: Mapped[int] = mapped_column(nullable=False, comment='Nguyên giá')
    tangible_fixed_assets_accumulated_depreciation: Mapped[int] = mapped_column(nullable=False, comment='Giá trị hao mòn lũy kế')
    finance_lease_fixed_assets: Mapped[int] = mapped_column(nullable=False, comment='2. Tài sản cố định thuê tài chính')
    finance_lease_fixed_assets_cost: Mapped[int] = mapped_column(nullable=False, comment='Nguyên giá (2)')
    finance_lease_fixed_assets_accumulated_depreciation: Mapped[int] = mapped_column(nullable=False, comment='Giá trị hao mòn lũy kế (2)')
    intangible_fixed_assets: Mapped[int] = mapped_column(nullable=False, comment='3. Tài sản cố định vô hình')
    intangible_fixed_assets_cost: Mapped[int] = mapped_column(nullable=False, comment='Nguyên giá (3)')
    intangible_fixed_assets_accumulated_amortization: Mapped[int] = mapped_column(nullable=False, comment='Giá trị hao mòn lũy kế (3)')
    construction_in_progress: Mapped[int] = mapped_column(nullable=False, comment='5. Chi phí XDCB dở dang')
    investment_properties: Mapped[int] = mapped_column(nullable=False, comment='XI. Bất động sản đầu tư')
    investment_properties_cost: Mapped[int] = mapped_column(nullable=False, comment='Nguyên giá (4)')
    investment_properties_accumulated_depreciation: Mapped[int] = mapped_column(nullable=False, comment='Giá trị hao mòn lũy kế (4)')
    total_other_assets: Mapped[int] = mapped_column(nullable=False, comment='XII. Tài sản có khác')
    other_receivables: Mapped[int] = mapped_column(nullable=False, comment='1. Các khoản phải thu')
    accrued_interest_and_fees_receivable: Mapped[int] = mapped_column(nullable=False, comment='2. Các khoản lãi, phí phải thu')
    deferred_corporate_income_tax_assets: Mapped[int] = mapped_column(nullable=False, comment='3. Tài sản thuế TNDN hoãn lại')
    other_asset_items: Mapped[int] = mapped_column(nullable=False, comment='4. Tài sản có khác')
    goodwill: Mapped[int] = mapped_column(nullable=False, comment='Trong đó: Lợi thế thương mại')
    allowance_for_other_on_balance_sheet_assets: Mapped[int] = mapped_column(nullable=False, comment='5. Các khoản dự phòng rủi ro cho các tài sản có nội bảng khác')
    total_assets: Mapped[int] = mapped_column(BigInteger, nullable=False, comment='TỔNG CỘNG TÀI SẢN')

    # ==================== NGUỒN VỐN (LIABILITIES AND EQUITY) ====================
    borrowings_from_the_government_and_the_sbv: Mapped[int] = mapped_column(nullable=False, comment='I. Các khoản nợ chính phủ và NHNN')
    total_deposits_and_borrowings_from_other_cis: Mapped[int] = mapped_column(nullable=False, comment='II. Tiền gửi và cho vay các TCTD khác')
    deposits_from_other_credit_institutions: Mapped[int] = mapped_column(nullable=False, comment='1. Tiền gửi các tổ chức tín dụng khác')
    borrowings_from_other_credit_institutions: Mapped[int] = mapped_column(nullable=False, comment='2. Vay các TCTD khác')
    deposits_from_customers: Mapped[int] = mapped_column(BigInteger, nullable=False, comment='III. Tiền gửi khách hàng')
    derivatives_and_other_fin_liab: Mapped[int] = mapped_column(BigInteger, nullable=False, comment='IV. Các công cụ tài chính phái sinh và các khoản nợ tài chính khác')
    entrusted_funds_and_grants: Mapped[int] = mapped_column(BigInteger, nullable=False, comment='V. Vốn tài trợ, uỷ thác đầu tư mà ngân hàng chịu rủi ro')
    valuable_papers_issued: Mapped[int] = mapped_column(nullable=False, comment='VI. Phát hành giấy tờ có giá')
    total_other_liabilities: Mapped[int] = mapped_column(nullable=False, comment='VII. Các khoản nợ khác')
    accrued_interest_and_fees_payable: Mapped[int] = mapped_column(nullable=False, comment='1. Các khoản lãi, phí phải trả')
    deferred_corporate_income_tax_liabilities: Mapped[int] = mapped_column(nullable=False, comment='2.Thuế TNDN hoãn lại phải trả')
    other_payables_and_liabilities: Mapped[int] = mapped_column(nullable=False, comment='3. Các khoản phải trả và công nợ khác')
    other_provisions: Mapped[int] = mapped_column(nullable=False, comment='4. Dự phòng rủi ro khác')
    total_capital_and_reserves: Mapped[int] = mapped_column(nullable=False, comment='VIII. Vốn và các quỹ')  # Sửa từ total_equity sang total_capital_and_reserves
    credit_institution_capital: Mapped[int] = mapped_column(nullable=False, comment='1. Vốn của Tổ chức tín dụng')
    charter_capital: Mapped[int] = mapped_column(nullable=False, comment='Vốn điều lệ')
    capital_expenditure_fund: Mapped[int] = mapped_column(nullable=False, comment='Vốn đầu tư XDCB')
    share_premium: Mapped[int] = mapped_column(nullable=False, comment='Thặng dư vốn cổ phần')
    treasury_shares: Mapped[int] = mapped_column(nullable=False, comment='Cổ phiếu quỹ')
    preferred_shares: Mapped[int] = mapped_column(nullable=False, comment='Cổ phiếu ưu đãi')
    other_capital: Mapped[int] = mapped_column(nullable=False, comment='Vốn khác')
    funds_of_the_credit_institution: Mapped[int] = mapped_column(nullable=False, comment='2. Quỹ của TCTD')
    foreign_exchange_differences: Mapped[int] = mapped_column(nullable=False, comment='3. Chênh lệch tỷ giá hối đoái')
    asset_revaluation_differences: Mapped[int] = mapped_column(nullable=False, comment='4. Chênh lệch đánh giá lại tài sản')
    retained_earnings_or_accumulated_losses: Mapped[int] = mapped_column(nullable=False, comment='5. Lợi nhuận chưa phân phối/Lỗ lũy kế')
    other_reserves_and_funds: Mapped[int] = mapped_column(nullable=False, comment='6. Nguồn kinh phí, Quỹ khác')
    non_controlling_interests: Mapped[int] = mapped_column(nullable=False, comment='IX. Lợi ích của cổ đông thiểu số')
    total_liabilities_and_equity: Mapped[int] = mapped_column(BigInteger, nullable=False, comment='TỔNG CỘNG NGUỒN VỐN')    


class CashFlowStatementTypeOne(Base):
    """
    Cash Flow Statement (Báo cáo lưu chuyển tiền tệ) - Gián tiếp 
    Áp dụng cho doanh nghiệp sản xuất, thương mại (Ví dụ: HPG, DGC, MWG...)
    """
    __tablename__ = 'fs_cash_flow_statement_type_one'

    # --- Thông tin cấu trúc dữ liệu ---
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    stock_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    year: Mapped[int] = mapped_column(nullable=False, index=True)
    quarter: Mapped[str] = mapped_column(String(10), nullable=False, index=True)

    # ==================== I. DÒNG TIỀN TỪ HOẠT ĐỘNG KINH DOANH ====================
    profit_before_tax: Mapped[int] = mapped_column(BigInteger, nullable=False, comment='1. Lợi nhuận trước thuế')
    total_adjustments: Mapped[int] = mapped_column(BigInteger, nullable=False, comment='2. Điều chỉnh cho các khoản')
    depreciation_of_fixed_assets: Mapped[int] = mapped_column(BigInteger, nullable=False, comment='Khấu hao TSCĐ')
    provisions: Mapped[int] = mapped_column(BigInteger, nullable=False, comment='Các khoản dự phòng')
    share_of_profit_from_associates: Mapped[int] = mapped_column(BigInteger, nullable=False, comment='Lợi nhuận thuần từ đầu tư vào công ty liên kết')
    write_offs_of_fixed_assets: Mapped[int] = mapped_column(BigInteger, nullable=False, comment='Xóa sổ tài sản cố định (thuần)')
    unrealized_foreign_exchange_changes: Mapped[int] = mapped_column(BigInteger, nullable=False, comment='Lãi, lỗ chênh lệch tỷ giá hối đoái chưa thực hiện')
    gain_loss_from_disposal_of_fixed_assets: Mapped[int] = mapped_column(BigInteger, nullable=False, comment='Lãi, lỗ từ thanh lý TSCĐ')
    gain_loss_from_investing_activities: Mapped[int] = mapped_column(BigInteger, nullable=False, comment='Lãi, lỗ từ hoạt động đầu tư')
    interest_income_from_deposits: Mapped[int] = mapped_column(BigInteger, nullable=False, comment='Lãi tiền gửi')
    interest_income: Mapped[int] = mapped_column(BigInteger, nullable=False, comment='Thu nhập lãi')
    interest_expense: Mapped[int] = mapped_column(BigInteger, nullable=False, comment='Chi phí lãi vay')
    direct_appropriations_from_profit: Mapped[int] = mapped_column(BigInteger, nullable=False, comment='Các khoản chi trực tiếp từ lợi nhuận')
    operating_profit_before_working_capital_change: Mapped[int] = mapped_column(BigInteger, nullable=False, comment='3. Lợi nhuận từ hoạt động kinh doanh trước thay đổi vốn lưu động')
    change_in_receivables: Mapped[int] = mapped_column(BigInteger, nullable=False, comment='Tăng, giảm các khoản phải thu')
    change_in_inventory: Mapped[int] = mapped_column(BigInteger, nullable=False, comment='Tăng, giảm hàng tồn kho')
    change_in_payables_excl_tax_and_interest: Mapped[int] = mapped_column(BigInteger, nullable=False, comment='Tăng, giảm các khoản phải trả (Không kể lãi vay phải trả, thuế thu nhập doanh nghiệp phải nộp)')
    change_in_prepaid_expenses: Mapped[int] = mapped_column(BigInteger, nullable=False, comment='Tăng giảm chi phí trả trước')
    change_in_other_current_assets: Mapped[int] = mapped_column(BigInteger, nullable=False, comment='Tăng giảm tài sản ngắn hạn khác')
    interest_paid: Mapped[int] = mapped_column(BigInteger, nullable=False, comment='Tiền lãi vay phải trả')
    corporate_income_tax_paid: Mapped[int] = mapped_column(BigInteger, nullable=False, comment='Thuế thu nhập doanh nghiệp đã nộp')
    other_operating_cash_receipts: Mapped[int] = mapped_column(BigInteger, nullable=False, comment='Tiền thu khác từ hoạt động kinh doanh')
    other_operating_cash_payments: Mapped[int] = mapped_column(BigInteger, nullable=False, comment='Tiền chi khác từ hoạt động kinh doanh')
    net_cash_flows_from_operating_activities: Mapped[int] = mapped_column(BigInteger, nullable=False, comment='Lưu chuyển tiền thuần từ hoạt động kinh doanh')

    # ==================== II. DÒNG TIỀN TỪ HOẠT ĐỘNG ĐẦU TƯ ====================
    cash_paid_for_fixed_assets: Mapped[int] = mapped_column(BigInteger, nullable=False, comment='1. Tiền chi để mua sắm, xây dựng TSCĐ và các tài sản dài hạn khác')
    cash_received_from_disposal_of_fixed_assets: Mapped[int] = mapped_column(BigInteger, nullable=False, comment='2. Tiền thu từ thanh lý, nhượng bán TSCĐ và các tài sản dài hạn khác')
    cash_paid_for_loans_and_debt_instruments: Mapped[int] = mapped_column(BigInteger, nullable=False, comment='3. Tiền chi cho vay, mua các công cụ nợ của đơn vị khác')
    cash_received_from_loans_and_debt_instruments: Mapped[int] = mapped_column(BigInteger, nullable=False, comment='4. Tiền thu hồi cho vay, bán lại các công cụ nợ của các đơn vị khác')
    investments_in_joint_ventures_and_associates: Mapped[int] = mapped_column(BigInteger, nullable=False, comment='5. Đầu tư góp vốn vào công ty liên doanh liên kết')
    cash_paid_for_short_term_investments: Mapped[int] = mapped_column(BigInteger, nullable=False, comment='6. Chi đầu tư ngắn hạn')
    cash_paid_for_equity_investments: Mapped[int] = mapped_column(BigInteger, nullable=False, comment='7. Tiền chi đầu tư góp vốn vào đơn vị khác')
    cash_received_from_equity_investments: Mapped[int] = mapped_column(BigInteger, nullable=False, comment='8. Tiền thu hồi đầu tư góp vốn vào đơn vị khác')
    interest_received_from_deposits: Mapped[int] = mapped_column(BigInteger, nullable=False, comment='9. Lãi tiền gửi đã thu')
    interest_and_dividends_received: Mapped[int] = mapped_column(BigInteger, nullable=False, comment='10. Tiền thu lãi cho vay, cổ tức và lợi nhuận được chia')
    cash_paid_to_buy_back_minority_interests: Mapped[int] = mapped_column(BigInteger, nullable=False, comment='11. Tiền chi mua lại phần vốn góp của các cổ đông thiểu số')
    net_cash_flows_from_investing_activities: Mapped[int] = mapped_column(BigInteger, nullable=False, comment='Lưu chuyển tiền thuần từ hoạt động đầu tư')

    # ==================== III. DÒNG TIỀN TỪ HOẠT ĐỘNG TÀI CHÍNH ====================
    cash_received_from_issuing_shares: Mapped[int] = mapped_column(BigInteger, nullable=False, comment='1. Tiền thu từ phát hành cổ phiếu, nhận vốn góp của chủ sở hữu')
    cash_paid_for_share_buybacks: Mapped[int] = mapped_column(BigInteger, nullable=False, comment='2. Tiền chi trả vốn góp cho các chủ sở hữu, mua lại cổ phiếu của doanh nghiệp đã phát hành')
    cash_received_from_borrowings: Mapped[int] = mapped_column(BigInteger, nullable=False, comment='3. Tiền vay ngắn hạn, dài hạn nhận được')
    cash_repayments_of_borrowings: Mapped[int] = mapped_column(BigInteger, nullable=False, comment='4. Tiền chi trả nợ gốc vay')
    cash_repayments_of_finance_lease_liabilities: Mapped[int] = mapped_column(BigInteger, nullable=False, comment='5. Tiền chi trả nợ thuê tài chính')
    other_financing_cash_payments: Mapped[int] = mapped_column(BigInteger, nullable=False, comment='6. Tiền chi khác từ hoạt động tài chính')
    payments_for_privatization: Mapped[int] = mapped_column(BigInteger, nullable=False, comment='7. Tiền chi trả từ cổ phần hóa')
    dividends_paid_to_owners: Mapped[int] = mapped_column(BigInteger, nullable=False, comment='8. Cổ tức, lợi nhuận đã trả cho chủ sở hữu')
    minority_capital_contribution_into_subsidiaries: Mapped[int] = mapped_column(BigInteger, nullable=False, comment='9. Vốn góp của các cổ đông thiểu số vào các công ty con')
    payments_for_welfare_and_social_funds: Mapped[int] = mapped_column(BigInteger, nullable=False, comment='10. Chi tiêu quỹ phúc lợi xã hội')
    net_cash_flows_from_financing_activities: Mapped[int] = mapped_column(BigInteger, nullable=False, comment='Lưu chuyển tiền thuần từ hoạt động tài chính')

    # ==================== TỔNG KẾT CUỐI KỲ ====================
    net_change_in_cash: Mapped[int] = mapped_column(BigInteger, nullable=False, comment='Lưu chuyển tiền thuần trong kỳ')
    cash_and_cash_equivalents_at_start_of_period: Mapped[int] = mapped_column(BigInteger, nullable=False, comment='Tiền và tương đương tiền đầu kỳ')
    effect_of_exchange_rate_changes: Mapped[int] = mapped_column(BigInteger, nullable=False, comment='Ảnh hưởng của thay đổi tỷ giá hối đoái quy đổi ngoại tệ')
    cash_and_cash_equivalents_at_end_of_period: Mapped[int] = mapped_column(BigInteger, nullable=False, comment='Tiền và tương đương tiền cuối kỳ')


class CashFlowStatementTypeFour(Base):
    """
        Cash flow statement for bank like ACB, TCB, CTG ...
    """
    __tablename__ = 'fs_cash_flow_statement_type_four'
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    stock_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    year: Mapped[int] = mapped_column(nullable=False, index=True)
    quarter: Mapped[str] = mapped_column(String(10), nullable=False, index=True)

    # ==================== I. DÒNG TIỀN TỪ HOẠT ĐỘNG KINH DOANH ====================
    interest_and_similar_income_received: Mapped[int] = mapped_column(nullable=False, comment='Thu nhập lãi và các khoản thu nhập tương tự nhận được')
    interest_and_similar_expenses_paid: Mapped[int] = mapped_column(nullable=False, comment='Chi phí lãi và các chi phí tương tự đã trả')
    fee_and_commission_income_received: Mapped[int] = mapped_column(nullable=False, comment='Thu nhập từ hoạt động dịch vụ nhận được')
    net_gain_loss_from_trading_activities: Mapped[int] = mapped_column(nullable=False, comment='Chênh lệch số tiền thực thu/ thực chi từ hoạt động kinh doanh (ngoại tệ, vàng bạc, chứng khoán)')
    other_operating_income: Mapped[int] = mapped_column(nullable=False, comment='Thu nhập khác')
    cash_recovered_from_bad_debts_written_off: Mapped[int] = mapped_column(nullable=False, comment='Tiền thu các khoản nợ đã được xử lý xóa, bù đắp bằng nguồn rủi ro')
    cash_paid_to_employees_and_for_operating_expenses: Mapped[int] = mapped_column(nullable=False, comment='Tiền chi trả cho nhân viên và hoạt động quản lý, công vụ')
    corporate_income_tax_paid: Mapped[int] = mapped_column(nullable=False, comment='Tiền thuế thu nhập thực nộp trong kỳ')
    operating_cash_flows_before_working_capital_changes: Mapped[int] = mapped_column(nullable=False, comment='Lưu chuyển tiền thuần từ hoạt động kinh doanh trước những thay đổi về tài sản và vốn lưu động')
    change_in_deposits_and_loans_to_other_cits: Mapped[int] = mapped_column(nullable=False, comment='(Tăng)/Giảm các khoản tiền, vàng gửi và cho vay các TCTD khác')
    change_in_trading_securities: Mapped[int] = mapped_column(nullable=False, comment='(Tăng)/Giảm các khoản về kinh doanh chứng khoán')
    change_in_derivative_financial_assets: Mapped[int] = mapped_column(nullable=False, comment='(Tăng)/Giảm các công cụ tài chính phái sinh và các tài sản tài chính khác')
    change_in_loans_to_customers: Mapped[int] = mapped_column(nullable=False, comment='(Tăng)/Giảm các khoản cho vay khách hàng')
    change_in_provisions_for_credit_losses: Mapped[int] = mapped_column(nullable=False, comment='(Tăng)/Giảm nguồn dự phòng để bù bắp tổn thất các khoản')
    change_in_other_operating_assets: Mapped[int] = mapped_column(nullable=False, comment='(Tăng)/Giảm khác về tài sản hoạt động')
    change_in_due_to_government_and_sbv: Mapped[int] = mapped_column(nullable=False, comment='Tăng/(Giảm) các khoản nợ chính phủ và NHNN')
    change_in_deposits_and_borrowings_from_other_cits: Mapped[int] = mapped_column(nullable=False, comment='Tăng/(Giảm) các khoản tiền gửi, tiền vay các TCTD')
    change_in_deposits_from_customers: Mapped[int] = mapped_column(nullable=False, comment='Tăng/(Giảm) tiền gửi của khách hàng')
    change_in_valuable_papers_issued: Mapped[int] = mapped_column(nullable=False, comment='Tăng/(Giảm) phát hành giấy tờ có giá')
    change_in_entrusted_funds_and_loans: Mapped[int] = mapped_column(nullable=False, comment='Tăng/(Giảm) vốn tài trợ, ủy thác đầu tư, cho vay mà TCTD chịu rủi ro')
    change_in_derivative_financial_liabilities: Mapped[int] = mapped_column(nullable=False, comment='Tăng/(Giảm) các công cụ tài chính phái sinh và các khoản nợ tài chính khác')
    change_in_other_operating_liabilities: Mapped[int] = mapped_column(nullable=False, comment='Tăng/(Giảm) khác về công nợ hoạt động')
    payments_from_welfare_and_other_funds: Mapped[int] = mapped_column(nullable=False, comment='Chi từ các quỹ của TCTD')
    net_cash_flows_from_operating_activities: Mapped[int] = mapped_column(nullable=False, comment='Lưu chuyển tiền thuần từ hoạt động kinh doanh')

    # ==================== II. DÒNG TIỀN TỪ HOẠT ĐỘNG ĐẦU TƯ ====================
    cash_proceeds_from_disposal_of_subsidiaries: Mapped[int] = mapped_column(nullable=False, comment='Tiền giảm do bán công ty con')
    cash_paid_for_fixed_assets: Mapped[int] = mapped_column(nullable=False, comment='Mua sắm TSCĐ')
    cash_received_from_disposal_of_fixed_assets: Mapped[int] = mapped_column(nullable=False, comment='Tiền thu từ thanh lý, nhượng bán TSCĐ')
    cash_paid_for_disposal_of_fixed_assets: Mapped[int] = mapped_column(nullable=False, comment='Tiền chi từ thanh lý, nhượng bán TSCĐ')
    cash_paid_for_investment_properties: Mapped[int] = mapped_column(nullable=False, comment='Mua sắm bất động sản đầu tư')
    cash_received_from_disposal_of_investment_properties: Mapped[int] = mapped_column(nullable=False, comment='Tiền thu từ bán, thanh lý bất động sản đầu tư')
    cash_paid_for_disposal_of_investment_properties: Mapped[int] = mapped_column(nullable=False, comment='Tiền chi ra do bán, thanh lý bất động sản đầu tư')
    cash_paid_for_equity_investments: Mapped[int] = mapped_column(nullable=False, comment='Tiền chi đầu tư, góp vốn vào các đơn vị khác')
    cash_received_from_equity_investments: Mapped[int] = mapped_column(nullable=False, comment='Tiền thu đầu tư, góp vốn vào các đơn vị khác')
    dividends_and_profits_received: Mapped[int] = mapped_column(nullable=False, comment='Tiền thu cổ tức và lợi nhuận được chia từ các khoản đầu tư, góp vốn dài hạn')
    net_cash_flows_from_investing_activities: Mapped[int] = mapped_column(nullable=False, comment='Lưu chuyển tiền thuần từ hoạt động đầu tư')

    # ==================== III. DÒNG TIỀN TỪ HOẠT ĐỘNG TÀI CHÍNH ====================
    cash_received_from_issuing_shares: Mapped[int] = mapped_column(nullable=False, comment='Tăng vốn cổ phần từ góp vốn và phát hành cổ phiếu')
    cash_received_from_long_term_eligible_papers_and_loans: Mapped[int] = mapped_column(nullable=False, comment='Tiền thu từ phát hành giấy tờ có giá dài hạn có đủ điều kiện tính vào vốn tự có và các khoản vốn vay dài hạn khác')
    cash_repayments_of_long_term_eligible_papers_and_loans: Mapped[int] = mapped_column(nullable=False, comment='Tiền chi thanh toán giấy tờ có giá dài hạn có đủ điều kiện tính vào vốn tự có và các khoản vốn vay dài hạn khác')
    dividends_paid_to_shareholders: Mapped[int] = mapped_column(nullable=False, comment='Cổ tức trả cho cổ đông, lợi nhuận đã chia')
    cash_paid_for_treasury_shares_buyback: Mapped[int] = mapped_column(nullable=False, comment='Tiền chi ra mua cổ phiếu ngân quỹ')
    cash_received_from_disposal_of_treasury_shares: Mapped[int] = mapped_column(nullable=False, comment='Tiền thu được do bán cổ phiếu ngân quỹ')
    net_cash_flows_from_financing_activities: Mapped[int] = mapped_column(nullable=False, comment='Lưu chuyển tiền từ hoạt động tài chính')

    # ==================== TỔNG KẾT CUỐI KỲ ====================
    net_change_in_cash: Mapped[int] = mapped_column(nullable=False, comment='Lưu chuyển tiền thuần trong kỳ')
    cash_and_cash_equivalents_at_start_of_period: Mapped[int] = mapped_column(nullable=False, comment='Tiền và tương đương tiền đầu kỳ')
    effect_of_exchange_rate_changes: Mapped[int] = mapped_column(nullable=False, comment='Ảnh hưởng của thay đổi tỷ giá hối đoái quy đổi ngoại tệ')
    cash_and_cash_equivalents_at_end_of_period: Mapped[int] = mapped_column(nullable=False, comment='Tiền và tương đương tiền cuối kỳ')
