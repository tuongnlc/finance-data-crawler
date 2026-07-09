from src.shared.application.crawler.base import BasePlaywrightCrawler
from typing import Any, Callable, ClassVar, TypeVar
from bs4 import BeautifulSoup
from typing import Any, AsyncIterator
import re

TProduct = TypeVar("TProduct", bound=BasePlaywrightCrawler)

class CrawlFinancialStatisticsOverviewTypeFour(BasePlaywrightCrawler):
    def __init__(self, headless: bool = True) -> None:
        super().__init__(headless=headless)

    async def scroll_page(self):
        pass

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
            "YOEA (%)": "yoea",
            "NIM (%)": "nim",
            "COF (%)": "cof",
            "LAR (%)": "lar",
            "LDR (%)": "ldr",
            "CLR (%)": "clr",
            "CTA (%)": "cta",
            "ELR (%)": "elr",
            "ROA (%)": "roa",
            "ROE (%)": "roe",
            "CIR (%)": "cir",
            "LLRL (%)": "llrl",
            "LLRNPL (%)": "llrnpl",
            "Tỷ lệ nợ xấu (%)": "npl_ratio",
            "PCL (%)": "pcl"
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
        self._map_keys(final_result)
        return final_result

    async def crawl_pages(self, links: list[str], **kwargs: Any) -> AsyncIterator[list[dict[str, Any]]]:
        await self._init_crawler()
        try:
            for link in links:
                print(f"Processing link: {link}")
                items = await self._extract_single_link(link)
                batch: list[dict[str, Any]] = [
                    {k: self._parse_string_to_float(v) for k, v in item.items()} for item in items
                ]
                print(f"Success extract from link: {link}")
                yield batch 
        finally:
            await self._close_crawler()

    async def extract(self, links: list[str], **kwargs: Any) -> AsyncIterator[list[dict[str, Any]]]:
        async for batch in self.crawl_pages(links, **kwargs):
            yield batch