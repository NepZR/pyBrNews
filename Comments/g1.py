import json
from datetime import datetime
from urllib.parse import unquote

import requests.exceptions
from requests_html import HTMLSession, HTML
from typing import Union, List, Optional

from loguru import logger
from Comments.crawler import Crawler

SESSION = HTMLSession()


class G1Comments(Crawler):
    _COMMENTS_API: str
    _API_CONFIG: dict

    def __init__(self) -> None:
        with open("./config/portal_g1/comments_api.json") as config_api:
            self._API_CONFIG = json.load(config_api)

        self._COMMENTS_API = self._API_CONFIG["api_url"]["comments_engine"]
        self._API_PARAMS = self._API_CONFIG["params"]
        self._ERRORS = (
            requests.exceptions.ReadTimeout, requests.exceptions.InvalidSchema, requests.exceptions.MissingSchema
        )

    def _get_comment_data(self, news_url: str) -> Optional[List[dict]]:
        parameters = dict(self._API_PARAMS)
        parameters["variables"] = parameters["variables"].replace("@", news_url)

        response = SESSION.get(url=news_url, params=parameters)
        if response.status_code != 200:
            logger.error(f"Error while getting comments from {news_url} @ Status Code: {response.status_code}")
            return None

        try:
            news_data = response.json()['data']['story']['comments']['edges']
        except json.decoder.JSONDecodeError:
            news_data = None

        if news_data is not None:
            return news_data

        return None

    def parse_comments(self, news_list: List[dict]) -> List[dict]:
        comments = []

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

                comments.append(data)

        return comments
