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
        csv_file_path = self.dir / f"{datetime.datetime.now()}.csv"
        self.writer = csv.DictWriter(csv_file_path, fieldnames=self.fields)
        self.writer.writeheader()

    @staticmethod
    def response_to_csv_line(response_dict: dict):
        data = list(response_dict.values())
        data["uuid"] = response_dict.keys[0]
        return data
    
    def _log_response_entry(self, response_entry: dict):
        response_entry["uuid"] = response_entry.keys[0]
        self.writer.writerow(response_entry)

    def log_response(self, response: dict):
        csv_file_path = self.dir / f"{datetime.datetime.now()}.csv"
        with open(csv_file_path, mode='w', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=self.fields)
            writer.writeheader()

            for uuid, response_entry in response.items():
                response_entry["uuid"] = uuid
                writer.writerow(response_entry)
            
