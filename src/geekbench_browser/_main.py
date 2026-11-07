# ruff: noqa: PD002, RET504

import asyncio
from json import dumps, loads
from pathlib import Path
from time import time

import nodriver as uc
from pandas import DataFrame

CACHE_PATH = Path.home() / ".cache" / "geekbench_browser"
CACHE_FILE = CACHE_PATH / "processor-benchmarks.json"
CACHE_EXPIRE_AFTER = 86400
GEEKBENCH_URL = "https://browser.geekbench.com/processor-benchmarks.json"


async def _get_json() -> dict:
    browser = await uc.start(
        user_data_dir=CACHE_PATH,
        sandbox=False,
        expert=True,
    )
    try:
        page = await browser.get(GEEKBENCH_URL)
        return loads(await page.evaluate("document.body.innerText", return_by_value=True))
    finally:
        await browser.aclose()
        browser.stop()


def get_data() -> DataFrame:
    if CACHE_FILE.exists() and time() - CACHE_FILE.stat().st_mtime < CACHE_EXPIRE_AFTER:
        json_data = loads(CACHE_FILE.read_bytes())
    else:
        json_data = asyncio.run(_get_json())
        CACHE_PATH.mkdir(parents=True, exist_ok=True)
        CACHE_FILE.write_text(dumps(json_data))

    df = DataFrame(json_data["devices"])
    df.set_index("name", inplace=True, drop=False)
    df.index.name = None
    df["frequency"] = (
        df["description"].str.extract(r"(\d+\.?\d+) [MG]Hz").astype(float, errors="ignore")
    )
    df.loc[df["description"].str.contains("MHz"), "frequency"] *= 1e-3
    df["cores"] = df["description"].str.extract(r"(\d+) cores").astype(int, errors="ignore")
    df = df.rename(columns={"score": "single", "multicore_score": "multi"})
    return df
