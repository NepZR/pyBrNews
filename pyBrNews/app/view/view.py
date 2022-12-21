import PySimpleGUI

from typing import List, Any
from pyBrNews.app.controller.view_controller import ViewController


class PyBrNewsView(ViewController):
    def __init__(self) -> None:
        super().__init__()
        self.ui_handler = PySimpleGUI
        self.layout = self._user_layout()
        self.user_interface = PySimpleGUI.Window(
            'PyBrNews',
            self.layout,
            resizable=True,
            element_justification="center",
            default_element_size=(400, 480),
            grab_anywhere=False,
            size=(800, 750)
        )

    def _user_layout(self) -> List[Any]:
        self.ui_handler.theme('Reddit')

        actions_tab = [
            [self.ui_handler.Column(
                key="-NEWS-ACTIONS-", expand_x=True,
                layout=[
                    [self.ui_handler.Text('Search Keyword: ', font=("Segoi UI", 11, "bold")),
                     self.ui_handler.InputText('', key='search_keyword', expand_x=True)],
                    [
                        self.ui_handler.Text('Search Platforms', font=("Segoi UI", 11, "bold"), expand_x=True),
                        self.ui_handler.Checkbox('Portal G1', key='news_platform_g1'),
                        self.ui_handler.Checkbox('Folha de São Paulo', key='news_platform_folhasp'),
                        self.ui_handler.Checkbox('Exame', key='news_platform_exame')
                    ],
                    [self.ui_handler.Col(
                        [[self.ui_handler.Button(
                            'Get news from pyBrNews', key="get_news", enable_events=True
                        )]], pad=(0, 10), justification="right"
                    )],

                    [self.ui_handler.HorizontalSeparator(color="black", pad=(0, 0))],
                    [self.ui_handler.Text(
                        f'Result Output (limited to 30)', font=("Segoi UI", 16, "bold"),
                        border_width=1, pad=(5, 5), key="-DOUT_TEXT"
                    )],
                    [self.ui_handler.Table(
                        values=[], headings=["Title", "Platform"], key="-OUTPUT_DATA-", justification="left",
                        col_widths=[60, 20], expand_x=True, expand_y=True, auto_size_columns=False, num_rows=20
                    )]
                ]
            )]
        ]

        search_tab = [
            [self.ui_handler.Column(
                key="-SEARCH-ACTIONS-", expand_x=True,
                layout=[
                    [self.ui_handler.Text('Search Query: ', font=("Segoi UI", 11, "bold")),
                     self.ui_handler.InputText('', key='search_query_text'),
                     ],
                    [self.ui_handler.Checkbox(
                        'Use \"AND\" Query', font=("Segoi UI", 11, "bold"), key="search_all_terms", expand_x=True
                    ), self.ui_handler.Text('Query Limit', font=("Segoi UI", 11, "bold")),
                    ],
                    [
                        self.ui_handler.Text('Search Platforms', font=("Segoi UI", 11, "bold"), expand_x=True),
                        self.ui_handler.Text(expand_x=True),
                        self.ui_handler.Combo(
                            [i for i in range(0, 1100, 100)], key="search_query_limit"
                        )
                    ],
                    [
                        self.ui_handler.Checkbox('Portal G1', key='search_query_platform_g1'),
                        self.ui_handler.Checkbox('Folha de São Paulo', key='search_query_platform_folhasp'),
                        self.ui_handler.Checkbox('Exame', key='search_query_platform_exame'),
                    ],
                    [self.ui_handler.Col(
                        [[
                            self.ui_handler.Text(
                                "Please, set the start date.", key="-QUERY_INIT_DT-"
                            ),
                            self.ui_handler.CalendarButton(
                                "Set Start Date", key="search_query_init_date",
                                format="%Y-%m-%d",
                            ),
                            self.ui_handler.VerticalSeparator(color="black", pad=(5, 0)),
                            self.ui_handler.Text("Please, set the final date.", key="-QUERY_END_DT-"),
                            self.ui_handler.CalendarButton(
                                "Set Final Date", key="search_query_final_date",
                                format="%Y-%m-%d"
                            ),
                            self.ui_handler.VerticalSeparator(color="black", pad=(5, 0)),
                        ]], justification="left"),
                        self.ui_handler.Col(
                            [[self.ui_handler.Button(
                                'Run Query', key="run_search_query", enable_events=True
                            )]], pad=(0, 10), justification="right"
                    )],

                    [self.ui_handler.HorizontalSeparator(color="black", pad=(0, 0))],
                    [self.ui_handler.Text(
                        f'Search Result', font=("Segoi UI", 16, "bold"),
                        border_width=1, pad=(5, 5), key="-DOUT_SEARCH"
                    )],
                    [self.ui_handler.Table(
                        values=[], headings=["Title", "Platform", "ID"], key="-RESULT_DATA-", justification="left",
                        col_widths=[60, 20, 10], expand_x=True, expand_y=True, auto_size_columns=False, num_rows=15,
                        enable_click_events=False
                    )],
                    [self.ui_handler.Button(
                        'Inspect selected item', key="inspect_selected_data", enable_events=True, button_color="gray",
                        mouseover_colors=("darkgray", "white"), expand_x=True
                    )]
                ]
            )]
        ]

        inspect_tab = [
            [
                # self.ui_handler.Table(
                #     values=entity_data, headings=["Name", "ID", "Category"],
                #     col_widths=list(map(lambda x: len(x) + 10, ["Name", "ID", ""])),
                #     expand_x=True, expand_y=True, auto_size_columns=False, num_rows=25
                # )
            ]
        ]

        layout = [
            [self.ui_handler.HorizontalSeparator(color="black", pad=(0, 10))],
            [self.ui_handler.Text(
                'pyBrNews', font=("Segoi UI", 22), expand_x=True, pad=(0, 5), justification="center"
            )],
            [self.ui_handler.Text(
                'A Brazilian News Website Data Acquisition Library for Python',
                font=("Segoi UI", 14, "italic"), expand_x=True, pad=(0, 5), justification="center"
            )],
            [self.ui_handler.HorizontalSeparator(color="black", pad=(0, 10))],
            [self.ui_handler.TabGroup([[
                self.ui_handler.Tab('Parse News', actions_tab),
                self.ui_handler.Tab('Search Data', search_tab),
                self.ui_handler.Tab('Inspection Tool', inspect_tab),
            ]])
            ],
            [self.ui_handler.Text(
               self.retrieve_db_backend_info(), expand_x=True, justification="left",
               font=("Segoi UI", 12, "bold"), key="-DB_BACKEND_INFO-", pad=(0, 15)
            ), self.ui_handler.Button(
                button_text=self.retrieve_db_switch_str(), key="db_backend_set", enable_events=True
            )
            ],
            [self.ui_handler.HorizontalSeparator(color="black", pad=(0, 10))],
            [self.ui_handler.Text(
                "© 2022 Lucas Rodrigues\nBuild v0.2.0-alpha1 (Branch: college/app-project)",
                font=("Segoi UI", 11), expand_x=True, justification="center"
            )],
            [self.ui_handler.Text(
                "pyBrNews Project, made with ❤️ by Lucas Rodrigues (@NepZR)",
                font=("Segoi UI", 9, "bold"), expand_x=True, justification="center"
            )],
            [self.ui_handler.HorizontalSeparator(color="black", pad=(0, 10))],
            [self.ui_handler.Button(
                "Exit", button_color='red', pad=(4, 10), expand_x=True, mouseover_colors=("white", "darkred")
            )],
        ]

        return layout


if __name__ == "__main__":
    ui_layout = PyBrNewsView().user_interface()

