import os

import pytest

from geekbench_browser._main import get_data  # ruff: ignore[import-private-name]


@pytest.mark.skipif(bool(os.getenv("CI")), reason="live Geekbench request is disabled in CI")
def test_get_data():
    get_data()
