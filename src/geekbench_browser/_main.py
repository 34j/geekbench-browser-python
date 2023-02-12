from logging import getLogger
from pathlib import Path

from pandas import DataFrame
from requests_cache import CachedSession

LOG = getLogger(__name__)

CACHE_PATH = Path.home() / ".cache" / "geekbench_browser" / "cache.sqlite"
GEEKBENCH_URL = "https://browser.geekbench.com/processor-benchmarks.json"


def get_data() -> DataFrame:
    with CachedSession(
        CACHE_PATH.as_posix(), backend="sqlite", expire_after=86400
    ) as session:
        resp = session.get(GEEKBENCH_URL)
        LOG.info(
            f"Last retrieved: {resp.created_at}, Cache expires: {resp.expires}, "
            f"Cache path: {CACHE_PATH}"
        )

        json_data = session.get(GEEKBENCH_URL).json()
        try:
            df = DataFrame(json_data["devices"])
        except Exception as e:
            raise RuntimeError("Failed to parse json data") from e
        df.set_index("name", inplace=True, drop=False)
        df.index.name = None
        df["frequency"] = (
            df["description"]
            .str.extract(r"(\d+\.?\d+) [MG]Hz")
            .astype(float, errors="ignore")
        )
        df.loc[df["description"].str.contains("MHz"), "frequency"] *= 1e-3
        df["cores"] = (
            df["description"].str.extract(r"(\d+) cores").astype(int, errors="ignore")
        )
        df = df.rename(columns={"score": "single", "multicore_score": "multi"})
        return df
