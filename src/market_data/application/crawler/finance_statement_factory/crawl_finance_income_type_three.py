from src.shared.application.crawler.base import BasePlaywrightCrawler
from typing import Any, TypeVar
from bs4 import BeautifulSoup
from typing import Any, AsyncIterator


TProduct = TypeVar("TProduct", bound=BasePlaywrightCrawler)

class CrawlIncomeStatementTypeThree(BasePlaywrightCrawler):
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
            # Thông tin chung (Tái sử dụng)
            "stock_id": "stock_id",
            "year": "year",
            "quarter": "quarter",

            # I. DOANH THU HOẠT ĐỘNG (OPERATING REVENUE)
            "I. DOANH THU HOẠT ĐỘNG": "operating_revenue",
            "1.1. Lãi từ các tài sản tài chính ghi nhận thông qua lãi/lỗ (FVTPL)": "gain_from_fvtpl_financial_assets",
            "a. Lãi bán các tài sản tài chính": "gain_on_disposal_of_financial_assets",
            "b. Chênh lệch tăng đánh giá lại các TSTC thông qua lãi/lỗ": "positive_revaluation_difference_of_fvtpl_financial_assets",
            "c. Cổ tức, tiền lãi phát sinh từ tài sản tài chính PVTPL": "dividends_and_interest_from_fvtpl_financial_assets",
            "1.2. Lãi từ các khoản đầu tư nắm giữ đến ngày đáo hạn (HTM)": "interest_from_htm_investments",
            "1.3. Lãi từ các khoản cho vay và phải thu": "interest_from_loans_and_receivables",
            "1.4. Lãi từ các tài sản tài chính sẵn sàng để bán (AFS)": "gain_from_afs_financial_assets",
            "1.5. Lãi từ các công cụ phái sinh phòng ngừa rủi ro": "gain_from_hedging_derivatives",
            "1.6. Doanh thu môi giới chứng khoán": "brokerage_revenue",
            "1.7. Doanh thu bảo lãnh, đại lý phát hành chứng khoán": "underwriting_and_agency_revenue",
            "1.8. Doanh thu tư vấn": "advisory_revenue",
            "1.9. Doanh thu hoạt động nhận ủy thác, đấu giá": "custody_and_auction_revenue",
            "1.10. Doanh thu lưu ký chứng khoán": "securities_depository_revenue",
            "1.11. Thu nhập hoạt động khác": "other_operating_income", # Tái sử dụng từ điển Bank
            "Cộng doanh thu hoạt động": "total_operating_revenue",

            # II. CHI PHÍ HOẠT ĐỘNG (OPERATING EXPENSES)
            "II. CHI PHÍ HOẠT ĐỘNG": "operating_expenses", # Tái sử dụng từ điển Bank
            "2.1. Lỗ các tài sản tài chính ghi nhận thông qua lãi/lỗ (FVTPL)": "loss_from_fvtpl_financial_assets",
            "a. Lỗ bán các tài sản tài chính": "loss_on_disposal_of_financial_assets",
            "b. Chênh lệch giảm đánh giá lại các TSTC thông qua lãi/lỗ": "negative_revaluation_difference_of_fvtpl_financial_assets",
            "c. c.Chi phí giao dịch mua các tài sản tài chính FVTPL": "transaction_costs_of_purchasing_fvtpl_financial_assets",
            "2.2. Lỗ các khoản đầu tư nắm giữ đến ngày đáo hạn (HTM)": "loss_from_htm_investments",
            "2.3. Chi phí lãi vay, lỗ từ các khoản cho vay và phải thu": "interest_expenses_and_loss_from_loans_and_receivables",
            "2.4. Lỗ bán các tài sản tài chính sẵn sàng để bán (AFS)": "loss_on_disposal_of_afs_financial_assets",
            "2.5. Lỗ từ các tài sản tài chính phái sinh phòng ngừa rủi ro": "loss_from_hedging_derivatives",
            "2.6. Chi phí hoạt động tự doanh": "proprietary_trading_expenses",
            "2.7. Chi phí môi giới chứng khoán": "brokerage_expenses",
            "2.8. Chi phí hoạt động bảo lãnh, đại lý phát hành chứng khoán": "underwriting_and_agency_expenses",
            "2.9. Chi phí tư vấn": "advisory_expenses",
            "2.10. Chi phí hoạt động đấu giá, ủy thác": "custody_and_auction_expenses",
            "2.11. Chi phí lưu ký chứng khoán": "securities_depository_expenses",
            "2.12. Chi phí khác": "other_expenses", # Tái sử dụng từ điển DN
            "Trong đó: Chi phí sửa lỗi giao dịch chứng khoán, lỗi khác": "of_which_error_correction_expenses",
            "Cộng chi phí hoạt động": "total_operating_expenses",

            # III. DOANH THU HOẠT ĐỘNG TÀI CHÍNH
            "III. DOANH THU HOẠT ĐỘNG TÀI CHÍNH": "financial_income", # Tái sử dụng từ điển DN
            "3.1. Chênh lệch lãi tỷ giá hối đoái đã và chưa thực hiện": "realized_and_unrealized_foreign_exchange_gains",
            "3.2. Doanh thu, dự thu cổ tức, lãi tiền gửi không cố định phát sinh trong kỳ": "dividends_and_interest_income_from_deposits",
            "3.3. Lãi bán, thanh lý các khoản đầu tư vào công ty con, liên kết, liên doanh": "gains_from_disposal_of_subsidiaries_and_associates",
            "3.4. Doanh thu khác về đầu tư": "other_investment_income",
            "Cộng doanh thu hoạt động tài chính": "total_financial_income",

            # IV. CHI PHÍ TÀI CHÍNH
            "IV. CHI PHÍ TÀI CHÍNH": "financial_expenses", # Tái sử dụng từ điển DN
            "4.1. Chênh lệch lỗ tỷ giá hối đoái đã và chưa thực hiện": "realized_and_unrealized_foreign_exchange_losses",
            "4.2. Chi phí lãi vay": "interest_expense", # Tái sử dụng từ điển DN
            "4.3. Lỗ bán, thanh lý các khoản đầu tư vào công ty con, liên kết, liên doanh": "losses_from_disposal_of_subsidiaries_and_associates",
            "4.4. Chi phí đầu tư khác": "other_investment_expenses",
            "Cộng chi phí tài chính": "total_financial_expenses",

            # V & VI. CHI PHÍ BÁN HÀNG & QUẢN LÝ
            "V. CHI BÁN HÀNG": "selling_expenses", # Tái sử dụng từ điển DN
            "VI. CHI PHÍ QUẢN LÝ CÔNG TY CHỨNG KHOÁN": "general_and_administrative_expenses", # Tái sử dụng từ điển DN

            # VII. KẾT QUẢ HOẠT ĐỘNG
            "VII. KẾT QUẢ HOẠT ĐỘNG": "net_operating_profit", # Tái sử dụng từ điển DN (Lợi nhuận thuần từ HĐKD)

            # VIII. THU NHẬP KHÁC VÀ CHI PHÍ KHÁC
            "VIII. THU NHẬP KHÁC VÀ CHI PHÍ KHÁC": "other_income_and_expenses",
            "8.1. Thu nhập khác": "other_income", # Tái sử dụng từ điển DN
            "8.2. Chi phí khác": "other_expenses", # Tái sử dụng từ điển DN
            "Cộng kết quả hoạt động khác": "other_profit", # Tái sử dụng từ điển DN (Lợi nhuận khác)

            # IX. TỔNG LỢI NHUẬN KẾ TOÁN TRƯỚC THUẾ
            "IX. TỔNG LỢI NHUẬN KẾ TOÁN TRƯỚC THUẾ": "total_accounting_profit_before_tax", # Tái sử dụng từ điển DN/Bank
            "9.1. Lợi nhuận đã thực hiện": "realized_profit",
            "9.2. Lợi nhuận chưa thực hiện": "unrealized_profit",

            # X. CHI PHÍ THUẾ TNDN
            "X. CHI PHÍ THUẾ TNDN": "corporate_income_tax_expense", # Tái sử dụng từ điển Bank
            "10.1. Chi phí thuế TNDN hiện hành": "current_corporate_income_tax_expense", # Tái sử dụng từ điển DN/Bank
            "10.2. Chi phí thuế TNDN hoãn lại": "deferred_corporate_income_tax_expense", # Tái sử dụng từ điển DN/Bank

            # XI. LỢI NHUẬN KẾ TOÁN SAU THUẾ TNDN
            "XI. LỢI NHUẬN KẾ TOÁN SAU THUẾ TNDN": "net_profit_after_corporate_income_tax", # Tái sử dụng từ điển DN/Bank
            "11.1. Lợi nhuận sau thuế phân bổ cho chủ sở hữu": "net_profit_parent", # Tái sử dụng từ điển DN (Lợi nhuận cổ đông công ty mẹ)
            "11.2. Lợi nhuận sau thuế trích các Quỹ dự trữ điều lệ, Quỹ Dự phòng tài chính và rủi ro nghề nghiệp theo quy định của Điều lệ Công ty là %)": "net_profit_appropriated_to_reserves",
            "11.3. Lợi nhuận thuần phân bổ cho lợi ích của cổ đông không kiểm soát": "non_controlling_interests", # Tái sử dụng từ điển DN

            # XII. THU NHẬP (LỖ) TOÀN DIỆN KHÁC SAU THUẾ TNDN (OCI)
            "XII. THU NHẬP (LỖ) TOÀN DIỆN KHÁC SAU THUẾ TNDN": "other_comprehensive_income_after_tax",
            "12.1. Lãi/(Lỗ) từ đánh giá lại các các khoản đầu tư giữ đến ngày đáo hạn": "gain_loss_from_revaluation_of_htm_investments",
            "12.2.Lãi/(Lỗ) từ đánh giá lại các tài sản tài chính sẵn sàng để bán": "gain_loss_from_revaluation_of_afs_financial_assets",
            "12.3. Lãi (lỗ) toàn diện khác được chia từ hoạt động đầu tư vào công ty con, công ty liên kết, liên doanh": "share_of_other_comprehensive_income_of_subsidiaries_and_associates",
            "12.4. Lãi/(Lỗ) từ đánh giá lại các công cụ tài chính phái sinh": "gain_loss_from_revaluation_of_derivative_financial_instruments",
            "12.5. Lãi/(lỗ) chênh lệch tỷ giá của hoạt động tại nước ngoài": "foreign_exchange_differences_from_foreign_operations",
            "12.6. Lãi, lỗ từ các khoản đầu tư vào công ty con, công ty liên kết, liên doanh chưa chia": "unallocated_gains_losses_from_subsidiaries_and_associates",
            "12.7. Lãi, lỗ đánh giá công cụ phái sinh": "gain_loss_on_derivatives_valuation",
            "12.8. Lãi, lỗ đánh giá lại tài sản cố định theo mô hình giá trị hợp lý": "gain_loss_from_revaluation_of_fixed_assets",
            "Tổng thu nhập toàn diện": "total_comprehensive_income",
            "Thu nhập toàn diện phân bổ cho chủ sở hữu": "comprehensive_income_attributable_to_owners",
            "Thu nhập toàn diện phân bổ cho cổ đông không nắm quyền kiểm soát": "comprehensive_income_attributable_to_non_controlling_interests",

            # XIII. THU NHẬP THUẦN TRÊN CỔ PHIẾU (EPS)
            "XIII. THU NHẬP THUẦN TRÊN CỔ PHIẾU PHỔ THÔNG": "earnings_per_share",
            "13.1. Lãi cơ bản trên cổ phiếu (Đồng/1 cổ phiếu)": "basic_earnings_per_share",
            "13.2. Thu nhập pha loãng trên cổ phiếu (Đồng/1 cổ phiếu)": "diluted_earnings_per_share"
        }

        for item in items:
            for key, value in mapping_keyword.items():
                if key in item and key != value:
                    item[value] = item.pop(key)

        #Remove some items
        for item in items:
            if "Tổng thu nhập toàn diện" in item:
                items.remove(item)

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
