# Geekbench Browser Python

<p align="center">
  <a href="https://github.com/34j/geekbench-browser-python/actions/workflows/ci.yml?query=branch%3Amain">
    <img src="https://img.shields.io/github/actions/workflow/status/34j/geekbench-browser-python/ci.yml?branch=main&label=CI&logo=github&style=flat-square" alt="CI Status" >
  </a>
  <a href="https://geekbench-browser-python.readthedocs.io">
    <img src="https://img.shields.io/readthedocs/geekbench-browser-python.svg?logo=read-the-docs&logoColor=fff&style=flat-square" alt="Documentation Status">
  </a>
</p>
<p align="center">
  <a href="https://codecov.io/gh/34j/geekbench-browser-python">
    <img src="https://img.shields.io/codecov/c/github/34j/geekbench-browser-python.svg?logo=codecov&logoColor=fff&style=flat-square" alt="Test coverage percentage">
  </a>
  <a href="https://github.com/astral-sh/uv">
    <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json" alt="uv">
  </a>
  <a href="https://github.com/astral-sh/ruff">
    <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff">
  </a>
  <a href="https://github.com/j178/prek">
    <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/j178/prek/master/docs/assets/badge-v0.json" alt="prek">
  </a>
</p>
<p align="center">
  <a href="https://pypi.org/project/geekbench-browser-python/">
    <img src="https://img.shields.io/pypi/v/geekbench-browser-python.svg?logo=python&logoColor=fff&style=flat-square" alt="PyPI Version">
  </a>
  <img src="https://img.shields.io/pypi/pyversions/geekbench-browser-python.svg?style=flat-square&logo=python&amp;logoColor=fff" alt="Supported Python versions">
  <img src="https://img.shields.io/pypi/l/geekbench-browser-python.svg?style=flat-square" alt="License">
</p>

---

**Documentation**: <a href="https://geekbench-browser-python.readthedocs.io" target="_blank">https://geekbench-browser-python.readthedocs.io </a>

**Source Code**: <a href="https://github.com/34j/geekbench-browser-python" target="_blank">https://github.com/34j/geekbench-browser-python </a>

---

Simple package for getting data from [browser.geekbench.com](https://browser.geekbench.com/).

## Installation

Install this via pip (or your favourite package manager):

```shell
pip install geekbench-browser-python
```

## Usage

Both `geekbench-browser` and `gbr` are available as CLI commands. Requests are cached in `~/.cache/geekbench-browser-python` by default and refreshed every 24 hours.

- Getting all data

```shell
$ gbr
(very long output)
```

- Getting specific CPU data (Not case sensitive)

```shell
$ gbr 3600x 3900x
┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━┓
┃                    ┃ description        ┃ single ┃ multi ┃ icon       ┃ family  ┃ samples ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━┩
│ AMD Ryzen 5 3600X  │ 3.8 GHz (6 cores)  │ 1243   │ 6857  │ amd-ryzen5 │ Matisse │ 9606    │
│ AMD Ryzen 5 3600XT │ 3.8 GHz (6 cores)  │ 1301   │ 7041  │ amd        │ Matisse │ 3241    │
│ AMD Ryzen 9 3900X  │ 3.8 GHz (12 cores) │ 1275   │ 11664 │ amd-ryzen9 │ Matisse │ 24420   │
│ AMD Ryzen 9 3900XT │ 3.8 GHz (12 cores) │ 1316   │ 11958 │ amd        │ Matisse │ 3409    │
└────────────────────┴────────────────────┴────────┴───────┴────────────┴─────────┴─────────┘
```

- Getting current CPU data and speific CPU data

```shell
$ gbr current 3900x
┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━┓
┃                    ┃ description        ┃ single ┃ multi ┃ icon       ┃ family  ┃ samples ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━┩
│ AMD Ryzen 9 3900X  │ 3.8 GHz (12 cores) │ 1275   │ 11664 │ amd-ryzen9 │ Matisse │ 24420   │
│ AMD Ryzen 9 3900XT │ 3.8 GHz (12 cores) │ 1316   │ 11958 │ amd        │ Matisse │ 3409    │
│ AMD Ryzen 9 3950X  │ 3.5 GHz (16 cores) │ 1295   │ 14127 │ amd-ryzen9 │ Matisse │ 11023   │
└────────────────────┴────────────────────┴────────┴───────┴────────────┴─────────┴─────────┘
```

- Sorting by single score

```shell
$ gbr "ryzen 9" -s single
┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━┓
┃                    ┃ description        ┃ single ┃ multi ┃ icon       ┃ family    ┃ samples ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━┩
│ AMD Ryzen 9 7950X  │ 4.5 GHz (16 cores) │ 2191   │ 23093 │ amd        │ Raphael   │ 5996    │
│ AMD Ryzen 9 7900X  │ 4.7 GHz (12 cores) │ 2181   │ 19243 │ amd        │ Raphael   │ 1857    │
│ AMD Ryzen 9 7900   │ 3.7 GHz (12 cores) │ 2098   │ 17982 │ amd        │ Raphael   │ 177     │
│ AMD Ryzen 9 5950X  │ 3.4 GHz (16 cores) │ 1682   │ 16439 │ amd        │ Vermeer   │ 58690   │
│ AMD Ryzen 9 5900X  │ 3.7 GHz (12 cores) │ 1671   │ 13899 │ amd        │ Vermeer   │ 60238   │
│ AMD Ryzen 9 5900   │ 3.0 GHz (12 cores) │ 1626   │ 12224 │ amd        │ Vermeer   │ 345     │
│ AMD Ryzen 9 6900HX │ 3.3 GHz (8 cores)  │ 1513   │ 9174  │ amd        │ Rembrandt │ 1639    │
│ AMD Ryzen 9 6900HS │ 3.3 GHz (8 cores)  │ 1416   │ 8479  │ amd        │ Rembrandt │ 1696    │
│ AMD Ryzen 9 5900HX │ 3.3 GHz (8 cores)  │ 1410   │ 7640  │ amd        │ Cezanne   │ 13702   │
│ AMD Ryzen 9 3900XT │ 3.8 GHz (12 cores) │ 1316   │ 11958 │ amd        │ Matisse   │ 3409    │
│ AMD Ryzen 9 3950X  │ 3.5 GHz (16 cores) │ 1295   │ 14127 │ amd-ryzen9 │ Matisse   │ 11023   │
│ AMD Ryzen 9 3900X  │ 3.8 GHz (12 cores) │ 1275   │ 11664 │ amd-ryzen9 │ Matisse   │ 24420   │
│ AMD Ryzen 9 3900   │ 3.1 GHz (12 cores) │ 1222   │ 10768 │ amd        │ Matisse   │ 1078    │
│ AMD Ryzen 9 4900H  │ 3.3 GHz (8 cores)  │ 1144   │ 6854  │ amd        │ Renoir    │ 1316    │
│ AMD Ryzen 9 4900HS │ 3.0 GHz (8 cores)  │ 1079   │ 6862  │ amd-ryzen9 │ Renoir    │ 4532    │
└────────────────────┴────────────────────┴────────┴───────┴────────────┴───────────┴─────────┘
```

- All options

```shell
$ gbr -h
Usage: gbr [OPTIONS] [NAMES]...

Options:
  -mc, --min-cores INTEGER        Minimum number of cores
  -xc, --max-cores INTEGER        Maximum number of cores
  -mf, --min-frequency FLOAT      Minimum frequency in GHz
  -xf, --max-frequency FLOAT      Maximum frequency in GHz
  -ms, --min-single FLOAT         Minimum single core score
  -xs, --max-single FLOAT         Maximum single core score
  -mm, --min-multi FLOAT          Minimum multi core score
  -xm, --max-multi FLOAT          Maximum multi core score
  -i, --icon TUPLE                Icon to search for
  -f, --family TUPLE              Family to search for
  -s, --sort [name|single|multi|frequency|cores|id]
                                  Sort by (reverse is default except for name,
                                  id)
  -r, --reverse                  Reverse the sort order
  -v, --verbose                   Verbose output
  -h, --help                      Show this message and exit.
```

## Contributors ✨

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- prettier-ignore-start -->
<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/34j"><img src="https://avatars.githubusercontent.com/u/55338215?v=4?s=80" width="80px;" alt="34j"/><br /><sub><b>34j</b></sub></a><br /><a href="https://github.com/34j/geekbench-browser-python/commits?author=34j" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/shvchk"><img src="https://avatars.githubusercontent.com/u/872945?v=4?s=80" width="80px;" alt="Andrei Shevchuk"/><br /><sub><b>Andrei Shevchuk</b></sub></a><br /><a href="https://github.com/34j/geekbench-browser-python/issues?q=author%3Ashvchk" title="Bug reports">🐛</a> <a href="https://github.com/34j/geekbench-browser-python/commits?author=shvchk" title="Code">💻</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->
<!-- prettier-ignore-end -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!

## Credits

This package was created with
[Copier](https://copier.readthedocs.io/) and the
[browniebroke/pypackage-template](https://github.com/browniebroke/pypackage-template)
project template.
