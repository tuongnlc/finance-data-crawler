import asyncio
import uuid
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
import json

async def scrape_simplize_stocks():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            await page.goto(
                "https://fmarket.vn/trade/account/investor/market/fund",
                wait_until="domcontentloaded",
                timeout=30000,
            )

            # Đợi JS trên trang chạy thêm 3s
            await page.wait_for_timeout(3000)

           
            buttons = {
                "dcds":"DCDS",
                "magef":"MAGEF"
            }
        
            for key, value in buttons.items():
                # button = page.get_by_text(value)
                print(f"Clicked button: {value}")

                button = page.get_by_text(value)
                await button.click()

                danh_muc_dau_tu_lon_button = page.get_by_text("Danh mục đầu tư lớn")
                await danh_muc_dau_tu_lon_button.click()

                # # Đợi bảng dữ liệu load xong
                await page.wait_for_selector(".row-color")

                # # Trích xuất dữ liệu từ các row
                stocks = []
                rows = await page.locator(".row-color").all()
                for row in rows:
                    # Trích xuất từng cột dựa trên index (0, 1, 2)
                    # Sử dụng .first để tránh lỗi strict mode nếu có nhiều label lồng nhau
                    stock_id = await row.locator("div").nth(0).locator("label").first.inner_text()
                    nganh = await row.locator("div").nth(1).locator("label").first.inner_text()
                    gav = await row.locator("div").nth(2).locator("label").first.inner_text()
                    
                    stocks.append({
                        "id": str(uuid.uuid4()),
                        "fund_id": key,
                        "stock_id": stock_id.strip(),
                        "business_sector": nganh.strip(),
                        "gav": gav.strip()
                    })

                    # # In kết quả dạng JSON để kiểm tra
                print(json.dumps(stocks, ensure_ascii=False, indent=2))
                
                # Click nút close (X) để đóng modal và quay lại danh sách quỹ
                # Sử dụng locator cụ thể hơn để tránh lỗi strict mode
                close_button = page.locator(".modal-header a").filter(has=page.locator("svg")).first
                await close_button.click()

                    # Đợi một chút để modal đóng hoàn toàn trước khi bắt đầu loop mới
                await page.wait_for_timeout(1000)


                # await asyncio.sleep(5)
        except Exception as e:
            print(f"Lỗi khi load trang: {e}")


if __name__ == "__main__":
    asyncio.run(scrape_simplize_stocks())