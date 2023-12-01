import csv
import datetime
from pathlib import Path


class ResponsePersister:
    def __init__(self, dir: Path, fields: list) -> None:
        self.dir = dir
        self.fields = fields

    def _create_response_dir(self):
        if not self.dir.exists():
            self.dir.mkdir(parents=True)

    def persist_response(self, response: dict):
        self._create_response_dir()
        csv_file_path = self.dir / f"{datetime.datetime.now()}.csv"
        with open(csv_file_path, mode="w", newline="") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=self.fields)
            writer.writeheader()

            for uuid, response_entry in response.items():
                response_entry["uuid"] = uuid
                writer.writerow(response_entry)
