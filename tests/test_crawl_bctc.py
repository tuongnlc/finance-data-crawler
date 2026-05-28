from typing import Any, AsyncIterator
from src.shared.application.crawler.base import BasePlaywrightCrawler
import re
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

    def _parse_string_to_float(self, value: Any) -> Any:
        if value is None:
            return 0

        if isinstance(value, (int, float)):
            return value

        if isinstance(value, str):
            if "," in value:
                return float(value.replace(",", ""))
            if value == "":
                return 0
            else:
                try:
                    return float(value)
                except:
                    return value
        else:
            raise ValueError(f"Expected str or float, got {type(value)}")

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

        # bao_cao_tai_chinh_tab = self.page.get_by_role("tab", name="Báo cáo tài chính").first
        # await bao_cao_tai_chinh_tab.wait_for(state="visible", timeout=5000)
        # await bao_cao_tai_chinh_tab.click()
        # await self.page.wait_for_timeout(1000)

        can_doi_ke_toan_tag = self.page.get_by_role("tab", name="Chỉ tiêu tài chính").first
        await can_doi_ke_toan_tag.wait_for(state="visible", timeout=5000)
        await can_doi_ke_toan_tag.click()
        await self.page.wait_for_timeout(1000)

    def _map_keys(self, items: list[dict[str, Any]]) -> None:
        mapping_keyword = {
    # Thông tin cấu trúc dữ liệu
    "stock_id": "stock_id",
    "year": "year",
    "quarter": "quarter",

    # Các chỉ số tài chính
    "P/E": "p_e",
    "P/S": "p_s",
    "P/B": "p_b",
    "EPS": "eps",
    "Tỷ lệ lãi ròng (%)": "net_profit_margin",
    "Tỷ lệ lãi gộp (%)": "gross_profit_margin",
    "Tỷ lệ EBIT (%)": "ebit_margin",
    "Tỷ lệ lãi từ HĐKD (%)": "operating_profit_margin",
    "Thanh toán hiện hành": "current_ratio",
    "Thanh toán nhanh": "quick_ratio",
    "Thanh toán lãi vay": "interest_coverage_ratio",
    "Nợ/VCSH": "debt_to_equity",
    "ROA (%)": "roa",
    "ROE (%)": "roe",
    "ROIC (%)": "roic",
    "ROCE (%)": "roce",
    "Vòng quay tổng TS": "total_asset_turnover",
    "Vòng quay HTK": "inventory_turnover",
    "Vòng quay các KPT": "receivables_turnover",
    "Vòng quay TSNH": "short_term_asset_turnover"
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
        tables = soup.select("table.border-collapse")
        target_tables: list[Any] = []
        for candidate in tables:
            thead = candidate.find("thead")
            if not thead:
                continue
            header_cells = thead.find_all("th")
            if any(th.get_text(strip=True).startswith("Q") for th in header_cells):
                target_tables.append(candidate)

        if not target_tables:
            print("Không tìm thấy bảng dữ liệu!")
            raise ValueError("Không tìm thấy bảng dữ liệu!")

        stock_id = link.split("/")[-1]

        quarter_labels: list[str] = []
        quarter_label_to_key: dict[str, tuple[str, int, str]] = {}
        for table in target_tables:
            header_cells = table.find("thead").find_all("th")
            for th in header_cells:
                label = th.get_text(strip=True)
                if not label.startswith("Q"):
                    continue
                if label in quarter_label_to_key:
                    continue
                quarter, year = label.split("/")
                key = (stock_id, int(year), quarter)
                quarter_label_to_key[label] = key
                quarter_labels.append(label)

        quarter_keys = [quarter_label_to_key[label] for label in quarter_labels]

        data_by_quarter: dict[tuple[str, int, str], dict[str, Any]] = {
            (sid, year, quarter): {"stock_id": sid, "year": year, "quarter": quarter}
            for sid, year, quarter in quarter_keys
        }

        representative_key = quarter_keys[0] if quarter_keys else None
        for table in target_tables:
            table_quarters: list[str] = []
            header_cells = table.find("thead").find_all("th")
            for th in header_cells:
                label = th.get_text(strip=True)
                if label.startswith("Q"):
                    table_quarters.append(label)

            tbody = table.find("tbody")
            if not tbody:
                continue

            rows = tbody.find_all("tr")
            for row in rows:
                cells = row.find_all("td")
                values_start = len(cells) - len(table_quarters)
                if values_start <= 0:
                    continue

                indicator_name_raw = cells[0].get_text(" ", strip=True)
                indicator_name_raw = " ".join(indicator_name_raw.split())
                indicator_name = indicator_name_raw.lstrip("-+ ").rstrip()
                indicator_name = re.sub(r"\s*\(\s*\d+\s*\)\s*$", "", indicator_name).strip()

                unique_indicator_name = indicator_name
                if representative_key:
                    existing0 = data_by_quarter[representative_key]
                    if unique_indicator_name in existing0:
                        suffix = 2
                        while f"{indicator_name} ({suffix})" in existing0:
                            suffix += 1
                        unique_indicator_name = f"{indicator_name} ({suffix})"

                for index, label in enumerate(table_quarters):
                    quarter_key = quarter_label_to_key.get(label)
                    if not quarter_key:
                        continue
                    value_cell = cells[values_start + index]
                    value = value_cell.get_text(strip=True)
                    data_by_quarter[quarter_key][unique_indicator_name] = value

        final_result = [data_by_quarter[key] for key in quarter_keys]
        self._remove_blank_data(final_result, 
            ["TÀI SẢN", "NGUỒN VỐN", "I. Lưu chuyển tiền từ hoạt động kinh doanh", "II. Lưu chuyển tiền từ hoạt động đầu tư", "III. Lưu chuyển tiền từ hoạt động tài chính", "III. Lưu chuyển tiền từ hoạt động tài chính",
            "1. Những thay đổi về tài sản hoạt động", "2. Những thay đổi về công nợ hoạt động"
            ])
        self._map_keys(final_result)
        return final_result

    async def _upsert_to_postgresql(self, results: list[dict[str, Any]]) -> None:
        try:
            async for db in async_session_scope():
                model_path = "src.shared.infrastructure.db.models.FinancialStatisticsOverviewTypeOne"
                final_repo = FinalStatementRepository(model_path=model_path, session=db)

                for result in results:
                    # data = {k: self._parse_string_to_int(v) for k, v in item.items()}
                    await final_repo.upsert_by_year_quarter_stock_id(
                        stock_id=result["stock_id"],
                        year=result["year"],
                        quarter=result["quarter"],
                        data=result,
                    )
        except Exception as e:
            print(f"Error inserting data to PostgreSQL: {e}")
            raise

    async def crawl_pages(self, links: list[str], **kwargs: Any) -> AsyncIterator[list[dict[str, Any]]]:
        await self._init_crawler()
        results: list[dict[str, Any]] = []
        try:
            for link in links:
                items = await self._extract_single_link(link)
                for item in items:
                    data = {k: self._parse_string_to_float(v) for k, v in item.items()}
                    results.append(data)
                yield results
                # await asyncio.sleep(60)
        finally:
            await self._close_crawler()

    async def crawl(self, links: list[str], **kwargs: Any) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        async for batch in self.crawl_pages(links, **kwargs):
            results.extend(batch)
        return results

    async def extract(self, link: str | list[str], **kwargs: Any) -> list[dict[str, Any]]:
        links = link if isinstance(link, list) else [link]
        return await self.crawl(links, **kwargs)


test_crawler = CrawlBCTC(
    headless=False,
)

test_links = [
    "https://fireant.vn/ma-chung-khoan/HPG",
]

async def test_extract():
    async for batch in test_crawler.crawl_pages(test_links):
        await test_crawler._upsert_to_postgresql(batch)
        print(batch)
        print("-----------------")
        print(f"Extracted {len(batch)} records for stock_id={batch[0]['stock_id'] if batch else None}")
    # await asyncio.sleep(5)
    # print(f"Extracted {len(data)} records")
    
if __name__ == "__main__":
    asyncio.run(test_extract())
