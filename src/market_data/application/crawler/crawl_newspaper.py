from src.shared.application.crawler.base import BaseCrawler
import newspaper
from typing import Any



class CrawlNewspaper(BaseCrawler):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def extract(self, link: str, **kwargs: Any) -> Any:
        article = newspaper.article(link)

        publish_date = article.publish_date
        content = article.text

        article.nlp()
        summary = article.summary
        return {
            "url": link,
            "publish_date": publish_date,
            "content": content,
            "summary": summary,
        }

#test here
url = 'https://vneconomy.vn/vi-pham-5-loi-chung-khoan-bms-bi-phat-toi-780-trieu-dong.htm'
test_crawler = CrawlNewspaper()
result = test_crawler.extract(url)
print(result)
