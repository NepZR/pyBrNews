from typing import Union, List
from pyBrNews.config.database import PyBrNewsDB, PyBrNewsES


class DatabaseController:
    def __init__(self, db_backend: str = "mongodb") -> None:
        self.database: Union[PyBrNewsDB, PyBrNewsES] = self._set_db_backend(db_backend=db_backend)

    @staticmethod
    def _set_db_backend(db_backend: str) -> Union[PyBrNewsDB, PyBrNewsES]:
        if "elasticsearch" in db_backend:
            db = PyBrNewsES()
        else:
            db = PyBrNewsDB()

        return db


if __name__ == "__main__":
    controller = DatabaseController()
    pass
