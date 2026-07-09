from finance_data_crawler.shared.application.crawler.base import BasePlaywrightCrawler
from typing import Any, Callable, ClassVar, TypeVar
from bs4 import BeautifulSoup
from typing import Any, AsyncIterator


TProduct = TypeVar("TProduct", bound=BasePlaywrightCrawler)

class CrawlIncomeStatementTypeFour(BasePlaywrightCrawler):
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
            "Thu nhập lãi thuần": "net_interest_income",
            "Thu nhập từ lãi và các khoản thu nhập tương tự": "interest_and_similar_income",
            "Chi phí lãi và các chi phí tương tự": "interest_and_similar_expenses",
            "Lãi/Lỗ thuần từ hoạt động dịch vụ": "net_fee_and_commission_income",
            "Thu nhập từ hoạt động dịch vụ": "fee_and_commission_income",
            "Chi phí hoạt động dịch vụ": "fee_and_commission_expenses",
            "Lãi/Lỗ thuần từ hoạt động kinh doanh ngoại hối": "net_gain_loss_from_foreign_currency_and_gold_dealings",
            "Lãi/Lỗ thuần từ mua bán chứng khoán kinh doanh": "net_gain_loss_from_trading_securities",
            "Lãi/Lỗ thuần từ mua bán chứng khoán đầu tư": "net_gain_loss_from_investment_securities",
            "Lãi/Lỗ thuần từ hoạt động khác": "net_gain_loss_from_other_operating_activities",
            "Thu nhập từ hoạt động khác": "other_operating_income",
            "Chi phí hoạt động khác": "other_operating_expenses",
            "Thu nhập từ hoạt động góp vốn mua cổ phần": "income_from_long_term_investments",
            "Chi phí hoạt động": "operating_expenses",
            "Lợi nhuận từ HDKD trước chi phí dự phòng rủi ro tín dụng": "net_operating_profit_before_provision_for_credit_losses",
            "Chi phí dự phòng rủi ro tín dụng": "provision_expenses_for_credit_losses",
            "Tổng lợi nhuận trước thuế": "total_accounting_profit_before_tax",
            "Chi phí thuế TNDN": "corporate_income_tax_expense",
            "Chi phí thuế thu nhập hiện hành": "current_corporate_income_tax_expense",
            "Chi phí thuế TNDN giữ lại": "deferred_corporate_income_tax_expense",
            "Lợi nhuận sau thuế thu nhập doanh nghiệp": "net_profit_after_corporate_income_tax",
            "Lợi ích của cổ đông thiểu số và cổ tức ưu đãi": "non_controlling_interests_and_preferred_dividends",
            "LNST sau khi điều chỉnh Lợi ích của CĐTS và Cổ tức ưu đãi": "net_profit_parent"
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
