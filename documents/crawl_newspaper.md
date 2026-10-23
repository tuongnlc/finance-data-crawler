# Tài liệu Crawl Newspaper

Tài liệu này mô tả luồng thu thập tin tức (bài báo) từ các trang báo tài chính, gồm 2 bước: **lấy danh sách URL bài báo** và **crawl nội dung từng bài báo**.

## 1. Tổng quan

- **Mục đích**: Thu thập tiêu đề, ngày đăng, nội dung và tóm tắt của các bài báo tài chính/chứng khoán để phục vụ tìm kiếm ngữ nghĩa (Qdrant).
- **Nguồn dữ liệu**: vietstock.vn, cafef.vn, thoibaotaichinhvietnam.vn (khai báo tại `configs/crawl_newspaper_url.yaml`).
- **Công nghệ sử dụng**: Python, Playwright (lấy link bài báo), `newspaper3k` (parse nội dung), SQLAlchemy (PostgreSQL).

## 2. Kiến trúc (DDD Structure)

Module tuân thủ cấu trúc DDD của dự án:

- **Crawler URL (`finance_data_crawler/market_data/application/crawler/crawl_newspaper_url.py`)**: Class `CrawlNewspaperUrl`, dùng Playwright để lấy các link bài báo trên trang danh mục.
- **Crawler nội dung (`finance_data_crawler/market_data/application/crawler/crawl_newspaper.py`)**: Class `CrawlNewspaper`, dùng `newspaper3k` để bóc tách nội dung từng bài.
- **Use Case (`finance_data_crawler/market_data/application/use_case/crawl_newspaper_url.py` và `.../crawl_newspaper.py`)**: Điều phối luồng dữ liệu và ghi xuống database.
- **Repository (`finance_data_crawler/market_data/infrastructure/persistence/postgresql/`)**: `NewspaperUrlRepository` và `NewspaperRepository`, thao tác với 2 bảng tương ứng.
- **Model (`finance_data_crawler/shared/infrastructure/db/models.py`)**: Bảng `newspaper_url` và `newspaper`.

## 3. Bảng dữ liệu

**`newspaper_url`** — lưu danh sách link bài báo và trạng thái đã crawl:

| Cột | Kiểu | Ghi chú |
| --- | --- | --- |
| id | UUID | Khóa chính |
| newspaper_title | String(255) | Tiêu đề link (lấy từ thẻ `h2/h3/h4 a`) |
| newspaper_url | String(255) | URL bài báo (có index) |
| source | String(255) | URL trang danh mục nguồn |
| is_crawled | Int | 0 = chưa crawl, 1 = đã crawl |
| created_at | Date | Ngày tạo |

**`newspaper`** — lưu nội dung bài báo đã crawl:

| Cột | Kiểu | Ghi chú |
| --- | --- | --- |
| id | UUID | Khóa chính |
| newspaper_title | Text | Tiêu đề bài báo |
| newspaper_url | String(255) | URL bài báo |
| publish_date | Date | Ngày đăng (có thể null) |
| newspaper_content | Text | Nội dung bài báo |
| newspaper_summary | Text | Tóm tắt (do `newspaper3k` NLP sinh ra) |
| is_load_to_qdrant | Int | 0 = chưa nạp lên Qdrant |
| created_at | Date | Ngày tạo |

## 4. Quy trình xử lý

### Bước 1 — Lấy danh sách URL (`CrawlNewspaperUrlUseCase`)

1. `CrawlNewspaperUrl.run(link)` mở trang danh mục bằng Playwright, chờ 2 giây rồi trích xuất mọi thẻ `h2 a, h3 a, h4 a` (text, href, source).
2. Với mỗi link, gọi `NewspaperUrlRepository.upsert_by_newspaper_url` để lưu vào bảng `newspaper_url` với `is_crawled = 0`.

### Bước 2 — Crawl nội dung (`CrawlNewspaperUseCase`)

1. `query_newspaper_url()` lấy tất cả URL có `is_crawled = 0` từ bảng `newspaper_url`.
2. Với mỗi URL, gọi `CrawlNewspaper.extract(link)` → dùng `newspaper.article(link)` để lấy `title`, `publish_date`, `text`, sau đó gọi `article.nlp()` để sinh `summary`.
3. Ghi kết quả vào bảng `newspaper` qua `NewspaperRepository.upsert_by_newspaper_url` (upsert theo `newspaper_url`).
4. Cập nhật lại bảng `newspaper_url`: `is_crawled = 1`.

## 5. Cách chạy

### 5.1 Qua Airflow DAG

DAG `2026_06_10_newspapers_crawler` trong `orchestration/crawl_newspapers.py` gồm 2 task chạy tuần tự:

```
start_crawl_dag >> crawl_newspaper_url >> crawl_newspaper
```

- `crawl_newspaper_url_task` → `main(url="crawl_newspaper_url.yaml")` → `kind: newspaper_url`, crawl danh sách link.
- `crawl_newspaper_task` → `main(url="crawl_newspaper.yaml")` → `kind: newspaper`, `query_to_db: true`, crawl nội dung từ các link chưa xử lý.

Cả 2 đều gọi `orchestration/python_script/crawl_market_data_v1.py::main`, registry `CRAWLER_CLASS` sẽ map `kind` sang đúng cặp crawler/repository/use_case.

### 5.2 Chạy thủ công

Xem ví dụ tại `examples/example_crawl_newspaper.py`:

```python
from finance_data_crawler.market_data.application.crawler.crawl_newspaper import CrawlNewspaper
from finance_data_crawler.market_data.application.use_case.crawl_newspaper import CrawlNewspaperUseCase
from finance_data_crawler.market_data.infrastructure.persistence.postgresql.newspaper_url_repository import NewspaperUrlRepository
from finance_data_crawler.market_data.infrastructure.persistence.postgresql.newspaper_repository import NewspaperRepository

async for db in async_session_scope():
    extractor = NewspaperUrlRepository(session=db)
    loader = NewspaperRepository(session=db)
    crawler = CrawlNewspaper()
    use_case = CrawlNewspaperUseCase(extractor, crawler, loader)
    await use_case.execute()
```

Cấu hình nguồn crawl tại `configs/crawl_newspaper_url.yaml` (danh sách URL trang danh mục theo từng báo).

## 6. Lưu ý kỹ thuật

- `CrawlNewspaper.extract` là hàm **đồng bộ** (sync), trong khi `CrawlNewspaperUseCase` gọi `self.crawler.extract(link=url)` không `await` → đúng theo thiết kế hiện tại, khác với các crawler Playwright (async).
- Tham số `headless` trong `CrawlNewspaper.__init__` hiện **chưa được sử dụng** (không truyền vào `super().__init__`), cần lưu ý khi cấu hình qua registry vì `crawl_market_data_v1` luôn gọi `crawler_cls(headless=True)`.
- `CrawlNewspaperUrl._extract_single_page` dùng `asyncio.sleep(2)` để chờ trang render; nếu báo đổi giao diện (không còn `h2/h3/h4 a`) thì cần cập nhật selector.
- `publish_date` có thể `None`; use case đã xử lý bằng `.date() if ... else None`.
- `is_load_to_qdrant` mặc định là 0, là cờ đánh dấu cho bước nạp dữ liệu lên Qdrant (chưa nằm trong module này).
- `NewspaperUrlRepository.upsert_by_newspaper_url` sẽ tự xóa các bản ghi trùng `newspaper_url` nếu phát hiện nhiều hơn 1.
