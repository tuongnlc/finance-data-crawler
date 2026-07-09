from finance_data_crawler.shared.application.crawler.base import BaseCrawler
import newspaper
from typing import Any
from datetime import datetime



class CrawlNewspaper(BaseCrawler):
    def __init__(self, headless: bool = True, **kwargs: Any) -> None:
        super().__init__()

    def extract(self, link: str, **kwargs: Any) -> Any:
        article = newspaper.article(link)

        newspaper_title = article.title
        publish_date = article.publish_date
        newspaper_content = article.text

        article.nlp()
        newspaper_summary = article.summary
        return {
            "newspaper_title": newspaper_title,
            "newspaper_url": link,
            "publish_date": publish_date,
            "newspaper_content": newspaper_content,
            "newspaper_summary": newspaper_summary,
            "is_load_to_qdrant": 0,
            "created_at": datetime.now().date(),
        }
