from News.exame import ExameNews

from loguru import logger

if __name__ == '__main__':
    crawler = ExameNews()

    articles = crawler.search_news(keywords=['Saneamento'], max_pages=2)
    parsed_data = crawler.parse_news(news_urls=articles, parse_body=True)

    for data in parsed_data:
        logger.debug(f"{data}")
