import unittest

from unittest.mock import patch, MagicMock

from main import OUIList, OUIRemoteSrc, OUIJsonStorage, OctetsSet, MACAddress


class TestOUIList(unittest.TestCase):

    @patch('main.OUIRemoteSrc')
    @patch('main.OUIJsonStorage')
    def test_preloading_empty_oui_list_from_empty_src(self, mock_storage: MagicMock, mock_src: MagicMock) -> None:
        mock_src.fetch.return_value = {'FFFFFF': 'Broadcast'}
        mock_storage.load.return_value = {}
        oui_list = OUIList(mock_src, mock_storage)

        self.assertDictEqual(oui_list.data, {})
        mock_storage.load.assert_called_once()

    @patch('main.OUIRemoteSrc')
    @patch('main.OUIJsonStorage')
    def test_updating_empty_oui_list_from_src(self, mock_storage: MagicMock, mock_src: MagicMock) -> None:
        mock_src.fetch.return_value = {'FFFFFF': 'Broadcast'}
        mock_storage.load.return_value = {}
        oui_list = OUIList(mock_src, mock_storage)
        oui_list.update()

        self.assertDictEqual(oui_list.data, {'FFFFFF': 'Broadcast'})
        mock_storage.dump.assert_called_once_with({'FFFFFF': 'Broadcast'})
        mock_storage.load.assert_called_once()


class TestOUIJsonStorage(unittest.TestCase):

    @patch('main.open')
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

    @patch('main.urllib.request')
    def test_parsing_oui_src(self, mock_request: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.read.return_value = self.CSV.strip()
        mock_request.urlopen.return_value.__enter__.return_value = mock_response
        self.assertDictEqual(OUIRemoteSrc().fetch(), {
            '002272': 'American Micro-Fuel Device Corp.',
            '00D0EF': 'IGT'
        })


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
