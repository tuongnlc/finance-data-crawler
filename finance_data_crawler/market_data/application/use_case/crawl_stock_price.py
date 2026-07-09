from typing import Any
from finance_data_crawler.market_data.domain.repository import StockPriceRepositoryProtocol
from finance_data_crawler.market_data.application.ports.crawl_data_port import CrawlDataPort


class CrawlStockPriceUseCase:
    def __init__(self, 
            crawler: CrawlDataPort, 
            loader: StockPriceRepositoryProtocol
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

        async for stock_prices in self.crawler.extract(link, **kwargs):
            for stock_data in stock_prices:
                # Clean and parse data
                try:
                    # Assuming date format is dd/mm/yyyy. Convert to YYYY-MM-DD for database if needed,
                    # or rely on SQLAlchemy/driver to handle date string if format matches.
                    # However, for robustness, we should parse it.
                    # Let's keep it simple for now and pass as is, assuming DB handles it or it's standard.
                    # If format is dd/mm/yyyy, we might need to swap to yyyy-mm-dd.
                    # Let's convert "10/05/2023" to "2023-05-10"
                    date_str = stock_data["date"]
                    if "/" in date_str:
                        day, month, year = date_str.split("/")
                        date_iso = f"{year}-{month}-{day}"
                    else:
                        date_iso = date_str
                    
                    open_price = float(stock_data["open_price"].replace(",", "").replace(".", ""))
                    high_price = float(stock_data["max_price"].replace(",", "").replace(".", ""))
                    low_price = float(stock_data["min_price"].replace(",", "").replace(".", ""))
                    close_price = float(stock_data["close_price"].replace(",", "").replace(".", ""))
                    volume = int(stock_data["volume"].replace(",", "").replace(".", ""))

                    await self.loader.upsert_by_date_and_stock_id(
                        stock_id=stock_id,
                        date=date_iso,
                        open_price=open_price,
                        high_price=high_price,
                        low_price=low_price,
                        close_price=close_price,
                        volume=volume,
                    )
                except Exception as e:
                    print(f"Error processing record {stock_data}: {e}")
                    continue
