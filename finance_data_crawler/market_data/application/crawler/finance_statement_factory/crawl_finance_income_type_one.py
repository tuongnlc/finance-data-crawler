from src.shared.application.crawler.base import BasePlaywrightCrawler
from typing import Any, Callable, ClassVar, TypeVar
from bs4 import BeautifulSoup
from typing import Any, AsyncIterator


TProduct = TypeVar("TProduct", bound=BasePlaywrightCrawler)

class CrawlIncomeStatementTypeOne(BasePlaywrightCrawler):
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
            if value == "":
                return 0
            else:
                try:
                    return int(value)
                except:
                    return value

        else:
            raise ValueError(f"Expected str or int, got {type(value)}")

    async def _close_popup(self) -> None:
        close_button = self.page.get_by_role("button", name="Close").first
        try:
            await close_button.wait_for(state="visible", timeout=3000)
            await close_button.click()
        except Exception:
            pass

    async def _open_financial_statement(self) -> None:
        tai_chinh_tab = self.page.get_by_role("tab", name="Tài chính").first
        await tai_chinh_tab.wait_for(state="visible", timeout=5000)
        await tai_chinh_tab.click()
        await self.page.wait_for_timeout(1000)

        bao_cao_tai_chinh_tab = self.page.get_by_role("tab", name="Báo cáo tài chính").first
        await bao_cao_tai_chinh_tab.wait_for(state="visible", timeout=5000)
        await bao_cao_tai_chinh_tab.click()
        await self.page.wait_for_timeout(1000)

    def _map_keys(self, items: list[dict[str, Any]]) -> None:
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
            "21. Lợi nhuận sau thuế của cổ đông của công ty mẹ (19)-(20)": "net_profit_parent",
        }

        for item in items:
            for key, value in mapping_keyword.items():
                if key in item and key != value:
                    item[value] = item.pop(key)

    async def _extract_single_link(self, link: str) -> list[dict[str, Any]]:
        await self.page.goto(link, wait_until="domcontentloaded", timeout=self.navigation_timeout_ms)
        await self.page.wait_for_timeout(2000)

        await self._close_popup()
        await self._open_financial_statement()
        await self.scroll_page()

        await self.page.wait_for_selector("table.border-collapse")
        html_content = await self.page.content()

        soup = BeautifulSoup(html_content, "html.parser")
        table = soup.find("table", class_=lambda x: x and "border-collapse" in x)
        if not table:
            print("Không tìm thấy bảng dữ liệu!")
            raise ValueError("Không tìm thấy bảng dữ liệu!")

        stock_id = link.split("/")[-1]

        quarters: list[str] = []
        header_cells = table.find("thead").find_all("th")
        for th in header_cells:
            text = th.get_text(strip=True)
            if text.startswith("Q"):
                quarters.append(text)

        quarter_keys: list[tuple[str, int, str]] = []
        for q in quarters:
            quarter, year = q.split(" ")
            quarter_keys.append((stock_id, int(year), quarter))

        data_by_quarter: dict[tuple[str, int, str], dict[str, Any]] = {
            (sid, year, quarter): {"stock_id": sid, "year": year, "quarter": quarter}
            for sid, year, quarter in quarter_keys
        }

        rows = table.find("tbody").find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            if len(cells) < 3:
                continue

            indicator_name = cells[0].get_text(" ", strip=True)
            indicator_name = indicator_name.lstrip("-+ ").rstrip("-+ ")

            for index in range(len(quarters)):
                value_cell = cells[index + 2]
                value = value_cell.get_text(strip=True)

                sid, year, quarter = quarter_keys[index]
                data_by_quarter[(sid, year, quarter)][indicator_name] = value

        final_result = [data_by_quarter[key] for key in quarter_keys]
        self._map_keys(final_result)
        return final_result

    async def crawl_pages(self, links: list[str], **kwargs: Any) -> AsyncIterator[list[dict[str, Any]]]:
        await self._init_crawler()
        try:
            for link in links:
                print(f"Processing link: {link}")
                items = await self._extract_single_link(link)
                batch: list[dict[str, Any]] = [
                    {k: self._parse_string_to_int(v) for k, v in item.items()} for item in items
                ]
                print(f"Success extract from link: {link}")
                yield batch 
        finally:
            await self._close_crawler()

    async def extract(self, links: list[str], **kwargs: Any) -> AsyncIterator[list[dict[str, Any]]]:
        async for batch in self.crawl_pages(links, **kwargs):
            yield batch
