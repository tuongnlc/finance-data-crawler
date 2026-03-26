# PostgreSQL adapters
from src.market_data.infrastructure.persistence.postgresql.company_name_repository import (
    CompanyNameRepository, 
)
from src.market_data.infrastructure.persistence.postgresql.fund_gav_repository import (
    FundGavRepository,
)
from src.market_data.infrastructure.persistence.postgresql.stock_price_repository import (
    StockPriceRepository,
)
from src.market_data.infrastructure.persistence.postgresql.foreign_trade import (
    ForeignTradeRepository,
)
from src.market_data.infrastructure.persistence.postgresql.vn_index_repository import (
    VNIndexRepository,
)

__all__ = ["CompanyNameRepository", "FundGavRepository", "StockPriceRepository", "ForeignTradeRepository", "VNIndexRepository"]
