from typing import Any, AsyncIterator
from src.shared.application.crawler.base import BasePlaywrightCrawler
import asyncio
import time
from bs4 import BeautifulSoup
from src.shared.infrastructure.db.models import IncomeStatementType1
from src.market_data.infrastructure.persistence.postgresql.final_statement_repository import FinalStatementRepository
from src.shared.infrastructure.db.connection import async_session_scope, get_async_engine

#load dot_env
import os
from dotenv import load_dotenv

load_dotenv()


class CrawlBCTC(BasePlaywrightCrawler):
    def __init__(self, headless: bool = True) -> None:
        super().__init__(headless=headless)

    async def scroll_page(self):
        await self.page.evaluate("window.scrollTo(1000, document.body.scrollHeight);")

    def _parse_string_to_int(self, value: Any) -> Any:
        if value is None:
            return 0

        if isinstance(value, (int, float)):
            return value

        if isinstance(value, str):
            if "," in value:
                return int(value.replace(",", ""))
            else:
                try:
                    return int(value)
                except:
                    return value

        # if value == "0":
        #     return 0
        else:
            raise ValueError(f"Expected str or int, got {type(value)}")

    async def extract(self, link: str, **kwargs: Any) -> list[dict[str, Any]]:
        await self._init_crawler()
        
        await self.page.goto(link, wait_until="domcontentloaded", timeout=self.navigation_timeout_ms)
        await self.page.wait_for_timeout(2000)

        #close x button
        close_button = self.page.get_by_role("button", name="Close").first
        try:
            await close_button.wait_for(state="visible", timeout=3000)
            await close_button.click()
        except Exception:
            pass

        # Click to Tai Chinh button
        tai_chinh_tab = self.page.get_by_role("tab", name="Tài chính").first
        await tai_chinh_tab.wait_for(state="visible", timeout=5000)
        await tai_chinh_tab.click()
        await self.page.wait_for_timeout(1000)

        #Click to KQKD button
        bao_cao_tai_chinh_tab = self.page.get_by_role("tab", name="Báo cáo tài chính").first
        await bao_cao_tai_chinh_tab.wait_for(state="visible", timeout=5000)
        await bao_cao_tai_chinh_tab.click()
        await self.page.wait_for_timeout(1000)

        await self.scroll_page()

        # Extract data
        await self.page.wait_for_selector("table.border-collapse")
        html_content = await self.page.content()

        soup = BeautifulSoup(html_content, "html.parser")
        table = soup.find("table", class_=lambda x: x and "border-collapse" in x)
        if not table:
            print("Không tìm thấy bảng dữ liệu!")
            raise ValueError("Không tìm thấy bảng dữ liệu!")

        # self.page.scolll

        # get stock_id
        stock_id = link.split("/")[-1]
        # 0. Lấy danh sách các quý từ thẻ <thead>

        # 1. Lấy danh sách các Quý từ thẻ <thead>
        quarters = []
        header_cells = table.find("thead").find_all("th")
        for th in header_cells:
            text = th.get_text(strip=True)
            if text.startswith("Q"):  # Lọc các cột như 'Q1 2025', 'Q2 2025'
                quarters.append(text)

        
        quarter_keys: list[tuple[int, str]] = []
        for q in quarters:
            quarter, year = q.split(" ")
            quarter_keys.append((stock_id, int(year), quarter))

        data_by_quarter: dict[tuple[str, int, str], dict[str, Any]] = {
            (stock_id, year, quarter): {"stock_id": stock_id, "year": year, "quarter": quarter} for stock_id, year, quarter in quarter_keys
        }

        # 2. Duyệt qua các dòng dữ liệu trong <tbody>
        rows = table.find("tbody").find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            if len(cells) < 3:
                continue  # Bỏ qua dòng thiếu dữ liệu

            # Lấy tên chỉ tiêu ở cột đầu tiên và làm sạch nút bấm thừa (+/-) nếu có
            indicator_name = cells[0].get_text(" ", strip=True)
            indicator_name = indicator_name.lstrip("-+ ").rstrip("-+ ")

            # Duyệt qua các cột số liệu tiếp theo, khớp vào đúng Quý dựa trên index
            for index, q in enumerate(quarters):
                # Ô số liệu thực tế bắt đầu từ cột thứ 3 (index trong HTML là: index_của_quý + 2)
                value_cell = cells[index + 2]
                value = value_cell.get_text(strip=True)

                # Đưa dữ liệu vào đúng vị trí Quý
                stock_id, year, quarter = quarter_keys[index]
                data_by_quarter[(stock_id, year, quarter)][indicator_name] = value

        final_result = [data_by_quarter[key] for key in quarter_keys]

        #mapping keyword
        mapping_keyword = {
            "stock_id": "stock_id",
            "year": "year",
            "quarter": "quarter",
            "1. Tổng doanh thu hoạt động kinh doanh": "gross_revenue",
            "2. Các khoản giảm trừ doanh thu": "revenue_deductions",
            "3. Doanh thu thuần (1)-(2)": "net_revenue",
            "4. Giá vốn hàng bán": "cost_of_goods_sold",
            "5. Lợi nhuận gộp (3)-(4)": "gross_profit",
            "6. Doanh thu hoạt động tài chính": "financial_income",
            "7. Chi phí tài chính": "financial_expenses",
            "Trong đó: Chi phí lãi vay": "interest_expense",
            "8. Phần lợi nhuận hoặc lỗ trong công ty liên kết liên doanh": "jv_associates_profit",
            "9. Chi phí bán hàng": "selling_expenses",
            "10. Chi phí quản lý doanh nghiệp": "general_and_administrative_expenses",
            "11. Lợi nhuận thuần từ hoạt động kinh doanh (5)+(6)-(7)+(8)-(9)-(10)": "net_operating_profit",
            "12. Thu nhập khác": "other_income",
            "13. Chi phí khác": "other_expenses",
            "14. Lợi nhuận khác (12)-(13)": "other_profit",
            "15. Tổng lợi nhuận kế toán trước thuế (11)+(14)": "total_accounting_profit_before_tax",
            "16. Chi phí thuế TNDN hiện hành": "current_corporate_income_tax_expense",
            "17. Chi phí thuế TNDN hoãn lại": "deferred_corporate_income_tax_expense",
            "18. Chi phí thuế TNDN (16)+(17)": "corporate_income_tax_expense",
            "19. Lợi nhuận sau thuế thu nhập doanh nghiệp (15)-(18)": "net_profit_after_corporate_income_tax",
            "20. Lợi nhuận sau thuế của cổ đông không kiểm soát": "non_controlling_interests",
            "21. Lợi nhuận sau thuế của cổ đông của công ty mẹ (19)-(20)": "net_profit_parent"
        }

        #rename keyword
        for item in final_result:
            for key, value in mapping_keyword.items():
                item[value] = item.pop(key)
            
            # parse string to init
        print(final_result)

        # parse string to int
        # for item in final_result:
        #     for key, value in item.items():
        #         if isinstance(value, str):
        #             item[key] = self._parse_string_to_int(value)

        

        #insert to postgresql
        try:
            async for db in async_session_scope():
                _model_path = 'src.shared.infrastructure.db.models.IncomeStatementType1'

                final_repo = FinalStatementRepository(
                    model_path=_model_path,
                    session=db
                )
                for item in final_result:
                    data = {k: self._parse_string_to_int(v) for k, v in item.items()}
                    await final_repo.upsert_by_year_quarter_stock_id(
                        stock_id=item["stock_id"],
                        year=item["year"],
                        quarter=item["quarter"],
                        data=data,
                    )
        except Exception as e:
            print(f"Error inserting data to PostgreSQL: {e}")
            raise


test_crawler = CrawlBCTC(
    headless=False,
)

test_link = 'https://fireant.vn/ma-chung-khoan/MWG'

async def test_extract():
    data = await test_crawler.extract(test_link)
    time.sleep(5)
    # print(f"Extracted {len(data)} records")
    
if __name__ == "__main__":
    asyncio.run(test_extract())
