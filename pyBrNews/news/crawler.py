from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, List, Union, Iterable

import requests.exceptions
import urllib3.exceptions
from requests_html import HTMLSession, HTML

from ..config.database import PyBrNewsDB, PyBrNewsFS


class Crawler(ABC):
    def __init__(self, use_database: bool = True) -> None:
        self.SESSION = HTMLSession()

        self.DB: Union[PyBrNewsDB, PyBrNewsFS]
        if not use_database:
            self.DB = PyBrNewsFS()
        else:
            self.DB = PyBrNewsDB()

        self._ERRORS = (
            requests.exceptions.ReadTimeout, requests.exceptions.InvalidSchema, requests.exceptions.MissingSchema,
            urllib3.exceptions.ConnectionError, urllib3.exceptions.ProtocolError, ConnectionResetError,
            requests.exceptions.ConnectionError, requests.exceptions.ChunkedEncodingError
        )

    @abstractmethod
    def parse_news(self,
                   news_urls: List[Union[str, dict]],
                   parse_body: bool = False,
                   save_html: bool = True) -> Iterable[dict]:
        """
        Extracts all the data from the article in a given news platform by iterating over a URL list. Yields a
        dictionary containing all the parsed data from the article.

        Parameters:
            news_urls (List[str]): A list containing all the URLs or a data dict to be parsed from a given platform.
            parse_body (bool): Defines if the article body will be extracted.
            save_html (bool): Defines if the HTML bytes from the article will be extracted.
        Returns:
             Iterable[dict]: Dictionary containing all the article parsed data.
        """
        pass

    @abstractmethod
    def search_news(self,
                    keywords: List[str],
                    max_pages: int = -1) -> List[Union[str, dict]]:
        """
        Extracts all the data or URLs from the news platform based on the keywords given. Returns a list containing the
        URLs / data found for the keywords.

        Parameters:
            keywords (List[str]): A list containing all the keywords to be searched in the news platform.
            max_pages (int): Number of pages to have the articles URLs extracted from.
                             If not set, will catch until the last possible.
        Returns:
             List[Union[str, dict]]: List containing all the URLs / data found for the keywords.
        """
        pass

    @staticmethod
    @abstractmethod
    def _extract_title(article_page: HTML) -> Optional[str]:
        """
        Extracts the title of a given news article page and returns as a string for the parsed data dictionary.

        Parameters:
             article_page (HTML): A HTML object containing the data from the news article page.
        Returns:
            Optional[str]: The title of the news article. None if not found.
        """
        pass

    @staticmethod
    @abstractmethod
    def _extract_abstract(article_page: HTML) -> Optional[str]:
        """
        Extracts the abstract of a given news article page and returns as a string for the parsed data dictionary.

        Parameters:
             article_page (HTML): A HTML object containing the data from the news article page.
        Returns:
            Optional[str]: The abstract of the news article. None if not found.
        """
        pass

    @staticmethod
    @abstractmethod
    def _extract_date(article_page: HTML) -> Optional[datetime]:
        """
        Extracts the date of a given news article page and returns as a datetime for the parsed data dictionary.

        Parameters:
             article_page (HTML): A HTML object containing the data from the news article page.
        Returns:
            Optional[datetime]: The published date of the news article. None if not found.
        """
        pass

    @staticmethod
    @abstractmethod
    def _extract_section(article_page: HTML) -> Optional[str]:
        """
        Extracts the section of a given news article page and returns as a string for the parsed data dictionary.

        Parameters:
             article_page (HTML): A HTML object containing the data from the news article page.
        Returns:
            Optional[str]: The section name of the news article. None if not found.
        """
        pass

    @abstractmethod
    def _extract_region(self, article_page: HTML) -> Optional[str]:
        """
        Extracts the region of a given news article page and returns as a string for the parsed data dictionary.

        Parameters:
             article_page (HTML): A HTML object containing the data from the news article page.
        Returns:
            Optional[str]: The region of the news article. None if not found.
        """
        pass

    @staticmethod
    @abstractmethod
    def _extract_tags(article_data: Union[HTML, str]) -> Optional[str]:
        """
        Extracts the tags/keywords of a given news article page and returns as a string for the parsed data dictionary.

        Parameters:
             article_data (Union[HTML, str]): A HTML or string object containing the data from the news article page.
        Returns:
            Optional[str]: The tags/keywords of the news article. None if not found.
        """
        pass

    @staticmethod
    @abstractmethod
    def _extract_type(article_page: HTML) -> Optional[str]:
        """
        Extracts the type of a given news article page and returns as a string for the parsed data dictionary.

        Parameters:
             article_page (HTML): A HTML object containing the data from the news article page.
        Returns:
            Optional[str]: The type of the news article. None if not found.
        """
        pass

    @staticmethod
    @abstractmethod
    def _extract_body(article_page: HTML) -> Optional[str]:
        """
        Extracts the full body text of a given news article page and returns as a string for the parsed data dictionary.

        Parameters:
             article_page (HTML): A HTML object containing the data from the news article page.
        Returns:
            Optional[str]: The full body text of the news article. None if not found.
        """
        pass
