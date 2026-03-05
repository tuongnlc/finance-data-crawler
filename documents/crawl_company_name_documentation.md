# Tài liệu Crawl Company Name

Tài liệu này mô tả chi tiết về module `CrawlCompanyName`, được sử dụng để thu thập danh sách tên công ty và mã chứng khoán từ website Simplize.

## 1. Tổng quan

- **Mục đích**: Tự động hóa việc lấy danh sách các mã cổ phiếu, tên công ty và ngành kinh doanh trên Simplize.
- **Nguồn dữ liệu**: [Simplize - Cổ phiếu](https://simplize.vn/co-phieu)
- **Công nghệ sử dụng**: Python, Playwright (Automation), SQLAlchemy (PostgreSQL).

## 2. Kiến trúc (DDD Structure)

Module này tuân thủ cấu trúc Domain-Driven Design (DDD) của dự án:

- **Crawler (`src/market_data/application/crawler/crawl_company_name.py`)**: Logic cào dữ liệu từ Simplize sử dụng Playwright, bao gồm xử lý popup và phân trang.
- **Use Case (`src/market_data/application/use_case/crawl_company_name.py`)**: Điều phối luồng dữ liệu, kiểm tra trùng lặp và lưu trữ.
- **Repository (`src/market_data/infrastructure/persistence/postgresql/company_name_repository.py`)**: Giao tiếp với database PostgreSQL để lưu thông tin công ty.
- **Model (`src/shared/infrastructure/db/models.py`)**: Định nghĩa bảng `company_name`.

## 3. Chi tiết triển khai Crawler

### Lớp `CrawlCompanyName`
Kế thừa từ `BasePlaywrightCrawler`, chuyên biệt cho việc xử lý cấu trúc bảng dữ liệu của Simplize.

#### Các tính năng chính:
- **Xử lý Popup (`handle_popup`)**: Tự động phát hiện và đóng các hộp thoại quảng cáo/đăng ký xuất hiện khi tải trang.
- **Cuộn trang (`scroll_page`)**: Thực hiện cuộn trang xuống một vị trí cố định để kích hoạt việc tải dữ liệu hoặc đảm bảo các phần tử hiển thị đầy đủ.
- **Trích xuất dữ liệu (`_extract_single_page`)**: Sử dụng JavaScript chạy trong trình duyệt (`page.evaluate`) để lấy dữ liệu từ các dòng trong bảng (`tr.simplize-table-row`).
- **Phân trang (`crawl_pages`)**: 
    - Duyệt qua nhiều trang bằng cách click nút "Next" (`li.simplize-pagination-next`).
    - Giới hạn số lượng trang thông qua thuộc tính `scroll_limit` (mặc định là 42).

## 4. Quy trình xử lý dữ liệu (Use Case)

Lớp `CrawlCompanyNameUseCase` thực hiện:
1. **Kiểm tra trùng lặp**: Sử dụng một `set` (biến `seen`) để tránh xử lý trùng mã cổ phiếu trong cùng một phiên chạy.
2. **Kiểm tra Database**: Trước khi tạo mới, kiểm tra xem mã cổ phiếu đã tồn tại trong DB chưa bằng phương thức `get_by_stock_id`.
3. **Lưu trữ**: Chỉ thêm mới các công ty chưa có trong hệ thống.
4. **Quản lý Transaction**: Thực hiện `commit` sau mỗi trang dữ liệu để tối ưu hiệu năng và đảm bảo an toàn dữ liệu.

## 5. Hướng dẫn sử dụng

Tham khảo file ví dụ tại `examples/example_crawl_company_name.py`:

```python
import asyncio
from src.market_data.application.crawler.crawl_company_name import CrawlCompanyName
from src.market_data.application.use_case.crawl_company_name import CrawlCompanyNameUseCase
from src.market_data.infrastructure.persistence.postgresql import CompanyNameRepository

async def main():
    # Khởi tạo crawler (headless=False nếu muốn debug giao diện)
    crawler = CrawlCompanyName(headless=True)
    
    async for db in async_session_scope():
        repo = CompanyNameRepository(session=db)
        
        # Khởi tạo và thực thi use case
        use_case = CrawlCompanyNameUseCase(crawler, repo)
        result = await use_case.execute("https://simplize.vn/co-phieu")
        print(f"Kết quả crawl: {result}")

if __name__ == "__main__":
    asyncio.run(main())
```

## 6. Lưu ý kỹ thuật
- **Popup ID**: Hiện tại đang nhắm vào selector `#is63`, giá trị này có thể thay đổi theo thời gian trên Simplize.
- **JavaScript Evaluation**: Logic trích xuất chính nằm ở phía client (trình duyệt) để tăng tốc độ và độ chính xác khi parse HTML phức tạp.
- **Timeout**: Sử dụng `asyncio.wait_for` khi tương tác với DB để tránh treo tiến trình nếu kết nối mạng/DB gặp vấn đề.
