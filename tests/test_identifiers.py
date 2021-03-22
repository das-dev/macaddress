import unittest

from unittest.mock import patch, MagicMock

from macaddress.identifiers import OUIList, OUIRemoteSrc, OUIJsonStorage, OctetsSet, MACAddress

TEST_OUI_LIST = {
    '002272': 'American Micro-Fuel Device Corp.',
    '00D0EF': 'IGT'
}
TEST_NORMALIZED_OUI_LIST = {
    '00:22:72': 'American Micro-Fuel Device Corp.',
    '00:D0:EF': 'IGT'
}


class TestOUIList(unittest.TestCase):

    @patch('macaddress.identifiers.OUIRemoteSrc')
    @patch('macaddress.identifiers.OUIJsonStorage')
    def test_preloading_empty_oui_list_from_empty_src(self, mock_storage: MagicMock, mock_src: MagicMock) -> None:
        mock_src.fetch.return_value = TEST_OUI_LIST
        mock_storage.load.return_value = {}
        oui_list = OUIList(mock_src, mock_storage)

        self.assertDictEqual(oui_list.data, {})
        mock_storage.load.assert_called_once()

    @patch('macaddress.identifiers.OUIRemoteSrc')
    @patch('macaddress.identifiers.OUIJsonStorage')
    def test_updated_oui_list_from_src(self, mock_storage: MagicMock, mock_src: MagicMock) -> None:
        mock_src.fetch.return_value = TEST_OUI_LIST
        mock_storage.load.return_value = {}
        oui_list = OUIList(mock_src, mock_storage)
        oui_list.update()

        self.assertDictEqual(oui_list.data, TEST_NORMALIZED_OUI_LIST)

        self.assertEqual(oui_list.lookup_by_oui('00D0EF'), 'IGT')
        self.assertEqual(oui_list.lookup_by_oui('00-D0-EF'), 'IGT')
        self.assertEqual(oui_list.lookup_by_oui('00:D0:EF'), 'IGT')
        self.assertIsNone(oui_list.lookup_by_oui('00:00:00'))

        with self.assertRaises(ValueError):
            oui_list.lookup_by_oui('00:D0:E')
        with self.assertRaises(ValueError):
            oui_list.lookup_by_oui('0:D0:EF')

        self.assertEqual(oui_list.lookup_by_mac('00D0EFFFFFFF'), 'IGT')
        self.assertEqual(oui_list.lookup_by_mac('00-D0-EF-FF-FF-FF'), 'IGT')
        self.assertEqual(oui_list.lookup_by_mac('00D0.EFFF.FFFF'), 'IGT')
        self.assertEqual(oui_list.lookup_by_mac('00:D0:EF:FF:FF:FF'), 'IGT')
        self.assertIsNone(oui_list.lookup_by_mac('00:00:00:00:00:00'))

        with self.assertRaises(ValueError):
            oui_list.lookup_by_mac('00:D0:EF')
        with self.assertRaises(ValueError):
            oui_list.lookup_by_mac('00:D0:EF:FF:FF:FF:F')
        with self.assertRaises(ValueError):
            oui_list.lookup_by_mac('00:D0:EF:FF:FF:FFF')

        mock_storage.dump.assert_called_once_with(TEST_NORMALIZED_OUI_LIST)
        mock_storage.load.assert_called_once()


class TestOUIJsonStorage(unittest.TestCase):

    @patch('macaddress.identifiers.open')
    def test_preloading_empty_oui_list_from_missed_src(self, mock_open: MagicMock) -> None:
        mock_open.side_effect = FileNotFoundError()

        self.assertDictEqual(OUIJsonStorage().load(), {})
        mock_open.assert_called_once()


class TestOUIRemoteSrc(unittest.TestCase):
    CSV = b'''
    Registry,Assignment,Organization Name,Organization Address
    MA-L,002272,American Micro-Fuel Device Corp.,2181 Buchanan Loop Ferndale WA US 98248
    MA-L,00D0EF,IGT,9295 PROTOTYPE DRIVE RENO NV US 89511
    '''

    @patch('macaddress.identifiers.urllib.request')
    def test_parsing_oui_src(self, mock_request: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.read.return_value = self.CSV.strip()
        mock_request.urlopen.return_value.__enter__.return_value = mock_response

        self.assertDictEqual(OUIRemoteSrc().fetch(), TEST_OUI_LIST)


class TestMACAddress(unittest.TestCase):

    def test_invalid_octets_set(self) -> None:
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
        self.assertEqual(str(MACAddress('FFFFFFFFFFFF')), 'FF:FF:FF:FF:FF:FF')
        self.assertEqual(str(MACAddress('FF-FF-FF-FF-FF-FF')), 'FF:FF:FF:FF:FF:FF')
        self.assertEqual(str(MACAddress('FFFF.FFFF.FFFF')), 'FF:FF:FF:FF:FF:FF')
        self.assertEqual(str(MACAddress('FF:FF:FF:FF:FF:FF')), 'FF:FF:FF:FF:FF:FF')
