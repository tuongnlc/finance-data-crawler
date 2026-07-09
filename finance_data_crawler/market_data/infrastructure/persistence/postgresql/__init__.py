# PostgreSQL adapters
from finance_data_crawler.market_data.infrastructure.persistence.postgresql.company_name_repository import (
    CompanyNameRepository, 
)
from finance_data_crawler.market_data.infrastructure.persistence.postgresql.fund_gav_repository import (
    FundGavRepository,
)
from finance_data_crawler.market_data.infrastructure.persistence.postgresql.stock_price_repository import (
    StockPriceRepository,
)
from finance_data_crawler.market_data.infrastructure.persistence.postgresql.foreign_trade import (
    ForeignTradeRepository,
)
from finance_data_crawler.market_data.infrastructure.persistence.postgresql.stock_index_repository import (
    StockIndexRepository,
)

__all__ = ["CompanyNameRepository", "FundGavRepository", "StockPriceRepository", "ForeignTradeRepository", "StockIndexRepository"]
