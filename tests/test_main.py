# ruff: noqa: PLC2701, PT009

import os
from unittest import TestCase, skipIf

from geekbench_browser._main import get_data


@skipIf(os.getenv("CI"), "live Geekbench request is disabled in CI")
class TestMain(TestCase):
    def test_get_data(self):
        get_data()
