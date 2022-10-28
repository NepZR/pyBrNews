import json.decoder
import time
from datetime import datetime
from itertools import count
from typing import List, Iterable, Optional

import requests.exceptions
import urllib3.exceptions
from loguru import logger
from requests_html import HTMLSession, Element, HTML

from .crawler import Crawler

SESSION = HTMLSession()


class FolhaComments(Crawler):
    def __init__(self) -> None:
        self._XPATH = {
            'comment_items': '//li[@class="c-list-comments__item"]',
            'comment_author': '//strong[@class="c-list-comments__user"]/text()',
            'comment_date': '//time[@class="c-list-comments__date"]/@datetime',
            'comment_text': '//p[@class="c-list-comments__comment"]/text()',
            'comment_upvote': '//button[@class="c-list-comments__rating"]/span/text()',
            'comment_id': '//button[@class="c-list-comments__rating"]/@data-comment-rating',
        }
        self._COMMENTS_API = 'https://comentarios1.folha.uol.com.br/comentarios/{}?sr={}'
        self._COMMENTS_ENGINE = 'https://comentarios1.folha.uol.com.br/comentarios.jsonp'
        self._ERRORS = (
            requests.exceptions.ReadTimeout, requests.exceptions.InvalidSchema, requests.exceptions.MissingSchema,
            urllib3.exceptions.ConnectionError, urllib3.exceptions.ProtocolError, ConnectionResetError,
            requests.exceptions.ConnectionError, requests.exceptions.ChunkedEncodingError
        )

    def _make_request(self, target_url: str, payload: dict = None, request_data: dict = None) -> Optional[HTML]:
        for _ in range(100):
            try:
                if (payload and request_data) is None:
                    response = SESSION.get(url=target_url)
                else:
                    response = SESSION.get(url=target_url, params=payload, cookies=request_data)

                if response.status_code == 200:
                    html_data = HTML(html=response.content, url=response.url)
                    return html_data

            except self._ERRORS:
                logger.warning(
                    f"Folha de São Paulo servers are trying to break the capture. Waiting 5 seconds before retrying."
                )
                SESSION.cookies.clear_session_cookies()
                time.sleep(5)

        return None

    @staticmethod
    def _gen_pagination() -> Iterable[int]:
        for page_index in count():
            logger.info(f"Getting comments from Page {page_index+1}.")
            page_number = 1 + (page_index * 50)
            yield page_number

    def _get_api_id(self, news_id_data: dict) -> Optional[int]:
        payload = {
            'service_name': news_id_data['service_name'],
            'type': news_id_data['data_type'],
            'limit': '1',
            'show_replies': 'false',
            'show_with_alternate': 'false',
            'link_format': 'html',
            'order_by': 'create',
            'callback': 'get_comments',
            'category_name': news_id_data['category_name'],
            'external_id': news_id_data['article_id'],
        }

        access_data = {
            'folha_ga_userType': 'not_logged',
            'folha_ga_loginType': 'not_logged',
            'folha_ga_userGroup': 'visitor',
            'folha_ga_swgt': 'sub_na',
        }

        response = self._make_request(target_url=self._COMMENTS_ENGINE, payload=payload, request_data=access_data)
        try:
            raw_data = response.html.replace("get_comments( ", "").replace(" ) ;", "")
            data = json.loads(raw_data)

            api_id = int(data['subject']['subject_id'])

            return api_id
        except (ValueError, KeyError, json.decoder.JSONDecodeError):
            return None

    def _get_comment_data(self, news_id: int) -> Iterable[Element]:
        logger.warning(f"Starting data extraction for comments from Article ID {news_id}.")
        total_comments = 0
        for page in self._gen_pagination():
            target_url = str(self._COMMENTS_API).format(news_id, page)

            response = self._make_request(target_url=target_url)
            if not response.xpath(self._XPATH["comment_items"]):
                break

            comments = response.xpath(self._XPATH["comment_items"])
            total_comments += len(comments)
            logger.info(f"Current number of comments acquired from ID {news_id}: {total_comments}.")
            yield from comments

        logger.success(
            f"A total of {total_comments} comments have been extracted from ID {news_id}! Finished at {datetime.now()}."
        )

    def _extract_author(self, comment_node: Element) -> Optional[str]:
        author = comment_node.xpath(self._XPATH['comment_author'], first=True)
        if author is not None:
            return author

        return None

    def _extract_date(self, comment_node: Element) -> Optional[datetime]:
        raw_date = comment_node.xpath(self._XPATH['comment_date'], first=True)
        if raw_date is not None:
            published_date = datetime.strptime(raw_date, "%Y-%m-%d %H:%M:%S")
            return published_date

        return None

    def _extract_upvote(self, comment_node: Element) -> Optional[int]:
        target_data = comment_node.xpath(self._XPATH['comment_upvote'], first=True)
        if target_data is not None:
            upvote = int(target_data)
            return upvote

        return None

    def _extract_comment_text(self, comment_node: Element) -> Optional[str]:
        comment_text = comment_node.xpath(self._XPATH['comment_text'], first=True)
        if comment_text is not None:
            return comment_text

        return None

    def _extract_comment_id(self, comment_node: Element) -> Optional[int]:
        comment_id = comment_node.xpath(self._XPATH['comment_id'], first=True)
        if comment_id is not None:
            return int(comment_id)

        return None

    def parse_comments(self, news_list: List[dict]) -> Iterable[dict]:
        for news_data in news_list:
            logger.info(f"Checking if \"{news_data['title']}\" have comments.")
            id_data = news_data["id_data"]
            if id_data is None:
                logger.warning(f"No comments found. Proceeding to the next one.")
                continue

            news_id = self._get_api_id(news_id_data=id_data)
            if news_id is None:
                logger.warning(f"No comments found. Proceeding to the next one.")
                continue

            raw_data = [data for data in self._get_comment_data(news_id=news_id)]
            if len(raw_data) == 0:
                continue

            for comment in raw_data:
                if comment is None:
                    continue

                data = {
                    "author": self._extract_author(comment_node=comment),
                    "date": self._extract_date(comment_node=comment),
                    "upvote": self._extract_upvote(comment_node=comment),
                    "news_data": {
                        "title": news_data["title"],
                        "region": news_data["region"],
                        "news_id": news_data["id_data"]["article_id"],
                        "api_id": news_id,
                        "api_url": f"https://comentarios1.folha.uol.com.br/comentarios/{news_id}",
                        "url": news_data["url"],
                    },
                    "comment": self._extract_comment_text(comment_node=comment),
                    "comment_id": self._extract_comment_id(comment_node=comment),
                    "platform": news_data["platform"],
                }

                yield data
