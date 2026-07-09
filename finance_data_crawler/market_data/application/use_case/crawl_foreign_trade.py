from typing import Any
from src.market_data.domain.repository import ForeignTradeRepositoryProtocol
from src.market_data.application.ports.crawl_data_port import CrawlDataPort


class CrawlForeignTradeUseCase:
    def __init__(self, 
            crawler: CrawlDataPort, 
            loader: ForeignTradeRepositoryProtocol
        ):
        self.crawler = crawler
        self.loader = loader

    async def execute(self, link: str, **kwargs: Any) -> Any:
        # Extract stock_id from link if not provided
        stock_id = kwargs.get("stock_id")
        if not stock_id and "/co-phieu/" in link:
            parts = link.split("/co-phieu/")
            if len(parts) > 1:
                stock_id = parts[1].split("/")[0]

        if not stock_id:
            raise ValueError("stock_id is required. Provide it in kwargs or check the link format.")

        async for foreign_trades in self.crawler.extract(link, **kwargs):
            for trade_data in foreign_trades:
                # Clean and parse data
                try:
                    # Assuming date format is dd/mm/yyyy. Convert to YYYY-MM-DD for database if needed,
                    # or rely on SQLAlchemy/driver to handle date string if format matches.
                    # However, for robustness, we should parse it.
                    # Let's keep it simple for now and pass as is, assuming DB handles it or it's standard.
                    # If format is dd/mm/yyyy, we might need to swap to yyyy-mm-dd.
                    # Let's convert "10/05/2023" to "2023-05-10"
                    date_str = trade_data["date"]
                    if "/" in date_str:
                        day, month, year = date_str.split("/")
                        date_iso = f"{year}-{month}-{day}"
                    else:
                        date_iso = date_str
                    
                    def parse_int(value: str) -> int | None:
                        if not value:
                            return None
                        clean_value = value.replace(",", "").replace(".", "").strip()
                        if not clean_value:
                            return None
                        try:
                            return int(clean_value)
                        except ValueError:
                            return None

                    foreign_room = parse_int(trade_data.get("foreign_room", ""))
                    buy_volume = parse_int(trade_data.get("buy_volume", ""))
                    sell_volume = parse_int(trade_data.get("sell_volume", ""))

                    await self.loader.upsert_by_date_and_stock_id(
                        stock_id=stock_id,
                        date=date_iso,
                        foreign_room=foreign_room,
                        buy_volume=buy_volume,
                        sell_volume=sell_volume,
                    )
                except Exception as e:
                    print(f"Error processing record {trade_data}: {e}")
                    continue
