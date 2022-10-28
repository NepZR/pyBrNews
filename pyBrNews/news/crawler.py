from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

import requests.exceptions
import urllib3.exceptions
from requests_html import HTMLSession, HTML

from ..config.database import PyBrNewsDB


class Crawler(ABC):
    def __init__(self) -> None:
        self.SESSION = HTMLSession()
        self._DB = PyBrNewsDB()
        self._ERRORS = (
            requests.exceptions.ReadTimeout, requests.exceptions.InvalidSchema, requests.exceptions.MissingSchema,
            urllib3.exceptions.ConnectionError, urllib3.exceptions.ProtocolError, ConnectionResetError,
            requests.exceptions.ConnectionError, requests.exceptions.ChunkedEncodingError
        )

    @abstractmethod
    def parse_news(self, news_urls: list, parse_body: bool = False, save_html: bool = True):
        pass

    @abstractmethod
    def search_news(self, keywords: list, max_pages: int = -1):
        pass

    @staticmethod
    @abstractmethod
    def _extract_title(article_page: HTML) -> Optional[str]:
        pass

    @staticmethod
    @abstractmethod
    def _extract_abstract(article_page: HTML) -> Optional[str]:
        pass

    @staticmethod
    @abstractmethod
    def _extract_date(article_page: HTML) -> Optional[datetime]:
        pass

    @staticmethod
    @abstractmethod
    def _extract_section(article_page: HTML) -> Optional[str]:
        pass

    @abstractmethod
    def _extract_region(self, article_page: HTML) -> Optional[str]:
        pass

    @staticmethod
    @abstractmethod
    def _extract_tags(article_page: HTML) -> Optional[str]:
        pass

    @staticmethod
    @abstractmethod
    def _extract_type(article_page: HTML) -> Optional[str]:
        pass

    @staticmethod
    @abstractmethod
    def _extract_body(article_page: HTML) -> Optional[str]:
        pass
