# Cấu trúc thư mục Crawler theo DDD (tham khảo)

Chỉ mô tả **folder / file structure**. Chưa cần nội dung code.

---

## Tổng quan

- **Shared**: Base crawler dùng chung (Playwright lifecycle, template method).
- **Market Data (bounded context)**: Crawler cụ thể (Simplize) kế thừa base, domain entity + repository như hiện tại.

---

## Cấu trúc thư mục đề xuất

```
src/
├── shared/
│   ├── domain/
│   │   └── base/
│   │       └── entity.py                    # (đã có)
│   ├── application/
│   │   └── crawler/
│   │       ├── __init__.py
│   │       └── base_playwright_crawler.py   # Base class: launch, goto, close, hooks
│   └── infrastructure/
│       └── ...
│
└── market_data/
    ├── domain/
    │   ├── entity.py                         # (đã có) CompanyName
    │   └── repository.py                     # (đã có) CompanyNameRepositoryProtocol
    │
    ├── application/
    │   ├── crawler/
    │   │   ├── __init__.py
    │   │   ├── crawl_company_name.py         # Script chạy 1 lần (as-is hoặc gọi use case)
    │   │   └── simplize_company_crawler.py   # Kế thừa BasePlaywrightCrawler, logic Simplize
    │   └── use_case/                         # (tùy chọn)
    │       ├── __init__.py
    │       └── crawl_and_save_company_names.py  # Gọi crawler + repository
    │
    └── infrastructure/
        └── persistence/
            └── postgresql/
                └── company_name_repository.py  # (đã có)
```

---

## Vai trò từng phần (chỉ structure)

| Vị trí | Vai trò |
|--------|--------|
| `shared/application/crawler/base_playwright_crawler.py` | Base class: Playwright lifecycle, template method (hooks để subclass implement). |
| `market_data/application/crawler/simplize_company_crawler.py` | Crawler cụ thể: kế thừa base, implement URL, selectors, extract logic cho Simplize. |
| `market_data/application/crawler/crawl_company_name.py` | Entrypoint/script: gọi crawler (và có thể use case). |
| `market_data/application/use_case/crawl_and_save_company_names.py` | (Tùy chọn) Use case: chạy crawler → map sang entity → gọi repository. |

---

## Luồng gợi ý (theo layer)

```
crawl_company_name.py (entry)
    → CrawlAndSaveCompanyNamesUseCase (application)
        → SimplizeCompanyCrawler (application, kế thừa BasePlaywrightCrawler)
        → CompanyNameRepository (infrastructure, implement port từ domain)
```

Khi nào cần code từng file, có thể yêu cầu từng phần (ví dụ: chỉ base, chỉ simplize crawler, hoặc chỉ use case).

---

## Use case cho crawler – Code structure (chỉ structure, không code)

### Thư mục và file

```
market_data/
├── domain/
│   ├── entity.py
│   └── repository.py                    # CompanyNameRepositoryProtocol (port)
│
├── application/
│   ├── crawler/
│   │   ├── __init__.py
│   │   ├── crawl_company_name.py       # CrawlCompanyName (class crawler)
│   │   └── ...
│   └── use_case/
│       ├── __init__.py
│       └── crawl_and_save_company_names.py   # Use case: crawl → map → save
│
└── infrastructure/
    └── persistence/postgresql/
        └── company_name_repository.py  # Implement repository port
```

### Luồng phụ thuộc (dependency flow)

```
CrawlAndSaveCompanyNamesUseCase
    │
    ├── phụ thuộc vào: CrawlCompanyName (hoặc port CompanyListSource nếu tách)
    │   → trả về: list[dict] (raw) hoặc list[CompanyName]
    │
    └── phụ thuộc vào: CompanyNameRepositoryProtocol (port, từ domain)
        → implementation: CompanyNameRepository (infrastructure)
```

### Vai trò từng phần (structure)

| Thành phần | Vị trí | Vai trò (structure) |
|------------|--------|----------------------|
| Use case | `market_data/application/use_case/crawl_and_save_company_names.py` | 1) Gọi crawler (run + extract). 2) Map kết quả sang domain/entity (nếu cần). 3) Gọi repository (port) để lưu. Không biết chi tiết DB hay Playwright. |
| Crawler | `market_data/application/crawler/crawl_company_name.py` | Trả về dữ liệu thô (list dict) hoặc list entity. Use case inject crawler (constructor) hoặc import trực tiếp. |
| Repository port | `market_data/domain/repository.py` | Interface: create / get_by_stock_id, v.v. Use case chỉ gọi qua port. |
| Repository impl | `market_data/infrastructure/.../company_name_repository.py` | Implement port; được inject vào use case khi chạy (script/DI). |

### Entrypoint sau khi có use case

```
examples/example_crawl_company_name.py  (hoặc script/cli)
    → CrawlAndSaveCompanyNamesUseCase(...).execute()   # thay vì gọi crawler.run() trực tiếp
```

- Use case nhận **crawler** và **repository** (port) qua constructor; script khởi tạo concrete crawler + concrete repository rồi truyền vào.
