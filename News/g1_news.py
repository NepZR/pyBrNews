import csv
import json
from datetime import datetime
from urllib.parse import unquote

import requests.exceptions
from requests_html import HTMLSession

from News.crawler import Crawler

SESSION = HTMLSession()
XPATH_DATA = {
    'news_title': '//div[@class="title"]/h1/text()|//meta[@name="title"]/@content',
    'news_date': '//time[@itemprop="datePublished"]/@datetime',
    'news_abstract': '//h2[@class="content-head__subtitle"]/text()|//meta[@name="description"]/@content',
    'news_content': '//div[@class="mc-article-body"]//p/text()',
    'news_section': '//div[@class="header-title-content"]/a/text()',
    'news_tags': '//ul[@class="entities__list"]//a/text()'
}


class G1News(Crawler):
    _NEWS_API: str
    _SEARCH_API: str
    _API_CONFIG: dict

    def __init__(self):
        with open('./config/portal_g1/news_api.json') as config_api:
            self._API_CONFIG = json.load(config_api)

        self._NEWS_API = self._API_CONFIG['api_url']['news_engine']
        self._SEARCH_API = self._API_CONFIG['api_url']['search_engine']

    def retrieve_news(self, max_pages: int, region_lock: bool = False, regions: list = None):
        news_urls = []
        if not region_lock:
            for i in range(max_pages):
                page = SESSION.get(self._NEWS_API.format(self._API_CONFIG['regions']['brasil'], str(i + 1))).json()
                for item in page['items']:
                    news_urls.append(item['content']['url'] if ('materia' in item['type']) else ())
        elif region_lock and regions is not None:
            for region in regions:
                for i in range(max_pages):
                    page = SESSION.get(self._NEWS_API.format(self._API_CONFIG['regions'][region], str(i + 1))).json()
                    for item in page['items']:
                        news_urls.append(item['content']['url'] if ('materia' in item['type']) else ())
        return news_urls

    def parse_news(self, news_urls: list, parse_content: bool = False):
        parsed_data = []
        for url in news_urls:
            parsed_news = {
                'title': str,
                'abstract': str,
                'date': str,
                'section': str,
                'region': str,
                'url': url,
                'platform': 'G1',
                'tags': str,
                'content': str,
            }
            try:
                page = SESSION.get(url)
                parsed_news['title'] = page.html.xpath(
                    XPATH_DATA['news_title'], first=True
                )

                parsed_news['abstract'] = page.html.xpath(
                    XPATH_DATA['news_abstract'], first=True
                )

                parsed_news['date'] = page.html.xpath(
                    XPATH_DATA['news_date'], first=True
                )

                parsed_news['section'] = page.html.xpath(
                    XPATH_DATA['news_section'], first=True
                )

                parsed_news['region'] = url.split('/')[3] if url.split(
                    '/')[3] in self._API_CONFIG['regions'].keys() else 'N/A'

                parsed_news['tags'] = '|'.join(
                    page.html.xpath(XPATH_DATA['news_tags'])
                ) if len(page.html.xpath(XPATH_DATA['news_tags'])) != 0 else 'N/A'

                parsed_news['content'] = ''.join(page.html.xpath(
                    XPATH_DATA['news_content']
                )) if parse_content else ''
                parsed_data.append(parsed_news)
            except (requests.exceptions.ReadTimeout, requests.exceptions.InvalidSchema) as error:
                print(f'Error parsing the page. Skipping. Error: {error}')
                continue
        return parsed_data

    def search_news(self, keywords: list, max_pages: int):
        news_urls = []
        for keyword in keywords:
            for i in range(max_pages):
                page = SESSION.get(self._SEARCH_API.format(keyword, str(i+1)))
                news_list = [unquote(url).split('u=')[1].split('&')[0] for url in page.html.xpath(
                    '//div[@class="widget--info__text-container"]/a/@href'
                )]
                news_urls += (url for url in news_list if 'g1.globo.com' in url)
        return news_urls

    def parse_url(self, url: str):
        if 'g1.globo.com' in url:
            return self.parse_news([url])[0]
