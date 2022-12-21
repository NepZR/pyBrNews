import csv
import json
import traceback
from datetime import datetime
from typing import List, Iterable, Optional, Union, Tuple

import pymongo
import pymongo.database
import pymongo.errors
from loguru import logger
import opensearchpy.exceptions
from opensearchpy import OpenSearch


class PyBrNewsDB:
    """
    pyBrNews Database Class to use MongoDB database to store all article and comment data from the platforms.

    By default, uses the standard MongoDB host and port (localhost:27017). Can be changed with set_connection,
    with the parameters host and port or while instancing the PyBrNewsDB object.

    Example: set_connection(host="192.168.0.1", port: 88890) or db = PyBrNewsDB(host="192.168.0.1", port: 88890).
    """
    def __init__(self, data_kind: str = "news", host: str = "localhost", port: int = 27017) -> None:
        if "news" not in data_kind and "comments" not in data_kind:
            raise ValueError(
                f"An invalid kind of data for database [ {data_kind} ] was supplied. Review and try again."
            )

        self.client: Optional[pymongo.MongoClient] = None
        self.db: Optional[pymongo.database.Database] = None

        self.set_connection(host=host, port=port)
        self.collection = self.db.get_collection(data_kind)
        self.backup = self.db.get_collection("backup")

    def set_connection(self, host: str = "localhost", port: int = 27017) -> None:
        """
        Sets the connection host:port parameters for the MongoDB. By default, uses the standard localhost:27017 for
        local usage.

        Parameters:
             host (str): Hostname or address to connect.
             port (int): Port to be used in the connection.
        """
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

    def read_data(
            self,
            origin: Optional[List[str]] = None,
            search_query: Optional[str] = None,
            init_final_year: Optional[Tuple[int]] = None,
            limit: int = 10
    ) -> Iterable[dict]:
        query = {}
        if origin is None and search_query is None and init_final_year is None:
            pass
        else:
            query.update(self._query_constructor(args=[origin, search_query, init_final_year]))

        for data in self.collection.find(query).limit(limit):
            yield data

    def update_data(self, payload: dict) -> dict:
        data_id = str(payload.pop("_id"))
        updated_data = self.collection.find_one_and_update(
            filter={"_id": data_id},
            update=payload
        )

        return updated_data

    def delete_data(self, doc_id: str, make_backup: bool = False) -> dict:
        data_backup = None
        if make_backup:
            data_backup = self.collection.find_one(filter=doc_id)

        removed_data = self.collection.delete_one(filter={"_id": doc_id}).raw_result

        if removed_data["acknowledged"] and data_backup is not None:
            del data_backup["_id"]
            self.backup.insert_one(dict(data_backup))

        return removed_data

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

    @staticmethod
    def _query_constructor(args: Optional[List[Union[List[str], Tuple[int], str]]] = None) -> dict:
        query = {}
        if args is None:
            return query

        for arg in args:
            if type(arg) is str:
                sharded_search = arg.split(" ")
                fields = ["title", "abstract", "body", "search_keyword"]
                _filter = "or" if "and" not in sharded_search else "and"
                del sharded_search[sharded_search.index(_filter)]

                if f"${_filter}" not in query.keys():
                    query[f"${_filter}"] = []

                for field in fields:
                    query[f"${_filter}"].append({field: {"$in": sharded_search}})

            elif type(arg) is tuple:
                query["date"] = {
                    "$gte": datetime(year=int(arg[0]), month=1, day=1),
                    "$lte": datetime(year=int(arg[1]), month=12, day=31)
                }

            elif type(arg) is list:
                data = [{"platform": {"$in": arg}}]
                if "$and" in query.keys():
                    query["$and"] += data
                else:
                    query["$and"] = data
            else:
                logger.warning("Passed parameters does not match any of the accepted ones. Using default query option.")

        return query


class PyBrNewsES:
    """
    pyBrNews ES Database Class to use ElasticSearch database to store all article and comment data from the platforms.

    By default, uses the standard ElasticSearch host and port (localhost:5601). Can be changed with set_connection,
    with the parameters host and port or while instancing the PyBrNewsES object. Do not forget to create the user
    "pybrnews" with the same password. If wanted, another auth credentials can be passed as a class parameter.
    """
    def __init__(
            self,
            data_kind: str = "news",
            host: str = "localhost",
            port: int = 9200,
            credentials: Tuple[str] = ("pybrnews", "pybrnews")
    ) -> None:
        if "news" not in data_kind and "comments" not in data_kind:
            raise ValueError(
                f"An invalid kind of data for database [ {data_kind} ] was supplied. Review and try again."
            )

        self.db = self.set_connection(host=host, port=port, credentials=credentials)
        self.index = "pybrnews_news" if "news" in data_kind else "pybrnews_comments"

    @staticmethod
    def set_connection(
            host: str = "localhost",
            port: int = 9200,
            credentials: Tuple[str] = ("pybrnews", "pybrnews")
    ) -> OpenSearch:
        """
        Sets the connection host:port parameters for the MongoDB. By default, uses the standard localhost:27017 for
        local usage.

        Parameters:
             host (str): Hostname or address to connect.
             port (int): Port to be used in the connection.
             credentials (Tuple[str]): Credentials for auth on ElasticSearch backend.
        """
        host_data = [{"host": host, "port": port}]

        database = OpenSearch(
            hosts=host_data, http_compress=True, http_auth=credentials,
            use_ssl=True, verify_certs=False, ssl_assert_hostname=False, ssl_show_warn=False
        )

        return database

    def insert_data(self, parsed_data: dict) -> dict:
        """
        Inserts the parsed data from a news article or extracted comment into the DB Backend (MongoDB - pyMongo).

        Parameters:
            parsed_data (dict): Dictionary containing the parsed data from a news article or comment.
        Returns:
            dict: Shows a success message and the insertion result if successfull. If not, shows an error message.
        """
        parsed_data["entry_dt"] = datetime.now()

        try:
            inserted_data = self.db.index(index=self.index, body=parsed_data, refresh=True)
            logger.success(
                f"Data inserted into pyBrNews DB! Document ID {inserted_data['_id']} "
                f"successfully added to the ES Backend into index \"{self.index}\"."
            )
            logger.debug(f"Inserted ES Backend data result: {inserted_data}")
        except Exception as e:
            logger.error(f"An error happened while attempting to insert the given data to the pyBrNews database.")
            logger.debug(f"Data URL: {parsed_data['url']}")
            logger.debug(f"{traceback.print_exception(e)}")

    def read_data(
            self,
            origin: Optional[List[str]] = None,
            search_query: Optional[str] = None,
            init_final_year: Optional[Tuple[int]] = None,
            limit: int = 10
    ) -> Iterable[dict]:
        if origin is None and search_query is None and init_final_year is None:
            query = None
        else:
            query = self._query_constructor(args=[origin, search_query, init_final_year])

        query_response = self.db.search(
            index=self.index, size=limit
        ) if query is None else self.db.search(index=self.index, body=query, size=limit)

        for data in query_response["hits"]["hits"]:
            yield data

    def update_data(self, payload: dict, doc_id: str) -> dict:
        updated_data = self.db.update(id=doc_id, body={"doc": payload}, index=self.index)
        return updated_data

    def delete_data(self, doc_id: str, make_backup: bool = False) -> dict:
        backup_data = None
        if make_backup:
            backup_data = self.db.get(index=self.index, id=doc_id)

        removed_data = self.db.delete(index=self.index, id=doc_id)
        if backup_data is not None:
            self.db.index(index=f"{self.index}_bkp", body=backup_data, refresh=True)

        return removed_data

    def check_duplicates(self, parsed_data: dict) -> bool:
        """
        Checks if the parsed data is already in the database and prevents from being duplicated
        in the crawler execution.

        Parameters:
            parsed_data (dict): Dictionary containing the parsed data from a news article or comment.
        Returns:
            bool: True if the given parsed data is already in the database. False if not.
        """

        check_query = {
            "query": {
                "bool": {
                    "must": [
                        {"match": {"url.keyword": parsed_data["url"]}},
                        {"match": {"date": parsed_data["date"]}}
                    ]
                }
            }
        }

        doc_count = self.db.count(index=self.index, body=check_query)
        if doc_count["count"] < 1:
            return False

        return True

    @staticmethod
    def _query_constructor(args: Optional[List[Union[List[str], Tuple[int], str]]] = None) -> Optional[dict]:
        query = {
            "query": {
                "query_string": {},
                "range": {},
                "must": []
            }
        }
        if args is None:
            return None

        for arg in args:
            if type(arg) is str:
                sharded_search = arg.split(" ")
                fields = ["title", "abstract", "body", "search_keyword"]
                _filter = "or" if "and" not in sharded_search else "and"
                del sharded_search[sharded_search.index(_filter)]

                search_query = f" {_filter.upper()} ".join(sharded_search)
                query["query"]["query_string"]["query"] = search_query
                query["query"]["query_string"]["fields"] = fields
            elif type(arg) is tuple:
                query["query"]["range"].update({
                    "gte": datetime(year=int(arg[0]), month=1, day=1),
                    "lte": datetime(year=int(arg[1]), month=12, day=31)
                })

            elif type(arg) is list:
                query["query"]["must"].append({"match": {"platform.keyword": plat}} for plat in arg)
            else:
                logger.warning("Passed parameters does not match any of the accepted ones. Using default query option.")

        return query


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
        file_name = f"ParsedNewsData_{export_time}.json"
        try:
            with open(f"{self.save_path}{file_name}", mode="w", encoding="utf-8") as json_file:
                json.dump(parsed_data, json_file, ensure_ascii=False, indent=4)

            logger.success(
                f"Data saved successfully as a JSON file! Document path: {self.save_path}{file_name}"
            )
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

            logger.success(
                f"All data exported successfully as a CSV file! Document path: {self.save_path}{file_name}"
            )
        except OSError:
            logger.error(
                "An error occurred while attempting to save the CSV file. Review the save path and the data, and try "
                "again."
            )


class PyBrNewsDBMigration:
    def __init__(
            self,
            src_db_backend: Union[PyBrNewsDB, PyBrNewsES],
            dest_db_backend: Union[PyBrNewsDB, PyBrNewsES],
            maintain_src_data: bool = True
    ) -> None:
        self.src_db = src_db_backend
        self.dest_db = dest_db_backend
        self.maintain_source_data = maintain_src_data

    def migrate_data(self) -> None:
        if type(self.src_db) is PyBrNewsDB:
            self._mongo_to_elastic()
        else:
            self._elastic_to_mongo()

    def _mongo_to_elastic(self) -> None:
        for data in self.src_db.collection.find({}).limit(0):
            doc_id = str(data["_id"])
            try:
                if self.dest_db.check_duplicates(parsed_data=data):
                    logger.warning(
                        f"pyBrNews | MongoDB DocID {doc_id} already into ElasticSeach index!")
                    continue
            except opensearchpy.exceptions.RequestError:
                logger.error(
                    f"pyBrNews | ElasticSearch error while trying to check for duplicates of MongoDB DocID {doc_id} on"
                    f" ES Backend. Ignoring and going to the next one."
                )

            del data["_id"]
            self.dest_db.insert_data(parsed_data=data)

            if not self.maintain_source_data:
                self.src_db.delete_data(doc_id=doc_id)

    def _elastic_to_mongo(self) -> None:
        src_total_size = self.src_db.db.count(index=self.src_db.index)["count"]
        for data in self.src_db.db.search(index=self.src_db.index, size=src_total_size)["hits"]["hits"]:
            doc_id = str(data["_id"])
            if self.dest_db.check_duplicates(parsed_data=data["_source"]):
                logger.warning("Data already into MongoDB collection! Proceeding to next doc.")
                continue

            del data["_id"]
            self.dest_db.insert_data(parsed_data=data["_source"])

            if not self.maintain_source_data:
                self.src_db.delete_data(doc_id=doc_id)
