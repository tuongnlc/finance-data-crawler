from typing import Any, AsyncIterator
from src.shared.application.crawler.base import BasePlaywrightCrawler
import uuid


class CrawlFundGav(BasePlaywrightCrawler):
    async def _extract_single_page(self, fund_id: str, fund_code: str) -> AsyncIterator[list[dict[str, Any]]]:
        print(f"Clicked button: {fund_code}")

        # Sử dụng .first() để tránh lỗi strict mode
        button = self.page.get_by_text(fund_code).first
        await button.click()

        danh_muc_dau_tu_lon_button = self.page.get_by_text("Danh mục đầu tư lớn").first
        await danh_muc_dau_tu_lon_button.click()

        # # Đợi bảng dữ liệu load xong
        await self.page.wait_for_selector(".row-color", timeout=10000)

        # # Trích xuất dữ liệu từ các row
        fund_gavs = []
        rows = await self.page.locator(".row-color").all()
        for row in rows:
            # Trích xuất từng cột dựa trên index (0, 1, 2)
            # Sử dụng .first để tránh lỗi strict mode nếu có nhiều label lồng nhau
            stock_id = await row.locator("div").nth(0).locator("label").first.inner_text()
            nganh = await row.locator("div").nth(1).locator("label").first.inner_text()
            gav_str = await row.locator("div").nth(2).locator("label").first.inner_text()
            
            # Xử lý gav: xóa dấu phẩy, đổi dấu phẩy decimal thành dấu chấm nếu cần
            # Ví dụ: "1,234.56" -> "1234.56", "1.234,56" -> "1234.56"
            # Ở đây ta giả định format chuẩn quốc tế hoặc VN nhưng cần clean
            clean_gav = gav_str.strip().replace(",", "") # Xóa dấu phân cách nghìn
            try:
                gav_float = float(clean_gav)
            except ValueError:
                gav_float = 0.0
            
            fund_gavs.append({
                "id": uuid.uuid4(), # Trả về UUID object thay vì string
                "fund_id": fund_code,
                "stock_id": stock_id.strip(),
                "business_sector": nganh.strip(),
                "gav": gav_float
            })

            # # In kết quả dạng JSON để kiểm tra
        # print(json.dumps(fund_gavs, ensure_ascii=False, indent=2))
        
        # Click nút close (X) để đóng modal và quay lại danh sách quỹ
        # Sử dụng locator cụ thể hơn để tránh lỗi strict mode
        close_button = self.page.locator(".modal-header a").filter(has=self.page.locator("svg")).first
        if await close_button.is_visible():
            await close_button.click()
        
        yield fund_gavs
        await self.page.wait_for_timeout(1000)

    async def crawl_pages(self, link: str, **kwargs: Any) -> AsyncIterator[list[dict[str, Any]]]:
        await self._init_crawler()
        try:
            await self.page.goto(link, wait_until="domcontentloaded", timeout=self.navigation_timeout_ms)
            await self.page.wait_for_timeout(2000)
        
            buttons = {
                "dcds":"DCDS",
                "magef":"MAGEF",
                "bvfed":"BVFED",
                "vndaf":"VNDAF",
                "uveef":"UVEEF",
                "vcbf-bcf":"VCBF-BCF",
                "vcamdf":"VCAMDF",
                "BMFF": "BMFF",
                "TBLF": "TBLF",
                "DCDE": "DCDE",
                "EVESG": "EVESG",
                "VEOF": "VEOF",
                "VDEF": "VDEF",
                "DCAF": "DCAF",
                "MBVF": "MBVF",
                "VCBF-AIF": "VCBF-AIF",
                "MAFEQI": "MAFEQI",
                "VMEEF": "VMEEF",
                "VESAF": "VESAF",
                "TCGF": "TCGF",
                "SSISCA": "SSISCA",
                "PHVSF": "PHVSF",
                "VLGF": "VLGF",
                "VCBF-MGF": "VCBF-MGF",
                "BVPF": "BVPF",
                "NTPPF": "NTPPF",
                "LHCDF": "LHCDF",
                "GDEGF": "GDEGF",
                "KDEF": "KDEF",
                "RVPIF": "RVPIF"
            }
        
            for key, value in buttons.items():
                async for stocks in self._extract_single_page(fund_id=key, fund_code=value):
                    yield stocks
        except Exception as e:
            print(f"Lỗi khi load trang: {e}")
        finally:
            await self._close_crawler()

    async def extract(self, link: str, **kwargs: Any) -> list[dict[str, Any]]:
        return await self.crawl(link, **kwargs)
