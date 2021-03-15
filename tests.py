import os
import glob
import unittest

from main import OUIList


class TestOUIList(unittest.TestCase):
    TEST_STORAGE_FILENAME = 'test_oui_{postfix}.json'

    def test_preloading_empty_oui_list(self) -> None:
        oui_list = OUIList(self.TEST_STORAGE_FILENAME.format(postfix='preloading'))
        self.assertDictEqual(oui_list.data, {})

    def test_fetching_oui_list_from_ieee(self) -> None:
        oui_list = OUIList(self.TEST_STORAGE_FILENAME.format(postfix='fetching'))
        oui_list.fetch_from_ieee()
        self.assertNotEqual(len(oui_list.data), 0)

    def tearDown(self) -> None:
        for filename in glob.glob(self.TEST_STORAGE_FILENAME.format(postfix='*')):
            os.unlink(filename)
