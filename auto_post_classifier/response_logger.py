import csv
import pathlib
import datetime
from pathlib import Path

class ResponseLogger:
    
    def __init__(self, dir: Path, fields : list) -> None:
        self.dir = dir
        self.fields = fields

    def set_path(self, path: pathlib.Path):
        self.path = path
    
    def start_new_file(self):
        csv_file = datetime.datetime.now()
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    @staticmethod
    def response_to_csv_line(response_dict: dict):
        data = list(response_dict.values())
        data["uuid"] = response_dict.keys[0]
        return data
        



    def log_response(self, response: list[dict]):
        
        with open(self.path, 'a') as f:
            writer = csv.writer(f)
            writer.writerow(data)

csv_logger = ResponseLogger()