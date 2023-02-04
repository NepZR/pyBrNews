import PySimpleGUI

from typing import List, Optional, Tuple

from pyBrNews.app.controller.database_controller import DatabaseController
from pyBrNews.config.database import PyBrNewsDB
from pyBrNews.news.g1 import G1News
from pyBrNews.news.folha_sp import FolhaNews
from pyBrNews.news.exame import ExameNews


class ViewController:
    def __init__(self) -> None:
        self.g1 = G1News()
        self.folha = FolhaNews()
        self.exame = ExameNews()
        self.db_controller: Optional[DatabaseController] = None

        self.set_db_backend()

    def set_db_backend(self, db_backend: str = "mongodb") -> None:
        self.db_controller = DatabaseController(db_backend=db_backend.lower())

    def switch_db_backend(self) -> None:
        if type(self.db_controller.database) is PyBrNewsDB:
            self.set_db_backend(db_backend="elasticsearch")
        else:
            self.set_db_backend(db_backend="mongodb")

    def retrieve_db_backend_info(self) -> str:
        db_backend_info = "[DB Backend] "
        if type(self.db_controller.database) is PyBrNewsDB:
            db_backend_info += (
                f"PyBrNewsDB (MongoDB), connected in "
                f"{self.db_controller.database.host}:{self.db_controller.database.port}"
            )
        else:
            db_backend_info += (
                f"PyBrNewsES (ElasticSearch), connected in "
                f"{self.db_controller.database.host}:{self.db_controller.database.port}"
            )

        return db_backend_info

    def retrieve_db_switch_str(self) -> str:
        if type(self.db_controller.database) is PyBrNewsDB:
            db_switch_str = f"Switch to PyBrNewsES (ElasticSearch)"
        else:
            db_switch_str = f"Switch to PyBrNewsDB (MongoDB)"

        return db_switch_str

    def get_inspection_tool_fields(self, document_id: str) -> List[list]:
        document_data, available_fields = self.db_controller.retrieve_doc_data(document_id)
        inspect_elements = []
        for field in available_fields:
            if "_id" in field or "entry_dt" in field:
                continue
            inspect_element = [
                PySimpleGUI.Text(f'{field}: ', font=("Segoi UI", 11, "bold")),
                PySimpleGUI.InputText(
                    default_text=document_data[field], key=f'doc_data_inspect_{field}', expand_x=True, readonly=False
                )
            ]
            inspect_elements.append(inspect_element)

        return inspect_elements

    def trigger_document_deletion(
            self,
            doc_info: Tuple[str, str, str],
            user_interface: PySimpleGUI.Window,
            make_backup: bool = True
    ) -> None:
        doc_id = doc_info[2]

        self.db_controller.database.delete_data(doc_id=doc_id, make_backup=make_backup)
        for fields in user_interface.key_dict.keys():
            if "doc_data_inspect_" in str(fields):
                user_interface[fields].update("")

        updated_results_list = list(user_interface["-RESULT_DATA-"].get())
        rm_index = updated_results_list.index(doc_info)
        del updated_results_list[rm_index]

        user_interface["-RESULT_DATA-"].update(updated_results_list)
        user_interface[f"Inspection Tool (No Data)"].update("Inspection Tool (No Data)")

    def trigger_export_document(self, doc_id: str, export_path: str) -> None:
        self.db_controller.fs_database.set_save_path(fs_save_path=export_path)

        doc_data = self.db_controller.database.get_data(doc_id=doc_id)
        self.db_controller.fs_database.to_json(parsed_data=doc_data)

    def search_data(self, query_params: dict) -> List[List[str]]:
        platforms = []
        if query_params["search_query_platform_g1"]:
            platforms.append("Portal G1")
        if query_params["search_query_platform_folhasp"]:
            platforms.append("Folha de São Paulo")
        if query_params["search_query_platform_exame"]:
            platforms.append("Exame")

        if len(platforms) == 0:
            platforms = None

        search_query = (query_params["search_query_text"] + " and") if query_params["search_all_terms"] else (
            query_params["search_query_text"]
        )

        if len(search_query) < 1:
            search_query = None

        if "Please" in query_params["search_query_init_date"] and "Please" in query_params["search_query_final_date"]:
            search_init_final_date = None
        else:
            search_init_final_date = (query_params["search_query_init_date"], query_params["search_query_final_date"])

        search_limit = int(query_params["search_query_limit"])

        query_response = [data for data in self.db_controller.database.read_data(
            origin=platforms, search_query=search_query, init_final_year=search_init_final_date, limit=search_limit
        )]

        retrieved_data = [
            [data["title"], data["platform"], data["_id"]] for data in query_response
        ]
        return retrieved_data

    def search_and_insert_news(self, search_params: dict) -> List[List[str]]:
        news_urls = {"g1": None, "folhasp": None, "exame": None}
        search_term = search_params["search_keyword"]
        if not search_params["acquire_news_page_limit"].isnumeric():
            search_limit = 100
        else:
            search_limit = int(search_params["acquire_news_page_limit"])

        if search_params["news_platform_g1"]:
            news_urls["g1"] = self.g1.search_news(keywords=[search_term], max_pages=search_limit)
            for article_data in self.g1.parse_news(news_urls=news_urls["g1"], parse_body=True, save_html=False):
                article_data["search_keyword"] = search_term
                self.db_controller.database.insert_data(parsed_data=article_data)

        if search_params["news_platform_folhasp"]:
            news_urls["folhasp"] = self.folha.search_news(keywords=[search_term], max_pages=search_limit)
            for article_data in self.folha.parse_news(news_urls=news_urls["folhasp"], parse_body=True, save_html=False):
                article_data["search_keyword"] = search_term
                self.db_controller.database.insert_data(parsed_data=article_data)

        if search_params["news_platform_exame"]:
            news_urls["exame"] = self.exame.search_news(keywords=[search_term], max_pages=search_limit)
            for article_data in self.exame.parse_news(news_urls=news_urls["exame"], parse_body=True, save_html=False):
                article_data["search_keyword"] = search_term
                self.db_controller.database.insert_data(parsed_data=article_data)

        query_response = self.db_controller.database.collection.find(
                {"search_keyword": search_term}
            ).limit(30) if type(self.db_controller.database) is PyBrNewsDB else self.db_controller.database.db.search(
            index=self.db_controller.database.index, body={"query": {"bool": {"must": [{"match": {
                "search_keyword.keyword": search_term}}]}}}, size=30
        )["hits"]["hits"]["_source"]

        retrieved_data = [
            [data["title"], data["platform"]] for data in query_response
        ]
        return retrieved_data
