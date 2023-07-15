from logging import INFO, basicConfig, getLogger

import click

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
@click.option(
    "--family", "-f", cls=OptionEatAll, type=tuple, help="Family to search for"
)
@click.option(
    "--sort",
    "-s",
    type=click.Choice(["name", "single", "multi", "frequency", "cores", "id"]),
    default="name",
    help="Sort by (reverse is default except for name, id)",
)
@click.option("--reverse", "-r", is_flag=True, help="Reverse the sort order")
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
        LOG.info(f"Current CPU: {name}")

        # geekbench cpuname is shorter than cpuinfo brand_raw
        current_names = data.loc[data["name"].map(lambda x: x in name)]["name"]
        if current_names.empty:
            raise ValueError(f"Could not find current CPU name in database: {name}")

        # remove current from names and add current_names
        names = [n for n in names if n != "current"] + list(current_names)

    # filter data
    if names:
        data = data.loc[
            data["name"].str.contains("|".join(names), regex=True, case=False)
        ]
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
            data["icon"]
            .astype(str)
            .str.contains("|".join(icon), regex=True, case=False)
        ]
    if family:
        data = data.loc[
            data["family"]
            .astype(str)
            .str.contains("|".join(family), regex=True, case=False)
        ]

    # sort data
    if sort in ["name", "id"]:
        reverse = not reverse
    data.sort_values(by=sort, inplace=True, ascending=reverse)

    # drop columns that does not make sense
    if not verbose:
        data = data.drop(columns=["cores", "frequency", "id", "name"])
    data = data.reindex(
        columns=["description", "single", "multi", "icon", "family", "samples"]
    )

    USE_RICH = True
    if USE_RICH:
        import rich
        import rich.box
        import rich.console
        import rich.table

        from ._rich_table import df_to_table

        console = rich.console.Console()
        table = rich.table.Table()
        console.print(df_to_table(data, table))
    else:
        click.echo(data)


cli()
