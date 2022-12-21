from typing import List

from pyBrNews.app.controller.database_controller import DatabaseController
from pyBrNews.news.g1 import G1News
from pyBrNews.news.folha_sp import FolhaNews
from pyBrNews.news.exame import ExameNews


class ViewController:
    def __init__(self) -> None:
        self.g1 = G1News()
        self.folha = FolhaNews()
        self.exame = ExameNews()
        self.db_controller = DatabaseController()

    def search_and_insert_news(self, search_params: dict) -> List[List[str]]:
        news_urls = {"g1": None, "folhasp": None, "exame": None}
        search_term = search_params["search_keyword"]

        if search_params["news_platform_g1"]:
            news_urls["g1"] = self.g1.search_news(keywords=[search_term])
            for article_data in self.g1.parse_news(news_urls=news_urls["g1"], parse_body=True, save_html=False):
                article_data["search_keyword"] = search_term
                self.db_controller.insert_data(parsed_data=article_data)

        if search_params["news_platform_folhasp"]:
            news_urls["folhasp"] = self.folha.search_news(keywords=[search_term])
            for article_data in self.folha.parse_news(news_urls=news_urls["folhasp"], parse_body=True, save_html=False):
                article_data["search_keyword"] = search_term
                self.db_controller.insert_data(parsed_data=article_data)

        if search_params["news_platform_exame"]:
            news_urls["exame"] = self.exame.search_news(keywords=[search_term])
            for article_data in self.exame.parse_news(news_urls=news_urls["exame"], parse_body=True, save_html=False):
                article_data["search_keyword"] = search_term
                self.db_controller.insert_data(parsed_data=article_data)

        retrieved_data = [
            [data["title"], data["platform"]] for data in self.db_controller.collection.find(
                {"search_keyword": search_term}
            ).limit(30)
        ]
        return retrieved_data
