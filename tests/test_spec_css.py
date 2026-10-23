"""CSS Color 4 and Compositing rules read back out of the fetched W3C pages.

The pages are fetched by `python scripts/fetch_upstream.py` at the dated W3C snapshots and
the w3c/wcag commit pinned in tests/upstream/MANIFEST.json (fetched 2026-10-23); these tests
skip until then. Every rule below is parsed from the fetched text and the library is
checked against an implementation built from that text, not against numbers in this file.
"""

from __future__ import annotations

import math
import re
from fractions import Fraction

from conftest import read_upstream
from spec_text import number, plain

from hexrgba import NAMED_COLORS, css_alpha, is_hex, parse_color

CSS = "css-color-4-20261022.html"


def test_named_color_table_is_the_spec_table_row_for_row() -> None:
    rows = re.findall(
        r'id="valdef-color-([a-z]+)">\1</dfn>\s*<td>(#[0-9a-f]{6})\s*<td>(\d+) (\d+) (\d+)',
        read_upstream(CSS),
    )
    assert len(rows) == 148
    for _name, value, *decimal in rows:
        assert [int(value[i : i + 2], 16) for i in (1, 3, 5)] == [int(d) for d in decimal]
    assert list(NAMED_COLORS.items()) == [(name, value) for name, value, *_ in rows]


def test_hex_lengths_are_the_ones_the_spec_lists() -> None:
    found = re.search(r"consists of (\d), (\d), (\d), or (\d) hexadecimal digits", plain(CSS))
    assert found
    lengths = {int(group) for group in found.groups()}
    assert lengths == {3, 4, 6, 8}
    for size in range(12):
        assert is_hex("#" + "aB9"[size % 3] * size) is (size in lengths), size


def test_keywords_are_ascii_case_insensitive_as_the_spec_says() -> None:
    assert "all of these keywords are ASCII case-insensitive" in plain(CSS)
    assert parse_color("ReBeCcAPurple", strict=True).hex == "#663399"


def test_transparent_is_transparent_black() -> None:
    text = plain(CSS)
    assert "transparent black is the same color, but fully transparent" in text
    assert parse_color("transparent").to_css() == "rgba(0, 0, 0, 0)"


def test_alpha_serialization_follows_the_numbered_steps_for_every_byte() -> None:
    text = plain(CSS)
    step = (
        r"between 0 and 100 inclusive that, when multiplied with ([\d.]+) and rounded to the"
        r" closest integer \(rounding up if two values are equally close\), equals alpha, let"
        r" rounded be that integer divided by (\d+)\. Otherwise, let rounded be alpha divided"
        r" by ([\d.]+) and rounded to the closest integer \(rounding up if two values are"
        r" equally close\), divided by (\d+)\."
    )
    times, first, divisor, second = number(step, text)

    def up(value: Fraction) -> int:
        return math.floor(value + Fraction(1, 2))

    for alpha in range(256):
        hits = [n for n in range(101) if up(n * times) == alpha]
        rounded = Fraction(hits[0], first) if hits else Fraction(up(alpha / divisor), second)
        assert Fraction(css_alpha(alpha)) == rounded, alpha


def test_spec_alpha_examples() -> None:
    text = plain(CSS)
    assert (
        "the integer 93 satisfies the criterion because Math.round(93 * 2.55) is 237,"
        ' and so the alpha is serialized as "0.93"'
    ) in text
    assert css_alpha(237) == "0.93"
    # The prose example for 236 prints 0.92549, which its own numbered steps do not give
    # (936 / 0.255 rounds to 925, divided by 1000). The library follows the steps.
    assert 'the alpha is serialized as "0.92549"' in text
    assert css_alpha(236) == "0.925"


def test_compositing_formulas_are_the_ones_implemented() -> None:
    # The spec writes alpha as the Greek letter; '@' stands for it here.
    text = plain("compositing-1-20240321.html").replace(chr(0x3B1), "@")
    for formula in ("co = Cs x @s + Cb x @b x (1 - @s)", "@o = @s + @b x (1 - @s)"):
        assert formula in text, formula
    assert "Co = co / @o" in text
