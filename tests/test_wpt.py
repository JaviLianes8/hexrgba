"""Golden vectors from the Web Platform Tests css/css-color/parsing tables.

The pages are not committed. `python scripts/fetch_upstream.py` fetches them at the commit
pinned in tests/upstream/MANIFEST.json; these tests skip until then and fail if a page
differs from the manifest.
"""

from __future__ import annotations

from typing import Any

from conftest import wpt_table

from hexrgba import is_color, parse_color
from hexrgba._hex import is_hex_body

KELVIN = chr(0x212A)  # KELVIN SIGN, a look-alike of the letter K

Rows = list[list[Any]]


def _out_of_scope(text: str) -> bool:
    # CSS comments need a tokenizer and currentcolor needs a cascade; both are out of scope.
    return "/*" in text or text.strip().lower() == "currentcolor"


def test_wpt_valid_hex_serializes_like_a_browser() -> None:
    rows: Rows = wpt_table("color-computed-hex-color.html")
    assert len(rows) == 6
    for entry in rows:
        assert parse_color(entry[0], strict=True).to_css() == entry[1], entry


def test_wpt_invalid_hex_is_rejected_in_both_modes() -> None:
    rows: Rows = wpt_table("color-invalid-hex-color.html")
    assert len(rows) == 10
    for entry in rows:
        assert not is_color(entry[0], strict=True), entry
        assert not is_color(entry[0]), entry


def test_wpt_named_color_serializes_like_a_browser() -> None:
    rows: Rows = wpt_table("color-computed-named-color.html")
    named = [e for e in rows if not _out_of_scope(e[0])]
    assert len(named) > 440
    assert len(rows) - len(named) == 3
    for entry in named:
        assert parse_color(entry[0]).to_css() == entry[1], entry
        if entry[0] == entry[0].strip():
            assert parse_color(entry[0], strict=True).to_css() == entry[1], entry
        else:
            assert not is_color(entry[0], strict=True), entry


def test_wpt_invalid_keyword_is_rejected_in_both_modes() -> None:
    rows: Rows = wpt_table("color-invalid-named-color.html")
    assert len(rows) > 150
    for entry in rows:
        assert not is_hex_body(entry[0].strip()), entry
        assert not is_color(entry[0], strict=True), entry
        assert not is_color(entry[0]), entry


def test_wpt_kelvin_sign_look_alikes_are_present_and_rejected() -> None:
    rows: Rows = wpt_table("color-invalid-named-color.html")
    look_alikes = [e[0] for e in rows if KELVIN in e[0]]
    assert "blac" + KELVIN in look_alikes
    for text in look_alikes:
        assert not is_color(text)


def test_wpt_valid_hex_and_keywords_parse() -> None:
    rows: Rows = wpt_table("color-valid.html")
    picked = [e for e in rows if e[0].startswith("#") or e[0].isalpha()]
    assert len(picked) >= 5
    for entry in picked:
        if _out_of_scope(entry[0]):
            assert not is_color(entry[0])
            continue
        color = parse_color(entry[0], strict=True)
        if entry[0].startswith("#"):
            assert color.to_css() == entry[1], entry
