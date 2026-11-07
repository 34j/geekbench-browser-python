# ruff: noqa: PLC2701, PT009

from unittest import TestCase
from unittest.mock import MagicMock, patch

from pandas import DataFrame

from geekbench_browser._main import get_data


class TestMain(TestCase):
    def test_get_data(self):
        response = MagicMock(created_at=None, expires=None)
        response.json.return_value = {
            "devices": [
                {
                    "name": "Test CPU",
                    "description": "3.0 GHz (4 cores)",
                    "score": 1,
                    "multicore_score": 2,
                },
            ],
        }
        with patch("geekbench_browser._main.CachedSession") as session_class:
            session_class.return_value.__enter__.return_value.get.return_value = response
            data = get_data()

        self.assertIsInstance(data, DataFrame)
