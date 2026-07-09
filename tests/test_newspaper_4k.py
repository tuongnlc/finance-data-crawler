import newspaper

import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from finance_data_crawler.market_data.infrastructure.persistence.postgresql.newspaper_repository import NewspaperRepository
from finance_data_crawler.market_data.infrastructure.persistence.postgresql.newspaper_url_repository import NewspaperUrlRepository


import asyncio
from sqlalchemy import text
from finance_data_crawler.shared.infrastructure.db.connection import async_session_scope, get_async_engine
from datetime import datetime
from finance_data_crawler.market_data.infrastructure.persistence.postgresql.newspaper_url_repository import NewspaperUrlRepository
import uuid



from dotenv import load_dotenv 

load_dotenv()  

async def test_scope():
    print("--- Test với async_session_scope ---")
    try:
        async for db in async_session_scope():
            loader = NewspaperUrlRepository(session=db)
            urls = await loader.query_urls_by_is_crawled()
    except Exception as e:
        print(f"❌ Lỗi: {e}")
    finally:
        await get_async_engine().dispose()

    for url in urls:
        # print(url)
        article = newspaper.article(url)
        print(article.title)
        print(article.publish_date)
        print(article.text)
        # print(article.title)
        article.nlp()
        print(article.summary)
        print("-----------------")

if __name__ == "__main__":
    asyncio.run(test_scope())


# url = 'https://vietstock.vn/2026/05/hon-nua-so-ma-dau-khi-van-giu-xu-huong-tang-dai-han-suot-5-thang-830-1442029.htm'
# article = newspaper.article(url)
# print(article.authors)
# print(article.publish_date)
# print(article.text)
# print(article.title)



# article.nlp()
# print(" ")
# print(article.summary)

#id
#title
#url
#publish_date
#content
#summary

# Step 1: Query newspaper_url table
