import asyncio
from playwright.async_api import async_playwright

async def get_heading_links(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, wait_until="networkidle")
        
        # Selector này lấy thẻ 'a' nằm trong 'h2' HOẶC 'h3'
        links = await page.eval_on_selector_all(
            "h2 a, h3 a, h4 a", 
            "elements => elements.map(el => ({text: el.innerText, href: el.href}))"
        )
        
        await browser.close()
        return links

# Chạy thử
url = 'https://vietstock.vn/chung-khoan.htm'
results = asyncio.run(get_heading_links(url))
for item in results:
    print(f"{item['text']}: {item['href']}")