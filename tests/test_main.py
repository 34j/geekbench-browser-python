# ruff: noqa: PLC2701, PT009

from unittest import TestCase
from unittest.mock import MagicMock, patch


from geekbench_browser._main import get_data


class TestMain(TestCase):
    def test_get_data(self):
        get_data()
