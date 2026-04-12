from typing import Any
from urllib.parse import urlparse
from src.market_data.domain.repository import StockIndexRepositoryProtocol
from src.market_data.application.ports.crawl_data_port import CrawlDataPort


class CrawlStockIndexUseCase:
    def __init__(self, 
            crawler: CrawlDataPort, 
            loader: StockIndexRepositoryProtocol
        ):
        self.crawler = crawler
        self.loader = loader

    async def execute(self, link: str, **kwargs: Any) -> Any:
        async for stock_indexs in self.crawler.extract(link, **kwargs):
            for stock_index in stock_indexs:
                # Clean and parse data
                try:
                    # Assuming date format is dd/mm/yyyy. Convert to YYYY-MM-DD for database if needed,
                    # or rely on SQLAlchemy/driver to handle date string if format matches.
                    # However, for robustness, we should parse it.
                    # Let's keep it simple for now and pass as is, assuming DB handles it or it's standard.
                    # If format is dd/mm/yyyy, we might need to swap to yyyy-mm-dd.
                    # Let's convert "10/05/2023" to "2023-05-10"
                    # https://simplize.vn/chi-so/DOW-JONES/lich-su-gia extract index_type is dow_jones
                    date_str = stock_index["trading_date"]
                    if "/" in date_str:
                        day, month, year = date_str.split("/")
                        date_iso = f"{year}-{month}-{day}"
                    else:
                        date_iso = date_str        
                    open_index_value = int(stock_index["open_index_value"].replace(",", "").replace(".", ""))
                    highest_index_value = int(stock_index["highest_index_value"].replace(",", "").replace(".", ""))
                    lowest_index_value = int(stock_index["lowest_index_value"].replace(",", "").replace(".", ""))
                    close_index_value = int(stock_index["close_index_value"].replace(",", "").replace(".", ""))
                    volume = int(stock_index["volume"].replace(",", "").replace(".", ""))
                    #get index_type by link
                    parsed = urlparse(link)
                    parts = [p for p in parsed.path.split("/") if p]
                    if len(parts) >= 2 and parts[-1].lower() == "lich-su-gia":
                        raw_index_type = parts[-2]
                    else:
                        raw_index_type = parts[-1] if parts else ""
                    index_type = raw_index_type.lower().replace("-", "_")

                    await self.loader.upsert_by_trading_date(
                        trading_date=date_iso,
                        open_index_value=open_index_value,
                        highest_index_value=highest_index_value,
                        lowest_index_value=lowest_index_value,
                        close_index_value=close_index_value,
                        volume=volume,
                        index_type=index_type,
                    )
                except Exception as e:
                    raise e
