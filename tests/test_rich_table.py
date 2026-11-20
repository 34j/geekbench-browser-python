import pandas as pd
from rich.console import Console
from rich.table import Table

from geekbench_browser._rich_table import _bar, df_to_table


def test_bar():
    assert _bar(10, 10, 4) == "━━━━"
    assert _bar(5, 10, 4) == "━━  "
    assert _bar(1, 4, 2) == "╸ "
    assert _bar(float("nan"), 10, 3) == "   "
    assert _bar(5, 0, 3) == "   "


def test_df_to_table_bars():
    df = pd.DataFrame(
        {"description": ["a", "b"], "single": [1000, 500], "multi": [8000, 2000]},
        index=["A", "B"],
    )
    console = Console(width=120, record=True, color_system=None)
    console.print(df_to_table(df, Table(), bar_columns=("single", "multi"), bar_width=8))
    lines = console.export_text().splitlines()
    assert any("1000 ━━━━━━━━" in line and "8000 ━━━━━━━━" in line for line in lines)
    assert any(" 500 ━━━━    " in line and "2000 ━━      " in line for line in lines)


def test_df_to_table_no_bars():
    df = pd.DataFrame({"single": [1000]}, index=["A"])
    console = Console(width=80, record=True, color_system=None)
    console.print(df_to_table(df, Table()))
    assert "1000 ━" not in console.export_text()
