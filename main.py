import re
import csv
import json
import urllib.request

from typing import Dict, List


class OctetsSet:

    def __init__(self, octets: str) -> None:
        self._original_value = octets
        self._octets = self._parse_octets()
        self._validate()

    def _parse_octets(self) -> List[str]:
        return re.split(r'[:-]', self._original_value)

    def _validate(self) -> None:
        for octet in self._octets:
            if len(octet) != 2:
                raise ValueError('Invalid hexadecimal representation of octet')
            try:
                int(octet, base=16)
            except ValueError:
                raise ValueError('Invalid octet')

    def __str__(self) -> str:
        return ':'.join(self._octets).upper()


class MACAddress(OctetsSet):

    def __init__(self, octets: str) -> None:
        super().__init__(octets)
        self.oui = OctetsSet(':'.join(self._octets[:3]))
        self.vendor_specific = OctetsSet(':'.join(self._octets[-3:]))

    def _validate(self) -> None:
        if len(self._octets) != 6:
            raise ValueError('Too few octets')


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


if __name__ == '__main__':
    pass
