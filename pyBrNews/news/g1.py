import json
import re
from datetime import datetime
from itertools import count
from typing import List, Iterable, Optional
from urllib.parse import unquote

from loguru import logger
from requests_html import HTML

from .crawler import Crawler
from ..config import g1_api

XPATH_DATA = {
    'news_title': '//div[@class="title"]/h1/text()|//meta[@name="title"]/@content|//head/title/text()',
    'news_date': '//time[@itemprop="datePublished"]/@datetime',
    'news_abstract': '//h2[@class="content-head__subtitle"]/text()|//meta[@name="description"]/@content',
    'news_body': '//div[@class="mc-article-body"]//p/text()',
    'news_section': '//div[@class="header-title-content"]/a/text()',
    'news_tags': '//ul[@class="entities__list"]//a/text()'
}


class G1News(Crawler):
    def __init__(self, use_database: bool = True) -> None:
        super().__init__(use_database=use_database)

        self._API_CONFIG = g1_api.news_config
        self._NEWS_API = self._API_CONFIG['api_url']['news_engine']
        self._SEARCH_API = self._API_CONFIG['api_url']['search_engine']

    def _retrieve_news_by_region(self, regions: list, max_pages: int = -1) -> Iterable[str]:
        for region in regions:
            for i in count():
                try:
                    page = self.SESSION.get(
                        self._NEWS_API.format(self._API_CONFIG['regions'][region], str(i + 1))
                    ).json()
                except json.decoder.JSONDecodeError:
                    break

                for item in page['items']:
                    try:
                        url = str(item['content']['url']) if ('materia' in item['type']) else None
                        if url is not None:
                            logger.success(
                                f"URL from G1 {region.upper()} retrieved successfully! Item added to list: {url}"
                            )
                            yield url
                    except KeyError:
                        for article in item['content']['posts']:
                            url = article['url']
                            if url is not None:
                                logger.success(
                                    f"URL from G1 {region.upper()} retrieved successfully! Item added to list: {url}"
                                )
                                yield url

                if i+1 == max_pages:
                    break

    def _retrieve_news_brazil(self, max_pages: int = -1) -> Iterable[str]:
        for i in count():
            try:
                page = self.SESSION.get(
                    self._NEWS_API.format(self._API_CONFIG['regions']['brasil'], str(i + 1))
                ).json()
            except json.decoder.JSONDecodeError:
                break

            for item in page['items']:
                try:
                    url = item['content']['url'] if ('materia' in item['type']) else ()
                    if url is not None:
                        logger.success(f"URL from G1 retrieved successfully! Item added to list: {url}")
                        yield url
                except KeyError:
                    for article in item['content']['posts']:
                        url = article['url']
                        if url is not None:
                            logger.success(
                                f"URL from G1 retrieved successfully! Item added to list: {url}"
                            )
                            yield url

            if i+1 == max_pages:
                break

    def retrieve_latest_news(self, regions: list = None, max_pages: int = -1) -> List[str]:
        news_urls = []
        if regions is None:
            news_urls = [url for url in self._retrieve_news_brazil(max_pages=max_pages)]

        if regions is not None:
            news_urls = [url for url in self._retrieve_news_by_region(regions=regions, max_pages=max_pages)]

        return news_urls

    def parse_news(self, news_urls: List[str], parse_body: bool = False, save_html: bool = True) -> Iterable[dict]:
        parsed_counter = 0
        for i, url in enumerate(news_urls):
            logger.info(f"Article {i+1} >> Parsing data at {datetime.now()}.")
            page = self.SESSION.get(url).html

            parsed_news = {
                'title': self._extract_title(article_page=page),
                'abstract': self._extract_abstract(article_page=page),
                'date': self._extract_date(article_page=page),
                'section': self._extract_section(article_page=page),
                'region': self._extract_region(article_url=url),
                'url': url,
                'platform': 'Portal G1',
                'tags': self._extract_tags(article_data=page),
                'type': self._extract_type(article_url=url),
                'body': self._extract_body(article_page=page),
                'id_data': None,
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

    def search_news(self, keywords: List[str], max_pages: int = -1) -> List[str]:
        news_urls = []
        for keyword in keywords:
            logger.info(f"Retrieving news from G1 associated with the Keyword \"{keyword}\".")
            for i in count():
                page = self.SESSION.get(self._SEARCH_API.format(keyword, str(i+1)))
                if "page" not in page.url:
                    break

                news_list = [unquote(url).split('u=')[1].split('&')[0] for url in page.html.xpath(
                    '//div[@class="widget--info__text-container"]/a/@href'
                )]
                news_urls += (url for url in news_list if 'g1.globo.com' in url)

                if i+1 == max_pages:
                    break

        logger.success(
            f"News retrieved successfully! A total of {len(news_urls)} articles have been found."
        )

        return news_urls

    @staticmethod
    def _extract_title(article_page: HTML) -> Optional[str]:
        title = article_page.xpath(XPATH_DATA['news_title'], first=True)
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
    def _extract_date(article_page: HTML) -> Optional[datetime]:
        raw_date = article_page.xpath(XPATH_DATA['news_date'], first=True)
        if raw_date is not None:
            try:
                published_date = datetime.strptime(raw_date, "%Y-%m-%dT%H:%M:%S.%fZ")
                return published_date
            except ValueError:
                return None

        return None

    @staticmethod
    def _extract_section(article_page: HTML) -> Optional[str]:
        section = article_page.xpath(XPATH_DATA['news_section'], first=True)
        if section is not None:
            return section

        return None

    def _extract_region(self, article_url: str) -> Optional[str]:
        region = article_url.split('/')[3]
        if region in self._API_CONFIG['regions'].keys():
            region = region.upper()
            return region

        return None

    @staticmethod
    def _extract_tags(article_data: HTML) -> Optional[str]:
        tags = article_data.xpath(XPATH_DATA['news_tags'], first=True)
        if tags is not None:
            return tags

        return None

    @staticmethod
    def _extract_type(article_url: str) -> Optional[str]:
        if "video" in article_url:
            news_type = "Video"
        else:
            news_type = "Article"

        return news_type

    @staticmethod
    def _extract_body(article_page: HTML) -> Optional[str]:
        article_body = article_page.xpath(XPATH_DATA['news_body'])
        if article_body is not None:
            body = ' '.join(article_body)
            re.sub(r"(\s{2,})|(\n)+", body, "")
            return body

        return None
