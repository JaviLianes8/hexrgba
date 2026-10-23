"""Read rules out of the fetched specification pages (see tests/upstream/MANIFEST.json)."""

from __future__ import annotations

import html
import re
from fractions import Fraction

from conftest import read_upstream


def plain(name: str) -> str:
    text = html.unescape(re.sub(r"<[^>]+>", "", read_upstream(name)))
    return re.sub(r"\s+", " ", text)


def number(pattern: str, text: str) -> list[Fraction]:
    found = re.search(pattern, text)
    assert found, pattern
    return [Fraction(group) for group in found.groups()]
