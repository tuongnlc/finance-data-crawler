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



