from src.shared.application.crawler.base import BasePlaywrightCrawler
from typing import Any, Callable, ClassVar, TypeVar
from bs4 import BeautifulSoup
from typing import Any, AsyncIterator


TProduct = TypeVar("TProduct", bound=BasePlaywrightCrawler)

class CrawlBalanceSheetTypeOne(BasePlaywrightCrawler):
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
            "A. Tài sản lưu động và đầu tư ngắn hạn": "current_assets",
            "I. Tiền và các khoản tương đương tiền": "cash_and_cash_equivalents",
            "1. Tiền": "cash",
            "2. Các khoản tương đương tiền": "cash_equivalents",
            "II. Các khoản đầu tư tài chính ngắn hạn": "short_term_financial_investments",
            "1. Chứng khoán kinh doanh": "trading_securities",
            "2. Dự phòng giảm giá chứng khoán kinh doanh": "provision_for_diminution_in_value_of_trading_securities",
            "3. Đầu tư nắm giữ đến ngày đáo hạn": "held_to_maturity_investments_short_term",
            "III. Các khoản phải thu ngắn hạn": "short_term_receivables",
            "1. Phải thu ngắn hạn của khách hàng": "short_term_trade_receivables",
            "2. Trả trước cho người bán": "short_term_advances_to_suppliers",
            "3. Phải thu nội bộ ngắn hạn": "short_term_internal_receivables",
            "4. Phải thu theo tiến độ hợp đồng xây dựng": "receivables_construction_contract_progress",
            "5. Phải thu về cho vay ngắn hạn": "short_term_loan_receivables",
            "6. Phải thu ngắn hạn khác": "other_short_term_receivables",
            "7. Dự phòng phải thu ngắn hạn khó đòi": "provision_for_short_term_doubtful_debts",
            "IV. Tổng hàng tồn kho": "inventories",
            "1. Hàng tồn kho": "gross_inventories",
            "2. Dự phòng giảm giá hàng tồn kho": "provision_for_decline_in_value_of_inventories",
            "V. Tài sản ngắn hạn khác": "other_current_assets",
            "1. Chi phí trả trước ngắn hạn": "short_term_prepaid_expenses",
            "2. Thuế giá trị gia tăng được khấu trừ": "deductible_value_added_tax",
            "3. Thuế và các khoản phải thu Nhà nước": "taxes_and_other_receivables_from_state_budget",
            "4. Giao dịch mua bán lại trái phiếu chính phủ": "government_bond_repo_transactions_short_term",
            "5. Tài sản ngắn hạn khác": "other_current_assets_items",

            "B. Tài sản cố định và đầu tư dài hạn": "non_current_assets",
            "I. Các khoản phải thu dài hạn": "long_term_receivables",
            "1. Phải thu dài hạn của khách hàng": "long_term_trade_receivables",
            "2. Vốn kinh doanh tại các đơn vị trực thuộc": "working_capital_provided_to_subordinates",
            "3. Phải thu dài hạn nội bộ": "long_term_internal_receivables",
            "4. Phải thu về cho vay dài hạn": "long_term_loan_receivables",
            "5. Phải thu dài hạn khác": "other_long_term_receivables",
            "6. Dự phòng phải thu dài hạn khó đòi": "provision_for_long_term_doubtful_debts",
            "II. Tài sản cố định": "fixed_assets",
            "1. Tài sản cố định hữu hình": "tangible_fixed_assets",
            "Nguyên giá": "tangible_fixed_assets_cost",
            "Giá trị hao mòn lũy kế": "tangible_fixed_assets_accumulated_depreciation",
            "2. Tài sản cố định thuê tài chính": "finance_lease_fixed_assets",
            "Nguyên giá (2)": "finance_lease_fixed_assets_cost",
            "Giá trị hao mòn lũy kế (2)": "finance_lease_fixed_assets_accumulated_depreciation",
            "3. Tài sản cố định vô hình": "intangible_fixed_assets",
            "Nguyên giá (3)": "intangible_fixed_assets_cost",
            "Giá trị hao mòn lũy kế (3)": "intangible_fixed_assets_accumulated_amortization",
            "III. Bất động sản đầu tư": "investment_properties",
            "Nguyên giá (4)": "investment_properties_cost",
            "Giá trị hao mòn lũy kế (4)": "investment_properties_accumulated_depreciation",
            "IV. Tài sản dở dang dài hạn": "long_term_assets_in_progress",
            "1. Chi phí sản xuất, kinh doanh dở dang dài hạn": "long_term_work_in_progress",
            "2. chi phí xây dựng cơ bản dở dang": "construction_in_progress",
            "V. Các khoản đầu tư tài chính dài hạn": "long_term_financial_investments",
            "1. Đầu tư vào công ty con": "investments_in_subsidiaries",
            "2. Đầu tư vào công ty liên kết, liên doanh": "investments_in_associates_and_joint_ventures",
            "3. Đầu tư khác vào công cụ vốn": "equity_investments_in_other_entities",
            "4. Dự phòng giảm giá đầu tư tài chính dài hạn": "provision_for_long_term_financial_investments",
            "5. Đầu tư nắm giữ đến ngày đáo hạn": "held_to_maturity_investments_long_term",
            "VI. Tổng tài sản dài hạn khác": "other_non_current_assets",
            "1. Chi phí trả trước dài hạn": "long_term_prepaid_expenses",
            "2. Tài sản Thuế thu nhập hoãn lại": "deferred_corporate_income_tax_assets",
            "3. Tài sản dài hạn khác": "other_long_term_asset_items",
            "VII. Lợi thế thương mại": "goodwill",
            "TỔNG CỘNG TÀI SẢN": "total_assets",

            # ==================== NGUỒN VỐN (LIABILITIES AND EQUITY) ====================
            "A. Nợ phải trả": "total_liabilities",
            "I. Nợ ngắn hạn": "current_liabilities",
            "1. Vay và nợ thuê tài chính ngắn hạn": "short_term_borrowings_and_finance_lease_liabilities",
            "2. Vay và nợ dài hạn đến hạn phải trả": "current_portion_of_long_term_borrowings_and_liabilities",
            "3. Phải trả người bán ngắn hạn": "short_term_trade_payables",
            "4. Người mua trả tiền trước": "short_term_advances_from_customers",
            "5. Thuế và các khoản phải nộp nhà nước": "statutory_obligations_and_taxes_payable",
            "6. Phải trả người lao động": "payables_to_employees",
            "7. Chi phí phải trả ngắn hạn": "short_term_accrued_expenses",
            "8. Phải trả nội bộ ngắn hạn": "short_term_internal_payables",
            "9. Phải trả theo tiến độ kế hoạch hợp đồng xây dựng": "payables_construction_contract_progress",
            "10. Doanh thu chưa thực hiện ngắn hạn": "short_term_unearned_revenue",
            "11. Phải trả ngắn hạn khác": "other_short_term_payables",
            "12. Dự phòng phải trả ngắn hạn": "short_term_provisions",
            "13. Quỹ khen thưởng phúc lợi": "bonus_and_welfare_fund",
            "14. Quỹ bình ổn giá": "price_stabilization_fund",
            "15. Giao dịch mua bán lại trái phiếu chính phủ": "government_bond_repo_transactions_liabilities",
            "II. Nợ dài hạn": "non_current_liabilities",
            "1. Phải trả người bán dài hạn": "long_term_trade_payables",
            "2. Chi phí phải trả dài hạn": "long_term_accrued_expenses",
            "3. Phải trả nội bộ về vốn kinh doanh": "internal_payables_on_working_capital",
            "4. Phải trả nội bộ dài hạn": "long_term_internal_payables",
            "5. Phải trả dài hạn khác": "other_long_term_payables",
            "6. Vay và nợ thuê tài chính dài hạn": "long_term_borrowings_and_finance_lease_liabilities",
            "7. Trái phiếu chuyển đổi": "convertible_bonds",
            "8. Thuế thu nhập hoãn lại phải trả": "deferred_corporate_income_tax_liabilities",
            "9. Dự phòng trợ cấp mất việc làm": "provision_for_severance_allowances",
            "10. Dự phòng phải trả dài hạn": "long_term_provisions",
            "11. Doanh thu chưa thực hiện dài hạn": "long_term_unearned_revenue",
            "12. Quỹ phát triển khoa học và công nghệ": "science_and_technology_development_fund",

            "B. Nguồn vốn chủ sở hữu": "total_equity",
            "I. Vốn chủ sở hữu": "owners_equity",
            "1. Vốn đầu tư của chủ sở hữu": "contributed_charter_capital",
            "2. Thặng dư vốn cổ phần": "share_premium",
            "3. Quyền chọn chuyển đổi trái phiếu": "convertible_bond_options",
            "4. Vốn khác của chủ sở hữu": "other_owners_equity",
            "5. Cổ phiếu quỹ": "treasury_shares",
            "6. Chênh lệch đánh giá lại tài sản": "asset_revaluation_differences",
            "7. Chênh lệch tỷ giá hối đoái": "foreign_exchange_differences",
            "8. Quỹ đầu tư phát triển": "investment_and_development_fund",
            "9. Quỹ dự phòng tài chính": "financial_reserve_fund",
            "10. Quỹ khác thuộc vốn chủ sở hữu": "other_funds_belonging_to_equity",
            "11. Lợi nhuận sau thuế chưa phân phối": "undistributed_earnings_after_tax",
            "LNST chưa phân phối lũy kế đến cuối kỳ trước": "accumulated_retained_earnings_up_to_previous_period",
            "LNST chưa phân phối kỳ này": "retained_earnings_for_current_period",
            "12. Nguồn vốn đầu tư xây dựng cơ bản": "capital_expenditure_fund",
            "13. Quỹ hỗ trợ sắp xếp doanh nghiệp": "enterprise_rearrangement_support_fund",
            "14. Lợi ích của cổ đông không kiểm soát": "non_controlling_interests",
            "II. Nguồn kinh phí và quỹ khác": "other_resources_and_funds",
            "1. Nguồn kinh phí": "non_business_expenditure_source",
            "2. Nguồn kinh phí đã hình thành tài sản cố định": "expenditure_source_formed_fixed_assets",
            "3. Quỹ dự phòng trợ cấp mất việc làm": "job_loss_allowance_reserve_fund",
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