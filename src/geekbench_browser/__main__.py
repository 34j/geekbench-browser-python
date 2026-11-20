# ruff: file-ignore[undocumented-public-function, boolean-type-hint-positional-argument, literal-membership]

from logging import INFO, basicConfig, getLogger

import click
import rich.console

from ._breakdown import Device
from ._main import get_data
from ._option_eat_all import OptionEatAll

LOG = getLogger(__name__)


# When using OptionEatAll, type must be tuple
@click.help_option("--help", "-h")
@click.command()
@click.argument("names", nargs=-1, type=str)
@click.option("--min-cores", "-mc", type=int, help="Minimum number of cores")
@click.option("--max-cores", "-xc", type=int, help="Maximum number of cores")
@click.option("--min-frequency", "-mf", type=float, help="Minimum frequency in GHz")
@click.option("--max-frequency", "-xf", type=float, help="Maximum frequency in GHz")
@click.option("--min-single", "-ms", type=float, help="Minimum single core score")
@click.option("--max-single", "-xs", type=float, help="Maximum single core score")
@click.option("--min-multi", "-mm", type=float, help="Minimum multi core score")
@click.option("--max-multi", "-xm", type=float, help="Maximum multi core score")
@click.option("--icon", "-i", cls=OptionEatAll, type=tuple, help="Icon to search for")
@click.option("--family", "-f", cls=OptionEatAll, type=tuple, help="Family to search for")
@click.option(
    "--sort",
    "-s",
    type=click.Choice(["name", "single", "multi", "frequency", "cores", "id"]),
    default="name",
    help="Sort by (reverse is default except for name, id)",
)
@click.option("--reverse", "-r", is_flag=True, help="Reverse the sort order")
@click.option("--bars/--no-bars", "-b/-B", default=True, help="Show bar graphs for scores")
@click.option("--bar-width", "-bw", type=click.IntRange(min=1), default=20, help="Bar graph width")
@click.option(
    "--breakdown",
    "-d",
    is_flag=True,
    help="Also graph the individual workload scores of a representative result per CPU",
)
@click.option(
    "--breakdown-limit",
    "-dl",
    type=click.IntRange(min=1),
    default=5,
    help="Maximum number of CPUs to show a breakdown for",
)
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def cli(
    names: list[str],
    min_cores: int,
    max_cores: int,
    min_frequency: float,
    max_frequency: float,
    min_single: float,
    max_single: float,
    min_multi: float,
    max_multi: float,
    icon: list[str],
    family: list[str],
    sort: str,
    reverse: bool,
    bars: bool,
    bar_width: int,
    breakdown: bool,
    breakdown_limit: int,
    verbose: bool,
) -> None:
    if verbose:
        basicConfig(level=INFO)

    # get data
    data = get_data()
    if "current" in names:
        import cpuinfo

        # get current cpu name
        name = cpuinfo.get_cpu_info()["brand_raw"]
        LOG.info("Current CPU: %s", name)

        # geekbench cpuname is shorter than cpuinfo brand_raw
        current_names = data.loc[data["name"].map(lambda x: x in name)]["name"]
        if current_names.empty:
            raise ValueError(f"Could not find current CPU name in database: {name}")

        # remove current from names and add current_names
        names = [n for n in names if n != "current"] + list(current_names)

    # filter data
    if names:
        data = data.loc[data["name"].str.contains("|".join(names), regex=True, case=False)]
    if min_cores:
        data = data.loc[data["cores"] >= min_cores]
    if max_cores:
        data = data.loc[data["cores"] <= max_cores]
    if min_frequency:
        data = data.loc[data["frequency"] >= min_frequency]
    if max_frequency:
        data = data.loc[data["frequency"] <= max_frequency]
    if min_single:
        data = data.loc[data["single"] >= min_single]
    if max_single:
        data = data.loc[data["single"] <= max_single]
    if min_multi:
        data = data.loc[data["multi"] >= min_multi]
    if max_multi:
        data = data.loc[data["multi"] <= max_multi]
    if icon:
        data = data.loc[
            data["icon"].astype(str).str.contains("|".join(icon), regex=True, case=False)
        ]
    if family:
        data = data.loc[
            data["family"].astype(str).str.contains("|".join(family), regex=True, case=False)
        ]

    # sort data
    if sort in ["name", "id"]:
        reverse = not reverse
    data.sort_values(by=sort, inplace=True, ascending=reverse)

    breakdown_devices = [
        (
            int(row.id),
            str(row.name),
            float(row.single),
            float(row.multi),
            None if row.cores != row.cores else int(row.cores),
        )
        for row in data.head(breakdown_limit).itertuples(index=False)
    ]
    breakdown_skipped = max(len(data) - breakdown_limit, 0)

    # drop columns that does not make sense
    if not verbose:
        data = data.drop(columns=["cores", "frequency", "id", "name"])
    data = data.reindex(columns=["description", "single", "multi", "icon", "family", "samples"])

    USE_RICH = True
    if USE_RICH:
        import rich.console
        import rich.table

        from ._rich_table import df_to_table

        console = rich.console.Console()
        table = rich.table.Table()
        bar_columns = ("single", "multi") if bars else ()
        console.print(df_to_table(data, table, bar_columns=bar_columns, bar_width=bar_width))
        if breakdown:
            _print_breakdowns(console, breakdown_devices, breakdown_skipped, bar_columns, bar_width)
    else:
        click.echo(data)


def _print_breakdowns(
    console: rich.console.Console,
    devices: list[Device],
    skipped: int,
    bar_columns: tuple[str, ...],
    bar_width: int,
) -> None:
    import pandas as pd
    import rich.table

    from ._breakdown import get_breakdowns
    from ._rich_table import df_to_table

    breakdowns = get_breakdowns(devices)
    frames = [
        None if b is None else pd.DataFrame({"single": b.single, "multi": b.multi})
        for b in breakdowns
    ]
    # one scale for every CPU so the bars are comparable across tables
    shown = [f for f in frames if f is not None]
    maximums = {c: max(f[c].max() for f in shown) for c in ("single", "multi")} if shown else {}

    for device, b, frame in zip(devices, breakdowns, frames, strict=True):
        if b is None or frame is None:
            console.print(f"[yellow]No recent result found for {device[1]}[/yellow]")
            continue
        table = rich.table.Table(
            title=f"{b.name} workloads",
            caption=(
                f"From one representative result (single {b.single_score}, "
                f"multi {b.multi_score}; chart {device[2]:.0f}, {device[3]:.0f}): {b.url}"
            ),
        )
        console.print()
        console.print(
            df_to_table(
                frame,
                table,
                index_name="workload",
                bar_columns=bar_columns,
                bar_width=bar_width,
                bar_maximums=maximums,
            )
        )
    if skipped:
        console.print(
            f"[dim]Breakdown shown for the first {len(devices)} CPUs only "
            f"({skipped} more matched; raise --breakdown-limit to see them).[/dim]"
        )


cli()
