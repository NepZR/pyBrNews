import json
from datetime import datetime
from urllib.parse import unquote

import requests.exceptions
from requests_html import HTMLSession
from typing import Union, List, Iterable
from loguru import logger
from itertools import count

from News.crawler import Crawler

SESSION = HTMLSession()
XPATH_DATA = {
    'news_title': '//div[@class="title"]/h1/text()|//meta[@name="title"]/@content|//head/title/text()',
    'news_date': '//time[@itemprop="datePublished"]/@datetime',
    'news_abstract': '//h2[@class="content-head__subtitle"]/text()|//meta[@name="description"]/@content',
    'news_body': '//div[@class="mc-article-body"]//p/text()',
    'news_section': '//div[@class="header-title-content"]/a/text()',
    'news_tags': '//ul[@class="entities__list"]//a/text()'
}


class G1News(Crawler):
    _NEWS_API: str
    _SEARCH_API: str
    _API_CONFIG: dict

    def __init__(self) -> None:
        with open('./config/portal_g1/news_api.json') as config_api:
            self._API_CONFIG = json.load(config_api)

        self._NEWS_API = self._API_CONFIG['api_url']['news_engine']
        self._SEARCH_API = self._API_CONFIG['api_url']['search_engine']
        self._ERRORS = (
            requests.exceptions.ReadTimeout, requests.exceptions.InvalidSchema, requests.exceptions.MissingSchema
        )

    def _retrieve_news_by_region(self, regions: list, max_pages: int = -1) -> Iterable[str]:
        for region in regions:
            for i in count():
                try:
                    page = SESSION.get(
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
                page = SESSION.get(
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

    def retrieve_news(self, regions: list = None, max_pages: int = -1) -> List[str]:
        news_urls = []
        if regions is None:
            news_urls = [url for url in self._retrieve_news_brazil(max_pages=max_pages)]

        if regions is not None:
            news_urls = [url for url in self._retrieve_news_by_region(regions=regions, max_pages=max_pages)]

        return news_urls

    def parse_news(self, news_urls: list, parse_body: bool = False) -> Iterable[dict]:
        parsed_counter = 0
        for i, url in enumerate(news_urls):
            logger.info(f"Article {i+1} >> Parsing data at {datetime.now()}.")
            parsed_news = {
                'title': str,
                'abstract': str,
                'date': Union[datetime, str, None],
                'section': str,
                'region': str,
                'url': url,
                'platform': 'G1',
                'tags': str,
                'type': str,
                'body': str,
                'html': bytes,
            }
            try:
                page = SESSION.get(url)
                parsed_news['title'] = page.html.xpath(
                    XPATH_DATA['news_title'], first=True
                )

                parsed_news['abstract'] = page.html.xpath(
                    XPATH_DATA['news_abstract'], first=True
                )

                raw_date = page.html.xpath(XPATH_DATA['news_date'], first=True)
                if raw_date is not None:
                    parsed_news['date'] = datetime.strptime(raw_date, "%Y-%m-%dT%H:%M:%S.%fZ")
                else:
                    parsed_news['date'] = None

                parsed_news['section'] = page.html.xpath(
                    XPATH_DATA['news_section'], first=True
                )

                parsed_news['region'] = url.split('/')[3].upper() if url.split(
                    '/')[3] in self._API_CONFIG['regions'].keys() else 'N/A'

                parsed_news['tags'] = '|'.join(
                    page.html.xpath(XPATH_DATA['news_tags'])
                ) if len(page.html.xpath(XPATH_DATA['news_tags'])) != 0 else 'N/A'

                parsed_news['type'] = 'Vídeo' if "video" in parsed_news['url'] else "Notícia"

                parsed_news['body'] = ''.join(page.html.xpath(
                    XPATH_DATA['news_body']
                )) if parse_body and len(page.html.xpath(XPATH_DATA['news_body'])) > 0 else None

                parsed_news['html'] = page.content

                parsed_counter += 1

                logger.success(f"Article {i+1} >> Data parsed successfully!.")
                yield parsed_news
            except self._ERRORS as error:
                logger.error(f'Error parsing data from the page. Skipping. Error: {error}')
                continue

        logger.success(
            f"All the data have been parsed successfully! "
            f"{parsed_counter} of {len(news_urls)} news had the data extracted."
        )

    def search_news(self, keywords: list, max_pages: int = -1) -> List[str]:
        news_urls = []
        for keyword in keywords:
            logger.info(f"Retrieving news from G1 associated with the Keyword \"{keyword}\".")
            for i in count():
                page = SESSION.get(self._SEARCH_API.format(keyword, str(i+1)))
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

    def parse_url(self, url: str) -> dict:
        if 'g1.globo.com' in url:
            data = [data for data in self.parse_news([url], parse_body=True)]
            return data[0]
