"""Hand-written cases for the browser agreement that tests/test_wpt.py checks on WPT pages.

These run without the fetched pages. Every case is written by hand from CSS Color 4
(https://www.w3.org/TR/css-color-4/, sections 5.2, 6.1 and 16), not copied from WPT.
"""

from __future__ import annotations

import pytest

from hexrgba import is_color, parse_color

# Hand-written: input and the serialization CSS Color 4 section 16 gives for it.
SERIALIZED = [
    ("#0f8", "rgb(0, 255, 136)"),
    ("#0F8C", "rgba(0, 255, 136, 0.8)"),
    ("#00ff8840", "rgba(0, 255, 136, 0.25)"),
    ("#ABCDEF", "rgb(171, 205, 239)"),
    ("rebeccapurple", "rgb(102, 51, 153)"),
    ("TRANSPARENT", "rgba(0, 0, 0, 0)"),
]

# Hand-written: text that is not a hex color or named color in any mode.
REJECTED = ["#", "#12", "#12345", "#1234567", "#ggg", "reed", "blac" + chr(0x212A), "/**/red"]


@pytest.mark.parametrize(("text", "expected"), SERIALIZED)
def test_serializes_like_css_color_4(text: str, expected: str) -> None:
    assert parse_color(text, strict=True).to_css() == expected


@pytest.mark.parametrize("text", REJECTED)
def test_rejected_in_both_modes(text: str) -> None:
    assert not is_color(text)
    assert not is_color(text, strict=True)


def test_currentcolor_needs_a_cascade_and_is_rejected() -> None:
    assert not is_color("currentcolor")


@pytest.mark.parametrize("text", ["#fff ", " navy "])
def test_surrounding_space_is_lenient_only(text: str) -> None:
    assert is_color(text)
    assert not is_color(text, strict=True)
