from typing import Any
from src.market_data.domain.repository import VnIndexRepositoryProtocol
from src.market_data.application.ports.crawl_data_port import CrawlDataPort


class CrawlVnIndexUseCase:
    def __init__(self, 
            crawler: CrawlDataPort, 
            loader: VnIndexRepositoryProtocol
        ):
        self.crawler = crawler
        self.loader = loader

    async def execute(self, link: str, **kwargs: Any) -> Any:
        async for vn_index_data in self.crawler.extract(link, **kwargs):
            for vn_index_value in vn_index_data:
                # Clean and parse data
                try:
                    # Assuming date format is dd/mm/yyyy. Convert to YYYY-MM-DD for database if needed,
                    # or rely on SQLAlchemy/driver to handle date string if format matches.
                    # However, for robustness, we should parse it.
                    # Let's keep it simple for now and pass as is, assuming DB handles it or it's standard.
                    # If format is dd/mm/yyyy, we might need to swap to yyyy-mm-dd.
                    # Let's convert "10/05/2023" to "2023-05-10"
                    date_str = vn_index_value["trading_date"]
                    if "/" in date_str:
                        day, month, year = date_str.split("/")
                        date_iso = f"{year}-{month}-{day}"
                    else:
                        date_iso = date_str
                    
                    open_index_value = int(vn_index_value["open_index_value"].replace(",", "").replace(".", ""))
                    highest_index_value = int(vn_index_value["highest_index_value"].replace(",", "").replace(".", ""))
                    lowest_index_value = int(vn_index_value["lowest_index_value"].replace(",", "").replace(".", ""))
                    close_index_value = int(vn_index_value["close_index_value"].replace(",", "").replace(".", ""))
                    volume = int(vn_index_value["volume"].replace(",", "").replace(".", ""))

                    await self.loader.upsert_by_trading_date(
                        trading_date=date_iso,
                        open_index_value=open_index_value,
                        highest_index_value=highest_index_value,
                        lowest_index_value=lowest_index_value,
                        close_index_value=close_index_value,
                        volume=volume,
                    )
                except Exception as e:
                    raise e
