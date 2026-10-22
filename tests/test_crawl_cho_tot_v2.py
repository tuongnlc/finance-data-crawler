from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
  # Mở trình duyệt (headless=False giúp bạn nhìn thấy trình duyệt đang làm gì để dễ debug)
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    # Truy cập trang web
    # page.goto("https://www.nhatot.com/mua-ban-nha-dat-quan-tan-binh-tp-ho-chi-minh?page=1")
    page.goto("https://www.nhatot.com/mua-ban-nha-dat-thanh-pho-thu-duc-tp-ho-chi-minh?page=2")

    # Đợi một phần tử quan trọng xuất hiện (đảm bảo trang đã load xong dữ liệu JS)
    # page.wait_for_selector(".product-item", timeout=100)

    # Lấy toàn bộ mã HTML của trang sau khi đã render
    html_content = page.content()

    # Đưa vào BeautifulSoup để parse như bình thường
    soup = BeautifulSoup(html_content, "html.parser")

    # Extract tất cả href của tất cả thẻ <a> có thuộc tính href
    urls = [a["href"] for a in soup.find_all("a", href=True)]
    print(urls)

    browser.close()