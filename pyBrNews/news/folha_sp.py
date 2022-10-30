import re
import time
from datetime import datetime
from itertools import count
from typing import Optional, List, Iterable
from urllib.parse import unquote

from loguru import logger
from requests_html import HTML

from .crawler import Crawler

XPATH_DATA = {
    'news_title': '//h1[@class="c-content-head__title"]/text()|//h1[@itemprop="headline"]/text()|'
                  '//meta[@property="og:title"]/@content|//head/title/text()',
    'news_date': '//meta[@property="article:published_time"]/@content|//time[@itemprop="datePublished"]/@datetime',
    'news_abstract': '//h2[@class="c-content-head__subtitle"]/text()|//h2[@itemprop="alternativeHeadline"]/text()|'
                     '//meta[@property="og:description"]/@content',
    'news_body': '//div[@itemprop="articleBody"]//p/text()|//div[@class="c-news__body"]//p/text()',
    'news_section': '//meta[@property="article:section"]/@content',
    'news_region': '//strong[@class="c-signature__location"]//text()|'
                   '//div[@class="c-signature c-signature--left"]//text()',
    'news_tags': '//meta[@name="keywords"]/@content',
    'news_type': '//meta[@property="og:type"]/@content',
    'news_id': "//section[@id='comentarios']",
}


class FolhaNews(Crawler):
    def __init__(self, use_database: bool = True) -> None:
        super().__init__(use_database=use_database)

        self._SEARCH_API = "https://search.folha.uol.com.br/?q={}&site=todos"

    def _make_request(self, target_url: str) -> Optional[HTML]:
        for _ in range(100):
            try:
                response = self.SESSION.get(url=target_url)
                if response.status_code == 200:
                    html_data = HTML(html=response.content, url=response.url)
                    return html_data

            except self._ERRORS:
                logger.warning(
                    f"Folha de São Paulo servers are trying to break the capture. Waiting 5 seconds before retrying."
                )
                self.SESSION.cookies.clear_session_cookies()
                time.sleep(5)

        return None

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
            published_date = datetime.strptime(raw_date, "%Y-%m-%d %H:%M:%S")
            return published_date

        return None

    @staticmethod
    def _extract_section(article_page: HTML) -> Optional[str]:
        section = article_page.xpath(XPATH_DATA['news_section'], first=True)
        if section is not None:
            return section

        return None

    def _extract_region(self, article_page: HTML) -> Optional[str]:
        region = article_page.xpath(XPATH_DATA['news_region'], first=True)
        if region is not None:
            return region

        return None

    @staticmethod
    def _extract_tags(article_page: HTML) -> Optional[str]:
        tags = article_page.xpath(XPATH_DATA['news_tags'], first=True)
        if tags is not None:
            return tags

        return None

    @staticmethod
    def _extract_type(article_data: HTML) -> Optional[str]:
        news_type = article_data.xpath(XPATH_DATA['news_type'], first=True)
        if news_type is not None:
            return news_type

        return None

    @staticmethod
    def _extract_body(article_page: HTML) -> Optional[str]:
        article_body = article_page.xpath(XPATH_DATA['news_body'])
        if article_body is not None:
            body = ' '.join(article_body)
            re.sub(r"\s{2,}", body, "")
            return body

        return None

    @staticmethod
    def _extract_id_data(article_page: HTML) -> Optional[dict]:
        try:
            news_id = dict(article_page.xpath(XPATH_DATA['news_id'], first=True).attrs)
        except AttributeError:
            return None

        if news_id is not None:
            news_id_data = {}
            if "data-section" in news_id.keys():
                news_id_data['category_name'] = news_id['data-section']
            if "data-id" in news_id.keys():
                news_id_data['article_id'] = news_id['data-id']
            if "data-service" in news_id.keys():
                news_id_data['service_name'] = news_id['data-service']
            if "data-type" in news_id.keys():
                news_id_data['data_type'] = news_id['data-type']

            if ('category_name' and 'article_id' and 'service_name' and 'data_type') in news_id_data.keys():
                return news_id_data

        return None

    def parse_news(self, news_urls: list, parse_body: bool = False, save_html: bool = True) -> Iterable[dict]:
        parsed_counter = 0
        for i, url in enumerate(news_urls):
            if '1.folha.uol.com.br' not in url:
                continue

            page = self._make_request(target_url=url)
            logger.info(f"Article {i+1} >> Parsing data at {datetime.now()}.")

            parsed_news = {
                'title': self._extract_title(article_page=page),
                'abstract': self._extract_abstract(article_page=page),
                'date': self._extract_date(article_page=page),
                'section': self._extract_section(article_page=page),
                'region':  self._extract_region(article_page=page),
                'url': url,
                'platform': 'Folha de São Paulo',
                'tags': self._extract_tags(article_page=page),
                'type': self._extract_type(article_data=page),
                'body': self._extract_body(article_page=page),
                'id_data': self._extract_id_data(article_page=page),
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

    def search_news(self, keywords: list, max_pages: int = -1) -> List[str]:
        news_urls = []
        for keyword in keywords:
            logger.info(f"Retrieving news from Folha de São Paulo associated with the Keyword \"{keyword}\".")
            page = self._make_request(self._SEARCH_API.format(keyword))
            if page is None:
                continue

            for i in count():
                if not page.xpath('//div[@class="c-headline__content"]'):
                    break

                logger.info(
                    f"{keyword.title()} >> Getting data from Page {i+1}. Current URLs acquired: {len(news_urls)}."
                )
                news_list = [url for url in page.xpath(
                    '//div[@class="c-headline__content"]/a/@href'
                )]
                news_urls += (url for url in news_list if '1.folha.uol.com.br' in url)

                if i+1 == max_pages:
                    break

                if not page.xpath('//li[@class="c-pagination__arrow"]'):
                    break

                next_page = unquote(page.xpath('//li[@class="c-pagination__arrow"]/a/@href', first=True))
                page = self._make_request(target_url=next_page)
                if page is None:
                    break

        logger.success(
            f"News retrieved successfully! A total of {len(news_urls)} articles have been found."
        )

        return news_urls
