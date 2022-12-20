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

        self.user_interface.close()


if __name__ == '__main__':
    app = PyBrNews()
    app.run()
