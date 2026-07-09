from finance_data_crawler.shared.application.crawler.base import BasePlaywrightCrawler
from typing import Any, Callable, ClassVar, TypeVar
from bs4 import BeautifulSoup
from typing import Any, AsyncIterator


TProduct = TypeVar("TProduct", bound=BasePlaywrightCrawler)

class CrawlBalanceSheetTypeFour(BasePlaywrightCrawler):
    def __init__(self, headless: bool = True) -> None:
        super().__init__(headless=headless)

    async def scroll_page(self):
        plus_icon = self.page.locator(
            "svg.lucide-plus, svg.lucide.lucide-plus, svg path[d='M12 5v14']"
        )

        class_like_button = self.page.locator(
            'button[class*="inline-flex"][class*="items-center"][class*="justify-center"]'
            '[class*="h-7"][class*="px-2"][class*="rounded-lg"]:not([disabled]), '
            '[role="button"][class*="inline-flex"][class*="items-center"][class*="justify-center"]'
            '[class*="h-7"][class*="px-2"][class*="rounded-lg"]:not([aria-disabled="true"])'
        )

        click_targets = class_like_button.filter(has=plus_icon)
        if await click_targets.count() == 0:
            click_targets = self.page.locator(
                'button:has(svg.lucide-plus), [role="button"]:has(svg.lucide-plus), a:has(svg.lucide-plus), '
                'button:has(svg.lucide.lucide-plus), [role="button"]:has(svg.lucide.lucide-plus), a:has(svg.lucide.lucide-plus), '
                'button:has(svg path[d="M12 5v14"]), [role="button"]:has(svg path[d="M12 5v14"]), a:has(svg path[d="M12 5v14"])'
            )

        for _ in range(self.scroll_limit):
            handles = await click_targets.element_handles()
            if not handles:
                break

            for handle in handles:
                try:
                    try:
                        await handle.scroll_into_view_if_needed()
                    except Exception:
                        pass

                    try:
                        await handle.click(timeout=1500)
                    except Exception:
                        try:
                            await handle.click(timeout=1500, force=True)
                        except Exception:
                            await self.page.evaluate(
                                """(el) => {
                                    if (!el) return;
                                    el.click?.();
                                    el.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
                                }""",
                                handle,
                            )
                    await self.page.wait_for_timeout(150)
                except Exception:
                    continue

            await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
            await self.page.wait_for_timeout(500)

        await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
        await self.page.wait_for_timeout(500)

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

    def _remove_blank_data(
        self,
        value: dict[str, Any] | list[dict[str, Any]],
        remove_keys: list[str],
    ) -> Any:
        """
            Remove blank data from the value if key in list of str value
        """
        if isinstance(value, list):
            for item in value:
                for key in remove_keys:
                    item.pop(key, None)
            return value

        for key in remove_keys:
            value.pop(key, None)
        return value

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

        can_doi_ke_toan_tag = self.page.get_by_role("tab", name="Cân đối kế toán").first
        await can_doi_ke_toan_tag.wait_for(state="visible", timeout=5000)
        await can_doi_ke_toan_tag.click()
        await self.page.wait_for_timeout(1000)

    def _map_keys(self, items: list[dict[str, Any]]) -> None:
        mapping_keyword = {
            # Thông tin cơ bản
            "stock_id": "stock_id",
            "year": "year",
            "quarter": "quarter",

            # ==================== TÀI SẢN (ASSETS) ====================
            "I. Tiền mặt, chứng từ có giá trị, ngoại tệ, kim loại quý, đá quý": "cash_gold_and_valuables",
            "II. Tiền gửi tại NHNN": "balances_with_the_sbv",
            "III. Tín phiếu kho bạc và các giấy tờ có giá ngắn hạn đủ tiêu chuẩn khác": "treasury_bills_and_eligible_short_term_valuable_papers",
            "IV. Tiền, vàng gửi tại các TCTD khác và cho vay các TCTD khác": "total_placements_with_and_loans_to_other_cis",
            "1. Tiền, Vàng gửi tại các TCTD khác": "placements_with_other_credit_institutions",
            "2. Cho vay các TCTD khác": "loans_to_other_credit_institutions",
            "3. Dự phòng rủi ro cho vay các TCTD khác": "allowance_for_loans_to_other_credit_institutions",
            "V. Chứng khoán kinh doanh": "total_trading_securities",
            "1. Chứng khoán kinh doanh": "trading_securities_gross",
            "2. Dự phòng giảm giá chứng khoán kinh doanh": "allowance_for_diminution_in_value_of_trading_securities",
            "VI. Các công cụ tài chính phái sinh và các tài sản tài chính khác": "derivative_financial_instruments_and_other_assets",
            "VII. Cho vay khách hàng": "total_loans_to_customers",
            "1. Cho vay khách hàng": "loans_to_customers_gross",
            "2. Dự phòng rủi ro cho vay khách hàng": "allowance_for_loans_to_customers",
            "VIII. Chứng khoán đầu tư": "total_investment_securities",
            "1. Chứng khoán đầu tư sẵn sàng để bán": "available_for_sale_investment_securities",
            "2. Chứng khoán đầu tư giữ đến ngày đáo hạn": "held_to_maturity_investment_securities",
            "3. Dự phòng giảm giá chứng khoán đầu tư": "allowance_for_diminution_in_value_of_investment_securities",
            "IX. Góp vốn đầu tư dài hạn": "total_long_term_investments",
            "1. Đầu tư vào công ty con": "investments_in_subsidiaries",
            "2. Góp vốn liên doanh": "investments_in_joint_ventures",
            "3. Đầu tư vào công ty liên kết": "investments_in_associates",
            "4. Đầu tư dài hạn khác": "other_long_term_investments",
            "5. Dự phòng giảm giá đầu tư dài hạn": "allowance_for_diminution_in_value_of_long_term_investments",
            "X. Tài sản cố định": "total_fixed_assets",
            "1. Tài sản cố định hữu hình": "tangible_fixed_assets",
            "Nguyên giá": "tangible_fixed_assets_cost",
            "Giá trị hao mòn lũy kế": "tangible_fixed_assets_accumulated_depreciation",
            "2. Tài sản cố định thuê tài chính": "finance_lease_fixed_assets",
            "Nguyên giá (2)": "finance_lease_fixed_assets_cost",
            "Giá trị hao mòn lũy kế (2)": "finance_lease_fixed_assets_accumulated_depreciation",
            "3. Tài sản cố định vô hình": "intangible_fixed_assets",
            "Nguyên giá (3)": "intangible_fixed_assets_cost",
            "Giá trị hao mòn lũy kế (3)": "intangible_fixed_assets_accumulated_amortization",
            "5. Chi phí XDCB dở dang": "construction_in_progress",
            "XI. Bất động sản đầu tư": "investment_properties",
            "Nguyên giá (4)": "investment_properties_cost",
            "Giá trị hao mòn lũy kế (4)": "investment_properties_accumulated_depreciation",
            "XII. Tài sản có khác": "total_other_assets",
            "1. Các khoản phải thu": "other_receivables",
            "2. Các khoản lãi, phí phải thu": "accrued_interest_and_fees_receivable",
            "3. Tài sản thuế TNDN hoãn lại": "deferred_corporate_income_tax_assets",
            "4. Tài sản có khác": "other_asset_items",
            "Trong đó: Lợi thế thương mại": "goodwill",
            "5. Các khoản dự phòng rủi ro cho các tài sản có nội bảng khác": "allowance_for_other_on_balance_sheet_assets",
            "TỔNG CỘNG TÀI SẢN": "total_assets",

            # ==================== NGUỒN VỐN (LIABILITIES AND EQUITY) ====================
            "I. Các khoản nợ chính phủ và NHNN": "borrowings_from_the_government_and_the_sbv",
            "II. Tiền gửi và cho vay các TCTD khác": "total_deposits_and_borrowings_from_other_cis",
            "1. Tiền gửi các tổ chức tín dụng khác": "deposits_from_other_credit_institutions",
            "2. Vay các TCTD khác": "borrowings_from_other_credit_institutions",
            "III. Tiền gửi khách hàng": "deposits_from_customers",
            "IV. Các công cụ tài chính phái sinh và các khoản nợ tài chính khác": "derivatives_and_other_fin_liab",
            "V. Vốn tài trợ, uỷ thác đầu tư mà ngân hàng chịu rủi ro": "entrusted_funds_and_grants",
            "VI. Phát hành giấy tờ có giá": "valuable_papers_issued",
            "VII. Các khoản nợ khác": "total_other_liabilities",
            "1. Các khoản lãi, phí phải trả": "accrued_interest_and_fees_payable",
            "2.Thuế TNDN hoãn lại phải trả": "deferred_corporate_income_tax_liabilities",
            "3. Các khoản phải trả và công nợ khác": "other_payables_and_liabilities",
            "4. Dự phòng rủi ro khác": "other_provisions",
            "VIII. Vốn và các quỹ": "total_capital_and_reserves",
            "1. Vốn của Tổ chức tín dụng": "credit_institution_capital",
            "Vốn điều lệ": "charter_capital",
            "Vốn đầu tư XDCB": "capital_expenditure_fund",
            "Thặng dư vốn cổ phần": "share_premium",
            "Cổ phiếu quỹ": "treasury_shares",
            "Cổ phiếu ưu đãi": "preferred_shares",
            "Vốn khác": "other_capital",
            "2. Quỹ của TCTD": "funds_of_the_credit_institution",
            "3. Chênh lệch tỷ giá hối đoái": "foreign_exchange_differences",
            "4. Chênh lệch đánh giá lại tài sản": "asset_revaluation_differences",
            "5. Lợi nhuận chưa phân phối/Lỗ lũy kế": "retained_earnings_or_accumulated_losses",
            "6. Nguồn kinh phí, Quỹ khác": "other_reserves_and_funds",
            "IX. Lợi ích của cổ đông thiểu số": "non_controlling_interests",
            "TỔNG CỘNG NGUỒN VỐN": "total_liabilities_and_equity",
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
            values_start = len(cells) - len(quarters)
            if values_start <= 0:
                continue

            indicator_name_raw = cells[0].get_text(" ", strip=True)
            indicator_name_raw = " ".join(indicator_name_raw.split())
            indicator_name = indicator_name_raw.lstrip("-+ ").rstrip()

            unique_indicator_name = indicator_name
            if quarter_keys:
                sid0, year0, quarter0 = quarter_keys[0]
                existing0 = data_by_quarter[(sid0, year0, quarter0)]
                if unique_indicator_name in existing0:
                    suffix = 2
                    while f"{indicator_name} ({suffix})" in existing0:
                        suffix += 1
                    unique_indicator_name = f"{indicator_name} ({suffix})"

            for index in range(len(quarters)):
                value_cell = cells[values_start + index]
                value = value_cell.get_text(strip=True)

                sid, year, quarter = quarter_keys[index]
                data_by_quarter[(sid, year, quarter)][unique_indicator_name] = value

        final_result = [data_by_quarter[key] for key in quarter_keys]
        self._remove_blank_data(final_result, ["TÀI SẢN", "NGUỒN VỐN"])
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