from typing import Any, AsyncIterator
from src.shared.application.crawler.base import BasePlaywrightCrawler
import asyncio
import time
from bs4 import BeautifulSoup


class CrawlBCTC(BasePlaywrightCrawler):
    def __init__(self, headless: bool = True) -> None:
        super().__init__(headless=headless)

    async def scroll_page(self):
        await self.page.evaluate("window.scrollTo(1000, document.body.scrollHeight);")

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
        print(html_content)
        # browser.close()
        soup = BeautifulSoup(html_content, "html.parser")
        table = soup.find("table", class_=lambda x: x and "border-collapse" in x)
        if not table:
            print("Không tìm thấy bảng dữ liệu!")
            raise ValueError("Không tìm thấy bảng dữ liệu!")

        # self.page.scolll

        # 1. Lấy danh sách các Quý từ thẻ <thead>
        quarters = []
        header_cells = table.find("thead").find_all("th")
        for th in header_cells:
            text = th.get_text(strip=True)
            if text.startswith("Q"):  # Lọc các cột như 'Q1 2025', 'Q2 2025'
                quarters.append(text)

        # Khởi tạo cấu trúc dict gom dữ liệu theo từng Quý
        # Key định dạng: "Q1_2025"
        data_by_quarter = {}
        for q in quarters:
            key = q.replace(" ", "_")
            data_by_quarter[key] = {"year": key}

        # 2. Duyệt qua các dòng dữ liệu trong <tbody>
        rows = table.find("tbody").find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            if len(cells) < 3:
                continue  # Bỏ qua dòng thiếu dữ liệu

            # Lấy tên chỉ tiêu ở cột đầu tiên và làm sạch nút bấm thừa (+/-) nếu có
            indicator_name = cells[0].get_text(strip=True)
            indicator_name = indicator_name.lstrip("-+ ").rstrip("-+ ")

            # Duyệt qua các cột số liệu tiếp theo, khớp vào đúng Quý dựa trên index
            for index, q in enumerate(quarters):
                quarter_key = q.replace(" ", "_")

                # Ô số liệu thực tế bắt đầu từ cột thứ 3 (index trong HTML là: index_của_quý + 2)
                value_cell = cells[index + 2]
                value = value_cell.get_text(strip=True)

                # Đưa dữ liệu vào đúng vị trí Quý
                data_by_quarter[quarter_key][indicator_name] = value

        final_result = list(data_by_quarter.values())
        print(final_result)
        return final_result


test_crawler = CrawlBCTC(
    headless=False,
)

test_link = 'https://fireant.vn/ma-chung-khoan/HPG'

async def test_extract():
    data = await test_crawler.extract(test_link)
    time.sleep(5)
    # print(f"Extracted {len(data)} records")
    
if __name__ == "__main__":
    asyncio.run(test_extract())
