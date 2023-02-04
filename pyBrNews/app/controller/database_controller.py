import json
from typing import Union, List, Tuple
from pyBrNews.config.database import PyBrNewsDB, PyBrNewsES, PyBrNewsFS


class DatabaseController:
    def __init__(self, db_backend: str = "mongodb") -> None:
        self.database: Union[PyBrNewsDB, PyBrNewsES] = self._set_db_backend(db_backend=db_backend)
        self.fs_database: PyBrNewsFS = PyBrNewsFS()

    @staticmethod
    def _set_db_backend(db_backend: str) -> Union[PyBrNewsDB, PyBrNewsES]:
        if "elasticsearch" in db_backend:
            db = PyBrNewsES()
        else:
            db = PyBrNewsDB()

        return db

    def retrieve_doc_data(self, document_id: str) -> Tuple[dict, List[str]]:
        document_data = self.database.get_data(doc_id=document_id)
        fields = []

        for field in document_data.keys():
            if "_id" in field or "entry_dt" in field:
                continue

            fields.append(field)

        return document_data, fields

    def import_ext_data(self, file_src: str) -> None:
        with open(file_src, "rb") as input_data:
            import_data = json.load(input_data)

        self.database.insert_data(parsed_data=import_data)


if __name__ == "__main__":
    controller = DatabaseController()
    pass
