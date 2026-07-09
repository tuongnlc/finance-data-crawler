from finance_data_crawler.shared.application.crawler.base import BasePlaywrightCrawler
from typing import Any, Callable, ClassVar, TypeVar
from bs4 import BeautifulSoup
from typing import Any, AsyncIterator


TProduct = TypeVar("TProduct", bound=BasePlaywrightCrawler)

class CrawlCashFlowStatementTypeOne(BasePlaywrightCrawler):
    def __init__(self, headless: bool = True) -> None:
        super().__init__(headless=headless)

    async def scroll_page(self): #same with crawl balance sheet
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

        bao_cao_luu_chuyen_tien_te_tag = self.page.get_by_role("tab", name="LCTT gián tiếp").first
        await bao_cao_luu_chuyen_tien_te_tag.wait_for(state="visible", timeout=5000)
        await bao_cao_luu_chuyen_tien_te_tag.click()
        await self.page.wait_for_timeout(1000)

    def _map_keys(self, items: list[dict[str, Any]]) -> None:
        mapping_keyword = {
            # Thông tin cấu trúc dữ liệu
            "stock_id": "stock_id",
            "year": "year",
            "quarter": "quarter",

            # ==================== I. DÒNG TIỀN TỪ HOẠT ĐỘNG KINH DOANH ====================
            "1. Lợi nhuận trước thuế": "profit_before_tax",
            "2. Điều chỉnh cho các khoản": "total_adjustments",
            "Khấu hao TSCĐ": "depreciation_of_fixed_assets",
            "Các khoản dự phòng": "provisions",
            "Lợi nhuận thuần từ đầu tư vào công ty liên kết": "share_of_profit_from_associates",
            "Xóa sổ tài sản cố định (thuần)": "write_offs_of_fixed_assets",
            "Lãi, lỗ chênh lệch tỷ giá hối đoái chưa thực hiện": "unrealized_foreign_exchange_changes",
            "Lãi, lỗ từ thanh lý TSCĐ": "gain_loss_from_disposal_of_fixed_assets",
            "Lãi, lỗ từ hoạt động đầu tư": "gain_loss_from_investing_activities",
            "Lãi tiền gửi": "interest_income_from_deposits",
            "Thu nhập lãi": "interest_income",
            "Chi phí lãi vay": "interest_expense",
            "Các khoản chi trực tiếp từ lợi nhuận": "direct_appropriations_from_profit",
            "3. Lợi nhuận từ hoạt động kinh doanh trước thay đổi vốn lưu động": "operating_profit_before_working_capital_change",
            "Tăng, giảm các khoản phải thu": "change_in_receivables",
            "Tăng, giảm hàng tồn kho": "change_in_inventory",
            "Tăng, giảm các khoản phải trả (Không kể lãi vay phải trả, thuế thu nhập doanh nghiệp phải nộp)": "change_in_payables_excl_tax_and_interest",
            "Tăng giảm chi phí trả trước": "change_in_prepaid_expenses",
            "Tăng giảm tài sản ngắn hạn khác": "change_in_other_current_assets",
            "Tiền lãi vay phải trả": "interest_paid",
            "Thuế thu nhập doanh nghiệp đã nộp": "corporate_income_tax_paid",
            "Tiền thu khác từ hoạt động kinh doanh": "other_operating_cash_receipts",
            "Tiền chi khác từ hoạt động kinh doanh": "other_operating_cash_payments",
            "Lưu chuyển tiền thuần từ hoạt động kinh doanh": "net_cash_flows_from_operating_activities",

            # ==================== II. DÒNG TIỀN TỪ HOẠT ĐỘNG ĐẦU TƯ ====================
            "1. Tiền chi để mua sắm, xây dựng TSCĐ và các tài sản dài hạn khác": "cash_paid_for_fixed_assets",
            "2. Tiền thu từ thanh lý, nhượng bán TSCĐ và các tài sản dài hạn khác": "cash_received_from_disposal_of_fixed_assets",
            "3. Tiền chi cho vay, mua các công cụ nợ của đơn vị khác": "cash_paid_for_loans_and_debt_instruments",
            "4. Tiền thu hồi cho vay, bán lại các công cụ nợ của các đơn vị khác": "cash_received_from_loans_and_debt_instruments",
            "5. Đầu tư góp vốn vào công ty liên doanh liên kết": "investments_in_joint_ventures_and_associates",
            "6. Chi đầu tư ngắn hạn": "cash_paid_for_short_term_investments",
            "7. Tiền chi đầu tư góp vốn vào đơn vị khác": "cash_paid_for_equity_investments",
            "8. Tiền thu hồi đầu tư góp vốn vào đơn vị khác": "cash_received_from_equity_investments",
            "9. Lãi tiền gửi đã thu": "interest_received_from_deposits",
            "10. Tiền thu lãi cho vay, cổ tức và lợi nhuận được chia": "interest_and_dividends_received",
            "11. Tiền chi mua lại phần vốn góp của các cổ đông thiểu số": "cash_paid_to_buy_back_minority_interests",
            "Lưu chuyển tiền thuần từ hoạt động đầu tư": "net_cash_flows_from_investing_activities",

            # ==================== III. DÒNG TIỀN TỪ HOẠT ĐỘNG TÀI CHÍNH ====================
            "1. Tiền thu từ phát hành cổ phiếu, nhận vốn góp của chủ sở hữu": "cash_received_from_issuing_shares",
            "2. Tiền chi trả vốn góp cho các chủ sở hữu, mua lại cổ phiếu của doanh nghiệp đã phát hành": "cash_paid_for_share_buybacks",
            "3. Tiền vay ngắn hạn, dài hạn nhận được": "cash_received_from_borrowings",
            "4. Tiền chi trả nợ gốc vay": "cash_repayments_of_borrowings",
            "5. Tiền chi trả nợ thuê tài chính": "cash_repayments_of_finance_lease_liabilities",
            "6. Tiền chi khác từ hoạt động tài chính": "other_financing_cash_payments",
            "7. Tiền chi trả từ cổ phần hóa": "payments_for_privatization",
            "8. Cổ tức, lợi nhuận đã trả cho chủ sở hữu": "dividends_paid_to_owners",
            "9. Vốn góp của các cổ đông thiểu số vào các công ty con": "minority_capital_contribution_into_subsidiaries",
            "10. Chi tiêu quỹ phúc lợi xã hội": "payments_for_welfare_and_social_funds",
            "Lưu chuyển tiền thuần từ hoạt động tài chính": "net_cash_flows_from_financing_activities",

            # ==================== TỔNG KẾT CUỐI KỲ ====================
            "Lưu chuyển tiền thuần trong kỳ": "net_change_in_cash",
            "Tiền và tương đương tiền đầu kỳ": "cash_and_cash_equivalents_at_start_of_period",
            "Ảnh hưởng của thay đổi tỷ giá hối đoái quy đổi ngoại tệ": "effect_of_exchange_rate_changes",
            "Tiền và tương đương tiền cuối kỳ": "cash_and_cash_equivalents_at_end_of_period",
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
        self._remove_blank_data(final_result, ["TÀI SẢN", "NGUỒN VỐN", "I. Lưu chuyển tiền từ hoạt động kinh doanh", "II. Lưu chuyển tiền từ hoạt động đầu tư", "III. Lưu chuyển tiền từ hoạt động tài chính", "III. Lưu chuyển tiền từ hoạt động tài chính"])
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