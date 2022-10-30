import csv
import json
import traceback
from datetime import datetime
from typing import List, Iterable, Optional

import pymongo
import pymongo.database
import pymongo.errors
from loguru import logger


class PyBrNewsDB:
    """
    pyBrNews Database Class to use MongoDB database to store all article and comment data from the platforms.

    By default, uses the standard MongoDB host and port (localhost:27017). Can be changed with set_connection,
    with the parameters host and port.

    Example: set_connection(host="192.168.0.1", port: 88890).
    """
    def __init__(self, data_kind: str = "news") -> None:
        if "news" not in data_kind and "comments" not in data_kind:
            raise ValueError(
                f"An invalid kind of data for database [ {data_kind} ] was supplied. Review and try again."
            )

        self.client: Optional[pymongo.MongoClient] = None
        self.db: Optional[pymongo.database.Database] = None

        self.set_connection()
        self.collection = self.db.get_collection(data_kind)

    def set_connection(self, host: str = "localhost", port: int = 27017) -> None:
        self.client = pymongo.MongoClient(host=host, port=port)
        self.db = self.client.get_database(name="pyBrNews")

    def insert_data(self, parsed_data: dict) -> None:
        """
        Inserts the parsed data from a news article or extracted comment into the DB Backend (MongoDB - pyMongo).

        Parameters:
            parsed_data (dict): Dictionary containing the parsed data from a news article or comment.
        Returns:
            None: Shows a success message if the insertion occurred normally. If not, shows an error message.
        """
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
        """
        Checks if the parsed data is already in the database and prevents from being duplicated
        in the crawler execution.

        Parameters:
            parsed_data (dict): Dictionary containing the parsed data from a news article or comment.
        Returns:
            bool: True if the given parsed data is already in the database. False if not.
        """
        check_params = {
            "url": parsed_data["url"],
            "date": parsed_data["date"],
        }

        documents = self.collection.find_one(check_params)
        if documents is None:
            return False

        return True


class PyBrNewsFS:
    """
    pyBrNews File System Class for exporting data without using the MongoDB database. Allows to export parsed data into
    individual JSON or condenses all the parsed data into a CSV file for external usage.

    By default, exports all the files into the current work directory. To alter the save path, call the set_save_path()
    method, passing the attribute "fs_save_path" with the desired directory ending with a slash.
    """
    def __init__(self) -> None:
        self.save_path = ""

    def set_save_path(self, fs_save_path: str) -> None:
        """
        Sets the save path for all the exported data generated by this Class.

        Example: set_save_path(fs_save_path="/home/ubuntu/newsData/")

        Parameters:
             fs_save_path (str): Desired save path directory, ending with a slash.
        """
        if "/" not in fs_save_path[-1]:
            raise ValueError("End the save path with a slash ( / ).")

        self.save_path = fs_save_path

    def to_json(self, parsed_data: dict) -> None:
        """
        Using the parsed data dictionary from a news article or a comment, export the data as an individual JSON file.

        Parameters:
            parsed_data (dict): Dictionary containing the parsed data from a news article or a comment.
        """
        if parsed_data is None:
            raise AttributeError("Parsed Data Dictionary cannot be an NoneType value.")

        export_time = datetime.today().strftime("%Y_%m_%d_%H_%M_%S")
        file_name = f"ParsedNewsData_{export_time}.csv"
        try:
            with open(f"{self.save_path}{file_name}", mode="w", encoding="utf-8") as json_file:
                json.dump(parsed_data, json_file, ensure_ascii=False, indent=4)
        except OSError:
            logger.error(
                "An error occurred while attempting to save the JSON file. Review the save path and the data, and try "
                "again."
            )

    @staticmethod
    def _remove_null_values(raw_full_data: List[dict]) -> Iterable[dict]:
        """
        By a given list of dictionaries containing the parsed data from news or comments, yields per iteration the dict
        only if the item is not None.

        Parameters:
            raw_full_data (List[dict]): List containing the original dictionaries of parsed data (incl. None).
        Returns:
            Iterable[dict]: Per iteration -> If the item is not None, yields the parsed data dictionary.
        """
        for data in raw_full_data:
            if data is not None:
                return data

    @staticmethod
    def check_duplicates(parsed_data: dict = None) -> bool:
        """
        Placeholder method, mirroring the existing one in the PyBrNewsDB Class. Just returns False because is a FS data
        structure.

        Parameters:
            parsed_data (dict): Dictionary containing the parsed data from a news article or comment.
        Returns:
            bool: Because it is a FS Class, it does not check for duplicates. Returns False.
        """
        if parsed_data is not None:
            logger.warning("PyBrNews File System in use. Checking for duplicates only works on the PyBrNews Database.")

        return False

    def export_all_data(self, full_data: List[dict]) -> None:
        """
        By a given list of dictionaries containing the parsed data from news or comments, export in a CSV file
        containing all data.

        Parameters:
            full_data (List[dict]): List containing the dictionaries of parsed data.
        """
        export_time = datetime.today().strftime("%Y_%m_%d_%H_%M_%S")
        export_data = [data for data in self._remove_null_values(raw_full_data=full_data)]

        if len(full_data) == 0:
            raise ValueError(f"An empty list of parsed data cannot be used.")

        header = [
            "title", "abstract", "date", "section", "region", "url", "platform",
            "tags", "type", "body", "id_data", "html",
        ]

        file_name = f"ParsedNewsData_{export_time}.csv"
        try:
            with open(f"{self.save_path}{file_name}", mode="w", encoding="utf-8") as export_file:
                writer = csv.DictWriter(export_file, fieldnames=header)
                writer.writeheader()
                writer.writerows(export_data)
        except OSError:
            logger.error(
                "An error occurred while attempting to save the CSV file. Review the save path and the data, and try "
                "again."
            )
