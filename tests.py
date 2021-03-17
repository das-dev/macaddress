import os
import glob
import unittest

from unittest.mock import patch

from main import OUIList, OUIRemoteSrc, OUIJsonStorage, OctetsSet, MACAddress


class TestOUIList(unittest.TestCase):
    TEST_STORAGE_FILENAME = 'test_oui_{postfix}.json'

    def test_preloading_empty_oui_list(self) -> None:
        with patch.object(OUIRemoteSrc, 'fetch', return_value={'FFFFFF': 'Broadcast'}):
            src = OUIRemoteSrc()
            storage = OUIJsonStorage(self.TEST_STORAGE_FILENAME.format(postfix='preloading'))
            oui_list = OUIList(src, storage)
            self.assertDictEqual(oui_list.data, {})
            self.assertEqual(len(oui_list.data), 0)

    def test_fetching_oui_list_from_ieee(self) -> None:
        with patch.object(OUIRemoteSrc, 'fetch', return_value={'FFFFFF': 'Broadcast'}):
            src = OUIRemoteSrc()
            storage = OUIJsonStorage(self.TEST_STORAGE_FILENAME.format(postfix='fetching'))
            oui_list = OUIList(src, storage)
            oui_list.update()
            self.assertDictEqual(oui_list.data, {'FFFFFF': 'Broadcast'})
            self.assertNotEqual(len(oui_list.data), 0)

    def tearDown(self) -> None:
        for filename in glob.glob(self.TEST_STORAGE_FILENAME.format(postfix='*')):
            os.unlink(filename)


class TestMACAddress(unittest.TestCase):

    def test_invalid_octets_set(self) -> None:
        with self.assertRaises(ValueError):
            OctetsSet(':FF:FF:FF')
        with self.assertRaises(ValueError):
            OctetsSet('FF:FF:FF:')
        with self.assertRaises(ValueError):
            OctetsSet('FF.FF.FF')
        with self.assertRaises(ValueError):
            OctetsSet('FF:FF:XY')
        with self.assertRaises(ValueError):
            OctetsSet('FF:FF:F')

    def test_valid_octets_set(self) -> None:
        self.assertEqual(str(OctetsSet('FF:FF:FF')), 'FF:FF:FF')
        self.assertEqual(str(OctetsSet('ff:ff:ff')), 'FF:FF:FF')

    def test_invalid_mac_address(self) -> None:
        with self.assertRaises(ValueError):
            MACAddress('FF:FF:FF')

    def test_valid_mac_address(self) -> None:
        self.assertEqual(str(MACAddress('FF:FF:FF:FF:FF:FF')), 'FF:FF:FF:FF:FF:FF')
