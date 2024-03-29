from loguru import logger

from pyBrNews.news.g1 import G1News

if __name__ == '__main__':
    crawler = G1News(use_database=False)

    articles = crawler.search_news(keywords=['Saneamento'], max_pages=2)
    for i, data in enumerate(crawler.parse_news(news_urls=articles, parse_body=True, save_html=False)):
        logger.debug(
            f"T: {data['title']} | PubDate: {data['date']} | Platform: {data['platform']} | Section: {data['section']}"
            f" | Body Total Length: {len(data['body']) if data['body'] is not None else 'Not captured.'}"
        )

        crawler.DB.set_save_path(fs_save_path="/home/ubuntu/Desktop/")
        crawler.DB.to_json(parsed_data=data)
