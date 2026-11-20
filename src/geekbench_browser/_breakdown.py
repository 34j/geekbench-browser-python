"""Per-workload score breakdowns.

The processor chart only carries the aggregate single/multi scores, so the
individual workload scores (File Compression, Navigation, ...) are taken from a
representative user-submitted result: the recent result for that processor
whose scores are closest to the chart scores.
"""

import asyncio
from dataclasses import asdict, dataclass
from json import dumps, loads
from logging import getLogger
from time import time
from typing import Any
from urllib.parse import urlencode

import nodriver as uc

from ._main import CACHE_EXPIRE_AFTER, CACHE_PATH, LOAD_ATTEMPTS

LOG = getLogger(__name__)

BASE_URL = "https://browser.geekbench.com"
# Search pages (25 recent results each) to look through for a representative result.
# Recent results can be flooded by virtual machines with few cores, so look deep.
MAX_SEARCH_PAGES = 20
# Search pages fetched at once after the first one.
SEARCH_BATCH = 5
# Stop searching once a result is this close to the chart scores (summed relative error).
GOOD_ENOUGH = 0.1

# (id, name, single, multi, cores); cores is None when unknown
Device = tuple[int, str, float, float, int | None]

_PARSE_SEARCH_JS = """
const parse = (doc) => [...doc.querySelectorAll(".list-col")].map((col) => {
  const num = (el) => parseInt(el.textContent.replace(/[^0-9]/g, ""), 10);
  const link = col.querySelector('a[href^="/v6/cpu/"]');
  const model = col.querySelector(".list-col-model");
  const scores = col.querySelectorAll(".list-col-text-score");
  if (!link || !model || scores.length < 2) return null;
  return {
    id: parseInt(link.getAttribute("href").split("/").pop(), 10),
    model: model.textContent.replace(/\\s+/g, " ").trim(),
    single: num(scores[0]),
    multi: num(scores[1]),
  };
}).filter(Boolean);
"""

# The page scripts return null until the real page (not a bot-check interstitial) is loaded.
_SEARCH_JS = f"""
(() => {{
  if (document.readyState !== "complete" || !document.title.includes("Geekbench")) return null;
  {_PARSE_SEARCH_JS}
  return JSON.stringify(parse(document));
}})()
"""

# Fetches further search pages from within the already loaded page; __URLS__ is a JSON list.
_SEARCH_MORE_JS = f"""
(async () => {{
  {_PARSE_SEARCH_JS}
  const docs = await Promise.all(__URLS__.map((url) => fetch(url)
    .then((response) => (response.ok ? response.text() : ""))
    .then((html) => new DOMParser().parseFromString(html, "text/html"))));
  return JSON.stringify(docs.map(parse));
}})()
"""

_RESULT_JS = """
(() => {
  if (document.readyState !== "complete" || !document.title.includes("Geekbench")) return null;
  const tables = [...document.querySelectorAll("table.benchmark-table")];
  if (tables.length < 2) return null;
  const parse = (table) => Object.fromEntries([...table.querySelectorAll("tbody tr")].map((row) => [
    row.querySelector("td.name").textContent.replace(/\\s+/g, " ").trim(),
    parseInt(row.querySelector("td.score").childNodes[0].textContent.replace(/[^0-9]/g, ""), 10),
  ]));
  return JSON.stringify({ single: parse(tables[0]), multi: parse(tables[1]) });
})()
"""


@dataclass(frozen=True)
class Breakdown:
    """Per-workload scores of one representative result for a processor."""

    name: str
    result_id: int
    single_score: int
    multi_score: int
    single: dict[str, int]
    multi: dict[str, int]

    @property
    def url(self) -> str:
        return f"{BASE_URL}/v6/cpu/{self.result_id}"


def distance(candidate: dict[str, Any], single: float, multi: float) -> float:
    """Summed relative error of a result's scores against the chart scores."""
    return abs(candidate["single"] / single - 1) + abs(candidate["multi"] / multi - 1)


def pick_result(
    candidates: list[dict[str, Any]],
    name: str,
    single: float,
    multi: float,
    cores: int | None = None,
) -> dict[str, Any] | None:
    """Pick the search result for exactly ``name`` closest to the chart scores.

    Results reporting a different core count than the chart (virtual machines,
    disabled cores) are ignored when ``cores`` is known.
    """
    prefix = name.casefold() + " "
    matching = [
        c
        for c in candidates
        if (c["model"].casefold() + " ").startswith(prefix)
        and c["single"] > 0
        and c["multi"] > 0
        and (cores is None or f"({cores} cores)" in c["model"])
    ]
    if not matching:
        return None
    return min(matching, key=lambda c: distance(c, single, multi))


async def _load(browser: uc.Browser, url: str, script: str) -> tuple[uc.Tab, Any]:
    tab = await browser.get(url)
    for _ in range(LOAD_ATTEMPTS):
        text = await tab.evaluate(script, return_by_value=True)
        if isinstance(text, str):
            return tab, loads(text)
        await asyncio.sleep(1)
    raise TimeoutError(f"Timed out loading {url}")


def _search_url(name: str, page: int) -> str:
    return f"{BASE_URL}/search?{urlencode({'k': 'v6_cpu', 'q': name, 'page': page})}"


async def _fetch(browser: uc.Browser, device: Device) -> Breakdown | None:
    _, name, single, multi, cores = device

    def good(picked: dict[str, Any] | None) -> bool:
        return picked is not None and distance(picked, single, multi) <= GOOD_ENOUGH

    tab, candidates = await _load(browser, _search_url(name, 1), _SEARCH_JS)
    picked = pick_result(candidates, name, single, multi, cores)
    next_page = 2
    while candidates and not good(picked) and next_page <= MAX_SEARCH_PAGES:
        pages = range(next_page, min(next_page + SEARCH_BATCH, MAX_SEARCH_PAGES + 1))
        urls = dumps([_search_url(name, page) for page in pages])
        script = _SEARCH_MORE_JS.replace("__URLS__", urls)
        found = loads(await tab.evaluate(script, await_promise=True, return_by_value=True))
        candidates += [candidate for page in found for candidate in page]
        picked = pick_result(candidates, name, single, multi, cores)
        if not all(found):  # ran past the last page of results
            break
        next_page = pages.stop
    if picked is None:
        return None
    LOG.info("Representative result for %s: %s", name, picked)
    _, scores = await _load(browser, f"{BASE_URL}/v6/cpu/{picked['id']}", _RESULT_JS)
    return Breakdown(
        name=name,
        result_id=picked["id"],
        single_score=picked["single"],
        multi_score=picked["multi"],
        single=scores["single"],
        multi=scores["multi"],
    )


async def _fetch_all(missing: list[Device]) -> dict[int, Breakdown | None]:
    browser = await uc.start(user_data_dir=CACHE_PATH, sandbox=False, expert=True)
    try:
        return {device[0]: await _fetch(browser, device) for device in missing}
    finally:
        await browser.aclose()
        browser.stop()


def get_breakdowns(devices: list[Device]) -> list[Breakdown | None]:
    """Get a breakdown for each device, using a daily cache.

    An entry is ``None`` when no recent result for that processor was found.
    """
    found: dict[int, Breakdown | None] = {}
    missing = []
    for device in devices:
        cache_file = CACHE_PATH / f"breakdown-{device[0]}.json"
        if cache_file.exists() and time() - cache_file.stat().st_mtime < CACHE_EXPIRE_AFTER:
            found[device[0]] = Breakdown(**loads(cache_file.read_bytes()))
        else:
            missing.append(device)
    if missing:
        fetched = asyncio.run(_fetch_all(missing))
        CACHE_PATH.mkdir(parents=True, exist_ok=True)
        for device_id, breakdown in fetched.items():
            if breakdown is not None:
                (CACHE_PATH / f"breakdown-{device_id}.json").write_text(dumps(asdict(breakdown)))
        found.update(fetched)
    return [found[device[0]] for device in devices]
