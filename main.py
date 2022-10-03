from News.g1 import G1News
from Comments.g1 import G1Comments

from News.folha_sp import FolhaNews
from Comments.folha_sp import FolhaComments
from loguru import logger

if __name__ == '__main__':
    # g1 = G1News()
    # g1c = G1Comments()

    fsp = FolhaNews()
    fsp_ = FolhaComments()

    parsed_news = fsp.search_news(keywords=['Saneamento'], max_pages=2)

    parsed_news_data = [data for data in fsp.parse_news(news_urls=parsed_news, parse_body=True)]
    for counter, news in enumerate(parsed_news_data):
        logger.debug(f"News {counter+1} -- {news['title']} from Section {news['section']}")

    for counter, comment in enumerate(fsp_.parse_comments(news_list=parsed_news_data)):
        logger.debug(
            f"Comment No. {counter+1} -- \"{comment['comment']}\" published by {comment['author']} "
            f"with {comment['upvote']} upvotes."
        )

    # g1.export_data(parsed_data=g1.parse_news(parsed_news), export_type='json')
