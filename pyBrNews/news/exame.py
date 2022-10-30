import time
from datetime import datetime
from itertools import count
from typing import Optional, List, Iterable

from loguru import logger
from requests_html import HTML

from .crawler import Crawler

XPATH_DATA = {
    'news_abstract': '//meta[@property="og:description"]/@content|//meta[@name="description"]/@content',
    'news_body': '//div[@id="news-body"]',
    'news_type': '//meta[@property="og:type"]/@content',
}


class ExameNews(Crawler):
    def __init__(self, use_database: bool = True) -> None:
        super().__init__(use_database=use_database)

        self._SEARCH_API = "https://content-api.exame.com/api/xm/wp/v2/news"

    def _get_article(self, article_url: str) -> Optional[HTML]:
        for _ in range(100):
            try:
                response = self.SESSION.get(url=article_url)
                if response.status_code == 200:
                    html_data = HTML(html=response.content, url=article_url)
                    return html_data

            except self._ERRORS:
                logger.warning(
                    f"Error while getting article with URL: {article_url}."
                )

        return None

    def _make_search(self, page: int, keyword: str) -> Optional[List[dict]]:
        search_params = {
            'page': f"{page}",
            'per_page': '25',
            '_details': 'true',
            '_fields': ('id,slug,date,link,title,featured_media_url,'
                        'categories_data,sponsor_type,sponsor_name,sponsor_link,acf'),
            'search': keyword,
            'order': 'desc',
        }

        for _ in range(100):
            try:
                response = self.SESSION.get(url=self._SEARCH_API, params=search_params)
                if response.status_code != 200:
                    return None

                search_data = response.json()
                return search_data
            except self._ERRORS:
                logger.warning(
                    f"Exame servers are trying to break the capture. Waiting 5 seconds before retrying."
                )
                self.SESSION.cookies.clear_session_cookies()
                time.sleep(5)

        return None

    @staticmethod
    def _extract_title(article_data: dict) -> Optional[str]:
        title = article_data['title']
        if title is not None:
            return title

        return None

    @staticmethod
    def _extract_abstract(article_page: HTML) -> Optional[str]:
        abstract = article_page.xpath(XPATH_DATA['news_abstract'], first=True)
        if abstract is not None:
            return abstract

        return None

    @staticmethod
    def _extract_date(article_data: dict) -> Optional[datetime]:
        raw_date = article_data['date']
        if raw_date is not None:
            published_date = datetime.strptime(raw_date, "%Y-%m-%dT%H:%M:%S")
            return published_date

        return None

    @staticmethod
    def _extract_section(article_data: dict) -> Optional[str]:
        section = article_data['categories_data'][0]['name']
        if section is not None:
            return section

        return None

    @staticmethod
    def _extract_tags(article_data: dict) -> Optional[str]:
        tags = [tag['name'] for tag in article_data['categories_data']]
        if tags is not None:
            article_tags = ' | '.join(tags)
            return article_tags

        return None

    @staticmethod
    def _extract_type(article_page: HTML) -> Optional[str]:
        news_type = article_page.xpath(XPATH_DATA['news_type'], first=True)
        if news_type is not None:
            return news_type

        return None

    def _extract_region(self, article_page: HTML) -> Optional[str]:
        region = None
        return region

    @staticmethod
    def _extract_body(article_page: HTML) -> Optional[str]:
        article_body = article_page.xpath(XPATH_DATA['news_body'], first=True)
        if article_body is not None:
            body = article_body.full_text
            return body

        return None

    @staticmethod
    def _extract_id(article_data: dict) -> Optional[int]:
        news_id = article_data['id']
        if news_id is not None:
            return news_id

        return None

    def parse_news(self, news_urls: List[dict], parse_body: bool = False, save_html: bool = True) -> Iterable[dict]:
        parsed_counter = 0
        for i, article_data in enumerate(news_urls):
            if article_data is None:
                continue

            url = article_data['link']
            if 'exame.com' not in url:
                continue

            page = self._get_article(article_url=url)
            logger.info(f"Article {i+1} >> Parsing data at {datetime.now()}.")

            parsed_news = {
                'title': self._extract_title(article_data=article_data),
                'abstract': self._extract_abstract(article_page=page),
                'date': self._extract_date(article_data=article_data),
                'section': self._extract_section(article_data=article_data),
                'region':  self._extract_region(article_page=page),
                'url': url,
                'platform': 'Exame',
                'tags': self._extract_tags(article_data=article_data),
                'type': self._extract_type(article_page=page),
                'body': self._extract_body(article_page=page),
                'id_data': self._extract_id(article_data=article_data),
                'html': page.raw_html if save_html else None,
            }

            if self.DB.check_duplicates(parsed_data=parsed_news):
                continue

            parsed_counter += 1
            logger.success(f"Article {i + 1} >> Data parsed successfully!.")

            yield parsed_news

        logger.success(
            f"All the data have been parsed successfully! "
            f"{parsed_counter} of {len(news_urls)} news had the data extracted."
        )

    def search_news(self, keywords: list, max_pages: int = -1) -> List[dict]:
        articles = []
        for keyword in keywords:
            logger.info(f"Retrieving news from Exame associated with the Keyword \"{keyword}\".")

            for i in count():
                logger.info(
                    f"{keyword.title()} >> Getting data from Page {i+1}. Current URLs acquired: {len(articles)}."
                )

                search_data = self._make_search(page=i+1, keyword=keyword)
                if search_data is None:
                    logger.success(
                        f"{keyword.title()} >> All data have been added to list! Finished at {datetime.now()}."
                    )
                    break

                for item in search_data:
                    if "link" not in item.keys():
                        continue

                    if "exame.com" in item["link"]:
                        articles.append(item)

                if i+1 == max_pages:
                    logger.success(
                        f"{keyword.title()} >> All data have been added to list! Finished at {datetime.now()}."
                    )
                    break

        logger.success(
            f"News retrieved successfully! A total of {len(articles)} articles have been found."
        )

        return articles
