from __future__ import annotations

import re
import csv
import sys
import json
import urllib.request

from typing import Dict, List, Optional


class OctetsSet:

    def __init__(self, octets: str) -> None:
        self._original_value = octets
        self._octets = self._parse_octets()
        self._validate()

    def _parse_octets(self) -> List[str]:
        return re.findall(r'\w{1,2}', self._original_value)

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


class OUIJsonStorage:

    def __init__(self, filename: str = 'oui.json'):
        self.filename = filename

    def dump(self, data) -> None:
        with open(self.filename, 'w') as file:
            json.dump(data, file)

    def load(self) -> Dict[str, str]:
        try:
            with open(self.filename) as json_file:
                return json.load(json_file)
        except FileNotFoundError:
            return {}


class OUIRemoteSrc:
    URL = 'http://standards-oui.ieee.org/oui/oui.csv'

    def fetch(self) -> Dict[str, str]:
        with urllib.request.urlopen(self.URL) as response:
            content = response.read().decode()
            reader = csv.reader(content.splitlines())
            next(reader)  # skip headers
            return {oui: vendor for _, oui, vendor, _ in reader}


class OUIList:
    def __init__(self, src: OUIRemoteSrc = OUIRemoteSrc(), storage: OUIJsonStorage = OUIJsonStorage()):
        self.src = src
        self.storage = storage
        self.data: Dict[str, str] = self.storage.load()

    def update(self) -> None:
        self.data = self._normalize(self.src.fetch())
        self.storage.dump(self.data)

    def _normalize(self, data: Dict[str, str]) -> Dict[str, str]:
        return {str(OctetsSet(octets)): vendor for octets, vendor in data.items()}

    def lookup_by_oui(self, octets: str) -> Optional[str]:
        return self.data.get(str(OctetsSet(octets)))

    def lookup_by_mac(self, octets: str) -> Optional[str]:
        return self.data.get(str(MACAddress(octets).oui))


def cli():
    try:
        param, value = sys.argv[1:]
    except ValueError:
        return
    if param != 'lookup-mac':
        return
    if vendor := OUIList().lookup_by_mac(value):
        sys.stdout.write(f'{vendor}\n')
    else:
        sys.stdout.write('Sorry, vendor not found\n')


if __name__ == '__main__':
    cli()


