import csv
import json
from abc import ABC, abstractmethod
from datetime import datetime


class Crawler(ABC):
    @abstractmethod
    def retrieve_news(self, max_pages: int, region_lock: bool = False, regions: list = None):
        pass

    @abstractmethod
    def parse_news(self, news_urls: list, parse_content: bool = False):
        pass

    @abstractmethod
    def search_news(self, keywords: list, max_pages: int):
        pass

    @abstractmethod
    def parse_url(self, url: str):
        pass

    @staticmethod
    def export_data(parsed_data: list, export_type: str = 'csv'):
        export_time = datetime.today().strftime('%Y_%m_%d_%HH_%MM')
        if len(parsed_data) == 0:
            raise ValueError(f'parsed_data ({export_type}) cannot be empty.')
        if ('csv' not in export_type.lower()) and ('json' not in export_type.lower()):
            raise ValueError(f'{export_type} is not a valid export format.')
        with open(f'ParsedNewsData_{export_time}.{export_type}', 'w', encoding='utf-8') as export_file:
            if export_type.lower() == 'csv':
                header = ['title', 'abstract', 'date', 'section', 'region', 'url', 'platform', 'content']
                writer = csv.DictWriter(export_file, fieldnames=header)
                writer.writeheader()
                writer.writerows(parsed_data)
            else:
                json.dump(parsed_data, export_file, ensure_ascii=False, indent=4)
