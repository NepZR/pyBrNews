from pyBrNews.app.view.view import PyBrNewsView


class PyBrNews(PyBrNewsView):
    def __init__(self) -> None:
        super().__init__()

    def run(self) -> None:
        while True:
            event, data = self.user_interface.read()

            if event is self.ui_handler.WIN_CLOSED or event in ("Exit", None):
                break
            elif "get_news" in event:
                retrieved_data = self.search_and_insert_news(search_params=data)
                self.user_interface["-OUTPUT_DATA-"].update(retrieved_data)
            elif "db_backend_set" in event:
                self.switch_db_backend()
                self.user_interface["-DB_BACKEND_INFO-"].update(self.retrieve_db_backend_info())
            elif "run_search_query" in event:
                data["search_query_init_date"] = self.user_interface["-QUERY_INIT_DT-"].get()
                data["search_query_final_date"] = self.user_interface["-QUERY_END_DT-"].get()
                query_data = self.search_data(query_params=data)
                self.user_interface["-RESULT_DATA-"].update(query_data)

        self.user_interface.close()


if __name__ == '__main__':
    app = PyBrNews()
    app.run()
