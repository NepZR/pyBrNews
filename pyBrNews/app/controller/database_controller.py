from pyBrNews.config.database import PyBrNewsDB


class DatabaseController(PyBrNewsDB):
    def __init__(self) -> None:
        super().__init__()


if __name__ == "__main__":
    controller = DatabaseController()
    pass
