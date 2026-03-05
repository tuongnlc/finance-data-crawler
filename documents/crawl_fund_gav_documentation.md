# Tài liệu Crawl Fund GAV

Tài liệu này mô tả chi tiết về module `CrawlFundGav`, được sử dụng để thu thập dữ liệu Giá trị Tài sản ròng (GAV) của các quỹ từ website FMarket.

## 1. Tổng quan

- **Mục đích**: Tự động hóa việc lấy dữ liệu danh mục đầu tư và GAV của các quỹ mở trên FMarket.
- **Nguồn dữ liệu**: [FMarket - Danh sách quỹ](https://fmarket.vn/trade/account/investor/market/fund)
- **Công nghệ sử dụng**: Python, Playwright (Automation), SQLAlchemy (PostgreSQL).

## 2. Kiến trúc (DDD Structure)

Module này được thiết kế theo mô hình Domain-Driven Design (DDD):

- **Crawler (`src/market_data/application/crawler/crawl_fund_gav.py`)**: Chứa logic cào dữ liệu thô từ web sử dụng Playwright.
- **Use Case (`src/market_data/application/use_case/crawl_fund_gav.py`)**: Điều phối luồng xử lý: gọi crawler -> xử lý dữ liệu -> lưu vào repository.
- **Repository (`src/market_data/infrastructure/persistence/postgresql/fund_gav_repository.py`)**: Thực hiện các thao tác lưu trữ dữ liệu vào database PostgreSQL.
- **Model (`src/shared/infrastructure/db/models.py`)**: Định nghĩa cấu trúc bảng `fund_gav`.

## 3. Chi tiết triển khai Crawler

### Lớp `CrawlFundGav`
Kế thừa từ `BasePlaywrightCrawler` để tận dụng các phương thức khởi tạo và đóng trình duyệt.

#### Các phương thức chính:
- `_extract_single_page(fund_id, fund_code)`: 
    - Click vào từng quỹ cụ thể theo `fund_code`.
    - Mở tab "Danh mục đầu tư lớn".
    - Trích xuất các cột: Mã chứng khoán (`stock_id`), Ngành (`business_sector`), và GAV.
    - Xử lý định dạng số GAV (xóa dấu phẩy).
    - Trả về một generator chứa danh sách các dict dữ liệu.
- `crawl_pages(link, **kwargs)`:
    - Khởi tạo trình duyệt.
    - Duyệt qua danh sách các mã quỹ được định nghĩa sẵn (DCDS, MAGEF, BVFED, ...).
    - Gọi `_extract_single_page` cho từng mã.

## 4. Quy trình xử lý dữ liệu (Use Case)

Lớp `CrawlFundGavUseCase` thực hiện các bước sau:
1. **Truncate dữ liệu cũ**: Xóa toàn bộ dữ liệu trong bảng `fund_gav` trước khi crawl mới để đảm bảo tính cập nhật.
2. **Crawl**: Lặp qua các trang dữ liệu từ crawler.
3. **Save**: Lưu từng bản ghi vào database thông qua repository.
4. **Transaction**: Thực hiện `commit` sau mỗi trang (hoặc mỗi quỹ) để đảm bảo dữ liệu được lưu an toàn.

## 5. Hướng dẫn sử dụng

Bạn có thể tham khảo file ví dụ tại `examples/example_crawl_fund_gav.py`:

```python
import asyncio
from src.market_data.application.crawler.crawl_fund_gav import CrawlFundGav
from src.market_data.application.use_case.crawl_fund_gav import CrawlFundGavUseCase
from src.market_data.infrastructure.persistence.postgresql import FundGavRepository

async def main():
    # Khởi tạo crawler (headless=False để xem quá trình chạy)
    crawler = CrawlFundGav(headless=False)
    
    # Khởi tạo repository với session db
    async for db in async_session_scope():
        loader = FundGavRepository(session=db)
        
        # Khởi tạo và chạy use case
        use_case = CrawlFundGavUseCase(crawler, loader)
        result = await use_case.execute("https://fmarket.vn/trade/account/investor/market/fund")
        print(f"Kết quả: {result}")

if __name__ == "__main__":
    asyncio.run(main())
```

## 6. Lưu ý kỹ thuật
- **Strict Mode**: Sử dụng `.first` trong Playwright locators để tránh lỗi khi có nhiều phần tử trùng khớp.
- **Timeout**: Đợi bảng dữ liệu load xong (`wait_for_selector(".row-color")`) trước khi trích xuất.
- **Data Cleaning**: GAV được chuyển đổi sang kiểu `float` sau khi loại bỏ ký tự phân cách nghìn.
