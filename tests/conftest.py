from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

import pytest

UPSTREAM = Path(__file__).resolve().parent / "upstream"


def read_upstream(name: str) -> str:
    """Return a third-party test file, checked against tests/upstream/MANIFEST.json.

    The files are not committed: `python scripts/fetch_upstream.py` fetches them. Their
    tests skip while a file is absent and fail if it differs from the manifest.
    """
    path = UPSTREAM / name
    if not path.is_file():
        pytest.skip(f"{name} is not fetched; run python scripts/fetch_upstream.py")
    entry = json.loads((UPSTREAM / "MANIFEST.json").read_text(encoding="utf-8"))[name]
    body = path.read_bytes()
    assert hashlib.sha256(body).hexdigest() == entry["sha256"], f"{name} differs from MANIFEST"
    return body.decode("utf-8")


def wpt_table(name: str) -> list[list[Any]]:
    """Read the test table out of a fetched WPT css-color parsing page.

    Most pages hold a ``tests = [...]`` array of JSON-compatible rows (with trailing
    commas); color-valid.html instead calls ``test_valid_value("color", ...)`` per row.
    """
    text = read_upstream(name)
    found = re.search(r"^tests = (\[.*?^\]);", text, re.S | re.M)
    if found:
        rows: list[list[Any]] = json.loads(re.sub(r",(\s*\])", r"\1", found.group(1)))
        return rows
    calls = re.findall(r'^test_valid_value\("color", (.*)\);$', text, re.M)
    return [json.loads(f"[{call}]") for call in calls]
