import os

import pytest

from geekbench_browser._main import get_data  # noqa: PLC2701


@pytest.mark.skipif(bool(os.getenv("CI")), reason="live Geekbench request is disabled in CI")
def test_get_data():
    get_data()
