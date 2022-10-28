import json
from datetime import datetime
from typing import List, Optional, Iterable

import requests.exceptions
from loguru import logger
from requests_html import HTMLSession, HTML

from .crawler import Crawler
from ..config import g1_api

SESSION = HTMLSession()


class G1Comments(Crawler):
    _COMMENTS_API: str
    _API_CONFIG: dict

    def __init__(self) -> None:
        self._API_CONFIG = g1_api.comments_config

        self._COMMENTS_API = self._API_CONFIG["api_url"]["comments_engine"]
        self._COUNT_API = self._API_CONFIG["api_url"]["count_engine"]
        self._API_PARAMS = self._API_CONFIG["params"]
        self._ERRORS = (
            requests.exceptions.ReadTimeout, requests.exceptions.InvalidSchema, requests.exceptions.MissingSchema
        )

    def _news_have_comments(self, target_url: str) -> bool:
        response = SESSION.get(url=f"{self._COUNT_API}{target_url}")
        if response.status_code != 200:
            return False

        response_data = response.json()

        count_data = int(response_data["count"]) if response_data["count"] is not None else None
        if count_data is None:
            return False
        if count_data == 0:
            return False

        return True

    def _get_comment_data(self, news_url: str) -> Optional[List[dict]]:
        if self._news_have_comments(target_url=news_url) is False:
            return None

        parameters = dict(self._API_PARAMS)
        parameters["variables"] = str(parameters["variables"].replace("@", news_url))

        response = SESSION.get(url=self._COMMENTS_API, params=parameters)
        if response.status_code != 200:
            logger.error(f"Error while getting comments from {news_url} @ Status Code: {response.status_code}")
            return None

        try:
            news_data = response.json()['data']['story']['comments']['edges']
        except (json.decoder.JSONDecodeError, TypeError):
            news_data = None

        if news_data is not None:
            return news_data

        return None

    def parse_comments(self, news_list: List[dict]) -> Iterable[dict]:
        for news_data in news_list:
            url = news_data["url"]

            raw_data = self._get_comment_data(news_url=url)
            if raw_data is None:
                continue

            for comment_node in raw_data:
                node_data = comment_node["node"]
                if len(node_data["body"]) == 0:
                    continue

                data = {
                    "author": node_data["author"]["username"],
                    "date": datetime.strptime(node_data["createdAt"], "%Y-%m-%dT%H:%M:%S.%fZ"),
                    "upvote": int(node_data["actionCounts"]["reaction"]["total"]),
                    "news_data": {
                        "title": news_data["title"],
                        "region": news_data["region"],
                        "url": url,
                    },
                    "comment": HTML(html=node_data["body"]).full_text,
                    "g1_id": node_data["id"],
                    "platform": "G1",
                }

                yield data
