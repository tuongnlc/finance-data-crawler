from src.shared.application.crawler.base import BasePlaywrightCrawler
from typing import Any, Callable, ClassVar, TypeVar
from bs4 import BeautifulSoup
from typing import Any, AsyncIterator


TProduct = TypeVar("TProduct", bound=BasePlaywrightCrawler)

class CrawlCashFlowStatementTypeFour(BasePlaywrightCrawler):
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

        bao_cao_luu_chuyen_tien_te_tag = self.page.get_by_role("tab", name="LCTT trực tiếp").first
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
            "Thu nhập lãi và các khoản thu nhập tương tự nhận được": "interest_and_similar_income_received",
            "Chi phí lãi và các chi phí tương tự đã trả": "interest_and_similar_expenses_paid",
            "Thu nhập từ hoạt động dịch vụ nhận được": "fee_and_commission_income_received",
            "Chênh lệch số tiền thực thu/ thực chi từ hoạt động kinh doanh (ngoại tệ, vàng bạc, chứng khoán)": "net_gain_loss_from_trading_activities",
            "Thu nhập khác": "other_operating_income",
            "Tiền thu các khoản nợ đã được xử lý xóa, bù đắp bằng nguồn rủi ro": "cash_recovered_from_bad_debts_written_off",
            "Tiền chi trả cho nhân viên và hoạt động quản lý, công vụ": "cash_paid_to_employees_and_for_operating_expenses",
            "Tiền thuế thu nhập thực nộp trong kỳ": "corporate_income_tax_paid",
            "Lưu chuyển tiền thuần từ hoạt động kinh doanh trước những thay đổi về tài sản và vốn lưu động": "operating_cash_flows_before_working_capital_changes",
            "(Tăng)/Giảm các khoản tiền, vàng gửi và cho vay các TCTD khác": "change_in_deposits_and_loans_to_other_cits",
            "(Tăng)/Giảm các khoản về kinh doanh chứng khoán": "change_in_trading_securities",
            "(Tăng)/Giảm các công cụ tài chính phái sinh và các tài sản tài chính khác": "change_in_derivative_financial_assets",
            "(Tăng)/Giảm các khoản cho vay khách hàng": "change_in_loans_to_customers",
            "(Tăng)/Giảm nguồn dự phòng để bù bắp tổn thất các khoản": "change_in_provisions_for_credit_losses",
            "(Tăng)/Giảm khác về tài sản hoạt động": "change_in_other_operating_assets",
            "Tăng/(Giảm) các khoản nợ chính phủ và NHNN": "change_in_due_to_government_and_sbv",
            "Tăng/(Giảm) các khoản tiền gửi, tiền vay các TCTD": "change_in_deposits_and_borrowings_from_other_cits",
            "Tăng/(Giảm) tiền gửi của khách hàng": "change_in_deposits_from_customers",
            "Tăng/(Giảm) phát hành giấy tờ có giá": "change_in_valuable_papers_issued",
            "Tăng/(Giảm) vốn tài trợ, ủy thác đầu tư, cho vay mà TCTD chịu rủi ro": "change_in_entrusted_funds_and_loans",
            "Tăng/(Giảm) các công cụ tài chính phái sinh và các khoản nợ tài chính khác": "change_in_derivative_financial_liabilities",
            "Tăng/(Giảm) khác về công nợ hoạt động": "change_in_other_operating_liabilities",
            "Chi từ các quỹ của TCTD": "payments_from_welfare_and_other_funds",
            "Lưu chuyển tiền thuần từ hoạt động kinh doanh": "net_cash_flows_from_operating_activities",

            # ==================== II. DÒNG TIỀN TỪ HOẠT ĐỘNG ĐẦU TƯ ====================
            "Tiền giảm do bán công ty con": "cash_proceeds_from_disposal_of_subsidiaries",
            "Mua sắm TSCĐ": "cash_paid_for_fixed_assets",
            "Tiền thu từ thanh lý, nhượng bán TSCĐ": "cash_received_from_disposal_of_fixed_assets",
            "Tiền chi từ thanh lý, nhượng bán TSCĐ": "cash_paid_for_disposal_of_fixed_assets",
            "Mua sắm bất động sản đầu tư": "cash_paid_for_investment_properties",
            "Tiền thu từ bán, thanh lý bất động sản đầu tư": "cash_received_from_disposal_of_investment_properties",
            "Tiền chi ra do bán, thanh lý bất động sản đầu tư": "cash_paid_for_disposal_of_investment_properties",
            "Tiền chi đầu tư, góp vốn vào các đơn vị khác": "cash_paid_for_equity_investments",
            "Tiền thu đầu tư, góp vốn vào các đơn vị khác": "cash_received_from_equity_investments",
            "Tiền thu cổ tức và lợi nhuận được chia từ các khoản đầu tư, góp vốn dài hạn": "dividends_and_profits_received",
            "Lưu chuyển tiền thuần từ hoạt động đầu tư": "net_cash_flows_from_investing_activities",

            # ==================== III. DÒNG TIỀN TỪ HOẠT ĐỘNG TÀI CHÍNH ====================
            "Tăng vốn cổ phần từ góp vốn và phát hành cổ phiếu": "cash_received_from_issuing_shares",
            "Tiền thu từ phát hành giấy tờ có giá dài hạn có đủ điều kiện tính vào vốn tự có và các khoản vốn vay dài hạn khác": "cash_received_from_long_term_eligible_papers_and_loans",
            "Tiền chi thanh toán giấy tờ có giá dài hạn có đủ điều kiện tính vào vốn tự có và các khoản vốn vay dài hạn khác": "cash_repayments_of_long_term_eligible_papers_and_loans",
            "Cổ tức trả cho cổ đông, lợi nhuận đã chia": "dividends_paid_to_shareholders",
            "Tiền chi ra mua cổ phiếu ngân quỹ": "cash_paid_for_treasury_shares_buyback",
            "Tiền thu được do bán cổ phiếu ngân quỹ": "cash_received_from_disposal_of_treasury_shares",
            "Lưu chuyển tiền từ hoạt động tài chính": "net_cash_flows_from_financing_activities",

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
        self._remove_blank_data(final_result, 
        ["TÀI SẢN", "NGUỒN VỐN", "I. Lưu chuyển tiền từ hoạt động kinh doanh", "II. Lưu chuyển tiền từ hoạt động đầu tư", "III. Lưu chuyển tiền từ hoạt động tài chính", "III. Lưu chuyển tiền từ hoạt động tài chính",
            "1. Những thay đổi về tài sản hoạt động", "2. Những thay đổi về công nợ hoạt động"
        ])
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