from datetime import datetime

import traceback
import pymongo
from loguru import logger


class PyBrNewsDB:
    def __init__(self, data_kind: str = "news") -> None:
        if "news" not in data_kind and "comments" not in data_kind:
            raise ValueError(
                f"An invalid kind of data for database [ {data_kind} ] was supplied. Review and try again."
            )

        self.client = pymongo.MongoClient(port=27017)
        self.db = self.client.get_database(name="pyBrNews")

        self.collection = self.db.get_collection(data_kind)

    def insert_data(self, parsed_data: dict) -> None:
        parsed_data["entry_dt"] = datetime.now()

        try:
            inserted_data = self.collection.insert_one(parsed_data)
            logger.success(
                f"Data inserted into pyBrNews DB! Document ID {inserted_data.inserted_id} "
                f"successfully added to the news collection."
            )
        except Exception as e:
            logger.error(f"An error happened while attempting to insert the given data to the pyBrNews database.")
            logger.debug(f"Data URL: {parsed_data['url']}")
            logger.debug(f"{traceback.print_exception(e)}")

    def check_duplicates(self, parsed_data: dict) -> bool:
        check_params = {
            "url": parsed_data["url"],
            "date": parsed_data["date"],
        }

        documents = self.collection.find_one(check_params)
        if documents is None:
            return False

        return True
