from src.shared.application.crawler.base import BaseCrawler
import newspaper
from typing import Any
from datetime import datetime



class CrawlNewspaper(BaseCrawler):
    def __init__(self, headless: bool = True, **kwargs: Any) -> None:
        super().__init__()

    def extract(self, link: str, **kwargs: Any) -> Any:
        article = newspaper.article(link)

        title = article.title
        publish_date = article.publish_date
        content = article.text

        article.nlp()
        summary = article.summary
        return {
            "title": title,
            "url": link,
            "publish_date": publish_date,
            "content": content,
            "summary": summary,
            "is_embedded": 0,
            "created_at": datetime.now().date(),
        }
