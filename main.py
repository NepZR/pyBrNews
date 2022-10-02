from News.g1 import G1News
from Comments.g1 import G1Comments
from loguru import logger

if __name__ == '__main__':
    g1 = G1News()
    g1c = G1Comments()

    parsed_news = g1.retrieve_news(
            max_pages=1000, regions=['am', 'ac', 'pa', 'rr', 'ro', 'ap', 'to']
    )

    # parsed_news = g1.search_news(keywords=['Bolsonaro'])

    parsed_news_data = g1.parse_news(news_urls=parsed_news, parse_body=True)
    for counter, news in enumerate(parsed_news_data):
        logger.debug(f"News {counter+1} -- {news['title']} on {news['url']}")

    for counter, comment in enumerate(g1c.parse_comments(news_list=parsed_news_data)):
        logger.debug(f"News {counter+1} -- {comment['comment']} by {comment['url']} with {comment['upvote']} upvotes.")

    # g1.export_data(parsed_data=g1.parse_news(parsed_news), export_type='json')
