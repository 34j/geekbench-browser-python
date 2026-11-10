"""Importing the CLI entry module must not run the CLI.

Regression test: ``geekbench_browser/__main__.py`` called ``cli()`` at
module level, so merely importing it (test collection, coverage, linters,
other tooling) executed the full command instead of just defining it.

The test imports the module in a subprocess with stdout rigged to raise on
any write: if the import executes the command, the benchmark table it prints
trips the guard and the import fails. A bare definition writes nothing.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest

pytest.importorskip("nodriver")

_IMPORT_PROBE = "\n".join(
    [
        "import sys",
        "class _Noisy:",
        "    def write(self, s): raise AssertionError('CLI executed on import')",
        "    def flush(self): pass",
        "sys.stdout = _Noisy()",
        "import geekbench_browser.__main__",
    ]
)


def test_importing_main_module_does_not_run_the_cli():
    src_dir = Path(__file__).resolve().parents[1] / "src"
    env = dict(os.environ)
    env["PYTHONPATH"] = str(src_dir) + os.pathsep + env.get("PYTHONPATH", "")
    proc = subprocess.run(
        [sys.executable, "-c", _IMPORT_PROBE],
        capture_output=True,
        text=True,
        env=env,
        timeout=300,
    )

    assert proc.returncode == 0, proc.stderr
