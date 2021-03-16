import re
import csv
import json
import urllib.request

from typing import Dict


class OUIList:
    IEEE_SRC = 'http://standards-oui.ieee.org/oui/oui.csv'

    def __init__(self, storage_filename: str = 'oui.json'):
        self.storage_filename = storage_filename
        self.data: Dict[str, str] = {}
        self.load()

    def fetch_from_ieee(self) -> None:
        with urllib.request.urlopen(self.IEEE_SRC) as response:
            content = response.read().decode()
            reader = csv.reader(content.splitlines())
            next(reader)  # skip headers
            self.data = {oui: vendor for _, oui, vendor, _ in reader}
        self.dump()

    def dump(self) -> None:
        with open(self.storage_filename, 'w') as file:
            json.dump(self.data, file)

    def load(self) -> None:
        try:
            self.data = self._load()
        except FileNotFoundError:
            self.data = {}

    def _load(self) -> Dict[str, str]:
        with open(self.storage_filename) as json_file:
            return json.load(json_file)


def validate_mac_address(mac_address: str) -> bool:
    octets = re.split(r'[:-]', mac_address)
    if len(octets) != 6:
        return False
    for octet in octets:
        if len(octet) != 2:
            return False
        try:
            int(octet, base=16)
        except ValueError:
            return False
    return True


if __name__ == '__main__':
    pass
