from unittest import TestCase

from pandas import DataFrame

from geekbench_browser._main import get_data


class TestMain(TestCase):
    def test_get_data(self):
        data = get_data()
        self.assertIsInstance(data, DataFrame)
