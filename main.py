from loguru import logger

from News.g1 import G1News
from config.database import PyBrNewsDB

if __name__ == '__main__':
    crawler = G1News()
    db = PyBrNewsDB(data_kind="news")

    articles = crawler.search_news(keywords=['Saneamento'], max_pages=2)
    for i, data in enumerate(crawler.parse_news(news_urls=articles, parse_body=True, save_html=False)):
        logger.debug(
            f"T: {data['title']} | PubDate: {data['date']} | Platform: {data['platform']} | Section: {data['section']}"
            f" | Body Total Length: {len(data['body']) if data['body'] is not None else 'Not captured.'}"
        )
        db.insert_data(parsed_data=data)
