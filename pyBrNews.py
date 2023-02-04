from datetime import datetime

from typing import Optional, Tuple, List
from pyBrNews.app.view.view import PyBrNewsView
from pyBrNews.config.database import PyBrNewsDB


class PyBrNews(PyBrNewsView):
    def __init__(self) -> None:
        super().__init__()

    def run(self) -> None:
        query_data: Optional[list] = None
        doc_info: Optional[Tuple[str, str, str]] = None
        inspect_data: Optional[dict] = None
        fields: Optional[List[str]] = None

        self.ui_handler.set_options(suppress_error_popups=True, suppress_raise_key_errors=False)

        while True:
            event, data = self.user_interface.read()

            if event is self.ui_handler.WIN_CLOSED or "Exit" in event:
                self.user_interface.close()
                break
            elif "get_news" in event:
                retrieved_data = self.search_and_insert_news(search_params=data)
                self.user_interface["-OUTPUT_DATA-"].update(retrieved_data)
            elif "db_backend_set" in event:
                self.switch_db_backend()
                self.user_interface["-DB_BACKEND_INFO-"].update(self.retrieve_db_backend_info())
                self.user_interface["db_backend_set"].update(self.retrieve_db_switch_str())
            elif "run_search_query" in event:
                data["search_query_init_date"] = self.user_interface["-QUERY_INIT_DT-"].get()
                data["search_query_final_date"] = self.user_interface["-QUERY_END_DT-"].get()
                query_data = self.search_data(query_params=data)
                self.user_interface["-RESULT_DATA-"].update(query_data)
            elif "inspect_selected_data" in event and len(data['-RESULT_DATA-']) > 0:
                doc_info = query_data[data['-RESULT_DATA-'][0]]
                try:
                    inspect_data, fields = self.db_controller.retrieve_doc_data(document_id=doc_info[2])
                    for field in fields:
                        self.user_interface[f"doc_data_inspect_{field}"].update(inspect_data[field])
                except KeyError:
                    self.user_interface.extend_layout(
                        self.user_interface["-INSPECTION_FIELDS-"],
                        self.get_inspection_tool_fields(document_id=doc_info[2])
                    )
                self.user_interface["Inspection Tool (No Data)"].update(f"Inspection Tool - DocID {doc_info[2]}")

            elif "trigger_delete_document" in event and doc_info is not None:
                self.trigger_document_deletion(doc_info=doc_info, make_backup=True, user_interface=self.user_interface)
                inspect_data, doc_info = None, None

            elif "trigger_export_document" in event and doc_info is not None:
                save_path = f"{data['export_document_path']}/"
                self.trigger_export_document(doc_id=doc_info[2], export_path=save_path)

            elif "trigger_save_edit_document" in event and doc_info is not None and fields is not None:
                doc_id = doc_info[2]
                updated_data = {}

                for field in fields:
                    if "date" in field or "entry_dt" in field:
                        date_pattern = "%Y-%m-%d %H:%M:%S.%f" if type(
                            self.db_controller.database) is PyBrNewsDB else "%Y-%m-%dT%H:%M:%S.%f"
                        updated_data[field] = datetime.strptime(
                            str(self.user_interface[f"doc_data_inspect_{field}"].get()), date_pattern
                        )
                    else:
                        updated_data[field] = str(self.user_interface[f"doc_data_inspect_{field}"].get())

                self.db_controller.database.update_data(payload=updated_data, doc_id=doc_id)

            elif "trigger_import_document" in event and len(data["import_document_path"]) > 0:
                self.trigger_import_document(import_path=data["import_document_path"])


if __name__ == '__main__':
    app = PyBrNews()
    app.run()
