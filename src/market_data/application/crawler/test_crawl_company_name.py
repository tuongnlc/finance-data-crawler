import asyncio
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
import json

async def scrape_simplize_stocks():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            await page.goto(
                "https://simplize.vn/co-phieu",
                wait_until="domcontentloaded",
                timeout=30000,
            )

            # Đợi JS trên trang chạy thêm 3s
            await page.wait_for_timeout(3000)

            # Đợi popup xuất hiện rồi BẤM NÚT ĐÓNG thay vì xóa tay
            try:
                await page.wait_for_selector("#is63", timeout=10000)
                # try:
                await page.wait_for_selector("button.simplize-dialog-close", timeout=10000)
                await page.click("button.simplize-dialog-close")
            except PlaywrightTimeoutError:
                # Không thấy popup thì bỏ qua
                pass
            else:
                # Thử tìm nút close trong popup và click
                close_candidate = page.locator(
                    "#is63 button, #is63 [role='button'], "
                    "#is63 [class*='close'], #is63 [class*='Close']"
                )
                if await close_candidate.count() > 0:
                    await close_candidate.first.click()
                else:
                    # Fallback: click gần góc trên bên phải vùng popup
                    box = await page.locator("#is63").bounding_box()
                    if box:
                        await page.mouse.click(
                            box["x"] + box["width"] - 10,
                            box["y"] + 10,
                        )

            # Scroll xuống dưới bằng scrollingElement
            await page.evaluate(
                """
                () => {
                    const el = document.scrollingElement || document.documentElement || document.body;
                    if (el) {
                        el.scrollTo({ top: 2300, behavior: 'auto' });
                    }
                }
                """
            )

            #Extract data from this page
            await page.wait_for_selector('tr.simplize-table-row')
            stocks_data = await page.evaluate('''() => {
            const rows = document.querySelectorAll('tr.simplize-table-row');
            return Array.from(rows).map(row => {
                // Lấy Stock ID (Mã CP)
                const stockId = row.querySelector('.css-8llhbn')?.innerText.trim();
                
                // Lấy Company Name (Tên công ty - từ attribute title)
                const companyName = row.querySelector('.css-skycj1')?.getAttribute('title') || 
                                    row.querySelector('.css-skycj1')?.innerText.trim();
                
                // Lấy Sector (Cột cuối cùng)
                const cells = row.querySelectorAll('td.simplize-table-cell');
                const sector = cells[cells.length - 1]?.innerText.trim();

                return {
                    "stock_id": stockId,
                    "company_name": companyName,
                    "Sector": sector
                };
            });
        }''')
            print(json.dumps(stocks_data, indent=4, ensure_ascii=False))
            print("       ")
            #Click to next page
            # await page.click('div.simplize-pagination-item-link')
            next_button = page.locator('li.simplize-pagination-next')
            await next_button.click()
            
            # wait to load page 2
             
            await page.wait_for_selector("li.simplize-pagination-item-active >> text='2'")
            stocks_data = await page.evaluate('''() => {
            const rows = document.querySelectorAll('tr.simplize-table-row');
            return Array.from(rows).map(row => {
                // Lấy Stock ID (Mã CP)
                const stockId = row.querySelector('.css-8llhbn')?.innerText.trim();
                
                // Lấy Company Name (Tên công ty - từ attribute title)
                const companyName = row.querySelector('.css-skycj1')?.getAttribute('title') || 
                                    row.querySelector('.css-skycj1')?.innerText.trim();
                
                // Lấy Sector (Cột cuối cùng)
                const cells = row.querySelectorAll('td.simplize-table-cell');
                const sector = cells[cells.length - 1]?.innerText.trim();

                return {
                    "stock_id": stockId,
                    "company_name": companyName,
                    "Sector": sector
                };
            });
        }''')
            print(json.dumps(stocks_data, indent=4, ensure_ascii=False))

            await asyncio.sleep(5)
        except Exception as e:
            print(f"Lỗi khi load trang: {e}")


if __name__ == "__main__":
    asyncio.run(scrape_simplize_stocks())