# ruff: file-ignore[boolean-type-hint-positional-argument, boolean-default-value-positional-argument, pandas-use-of-dot-values]

from collections.abc import Mapping, Sequence

import pandas as pd
from rich.table import Table
from rich.text import Text

# Thin line glyphs rather than full blocks, so bars on adjacent rows stay visually separate.
_FULL = "━"
_HALF = "╸"
_BAR_COLORS = ("cyan", "magenta", "green", "yellow")


def _bar(value: float, maximum: float, width: int) -> str:
    """Render a horizontal bar of ``width`` cells, to half-cell precision."""
    if not maximum > 0 or not value > 0:
        return " " * width
    halves = round(min(value / maximum, 1.0) * width * 2)
    full, rest = divmod(halves, 2)
    bar = _FULL * full + (_HALF if rest else "")
    return bar.ljust(width)


def df_to_table(
    pandas_dataframe: pd.DataFrame,
    rich_table: Table,
    show_index: bool = True,
    index_name: str | None = None,
    bar_columns: Sequence[str] = (),
    bar_width: int = 20,
    bar_maximums: Mapping[str, float] | None = None,
) -> Table:
    """Convert a pandas.DataFrame obj into a rich.Table obj.

    Args:
        pandas_dataframe (DataFrame):
            A Pandas DataFrame to be converted to a rich Table.
        rich_table (Table):
            A rich Table that should be populated by the DataFrame values.
        show_index (bool):
            Add a column with a row count to the table. Defaults to True.
        index_name (str, optional):
            The column name to give to the index column.
            Defaults to None, showing no value.
        bar_columns (Sequence[str]):
            Numeric columns to draw as horizontal bar graphs next to the value,
            each scaled to the largest value shown in that column.
        bar_width (int):
            Width of each bar in terminal cells. Defaults to 20.
        bar_maximums (Mapping[str, float], optional):
            Value that a full-width bar represents, per column. Lets several
            tables share one scale. Defaults to the largest value in the column.

    Returns:
        Table:
            The rich Table instance passed, populated with the DataFrame values.

    """
    if show_index:
        index_name = str(index_name) if index_name else ""
        rich_table.add_column(index_name)
        rich_indexes = pandas_dataframe.index.to_list()

    for column in pandas_dataframe.columns:
        # a wrapped bar is unreadable, so bar columns keep their width
        rich_table.add_column(str(column), no_wrap=column in bar_columns)

    columns = list(pandas_dataframe.columns)
    bars = {}
    for color_index, column in enumerate(c for c in bar_columns if c in columns):
        numeric = pd.to_numeric(pandas_dataframe[column], errors="coerce")
        maximum = (bar_maximums or {}).get(column, numeric.max())
        digits = int(numeric.map(lambda x: len(str(x))).max()) if len(numeric) else 0
        bars[column] = (maximum, digits, _BAR_COLORS[color_index % len(_BAR_COLORS)])

    for index, value_list in enumerate(pandas_dataframe.values.tolist()):
        row: list[str | Text] = [str(rich_indexes[index])] if show_index else []
        for column, value in zip(columns, value_list, strict=True):
            if column not in bars:
                row.append(str(value))
                continue
            maximum, digits, color = bars[column]
            number = pd.to_numeric(value, errors="coerce")
            cell = Text(str(value).rjust(digits) + " ")
            cell.append(_bar(number, maximum, bar_width), style=color)
            row.append(cell)
        rich_table.add_row(*row)

    return rich_table
