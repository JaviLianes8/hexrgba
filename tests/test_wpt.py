"""Golden vectors from the Web Platform Tests css/css-color/parsing tables.

The vectors live in fixtures/wpt-css-color-parsing.json, copied as fetched on 2026-10-12
from https://github.com/web-platform-tests/wpt/tree/786385c76ca1c01d40eba0234dc59384e2eb73d4/css/css-color/parsing
"""

import json
from pathlib import Path

import pytest

from hexrgba import is_color, parse_color
from hexrgba._hex import is_hex_body

_DATA = json.loads(
    (Path(__file__).parent / "fixtures" / "wpt-css-color-parsing.json").read_text("utf-8")
)["files"]


KELVIN = chr(0x212A)  # KELVIN SIGN, a look-alike of the letter K


def _out_of_scope(text: str) -> bool:
    # CSS comments need a tokenizer and currentcolor needs a cascade; both are out of scope.
    return "/*" in text or text.strip().lower() == "currentcolor"


@pytest.mark.parametrize("entry", _DATA["color-computed-hex-color.html"])
def test_wpt_valid_hex_serializes_like_a_browser(entry: list[str]) -> None:
    assert parse_color(entry[0], strict=True).to_css() == entry[1]


@pytest.mark.parametrize("entry", _DATA["color-invalid-hex-color.html"])
def test_wpt_invalid_hex_is_rejected_in_both_modes(entry: list[str]) -> None:
    assert not is_color(entry[0], strict=True)
    assert not is_color(entry[0])


_NAMED = [e for e in _DATA["color-computed-named-color.html"] if not _out_of_scope(e[0])]


def test_wpt_named_vectors_cover_most_of_the_file() -> None:
    skipped = len(_DATA["color-computed-named-color.html"]) - len(_NAMED)
    assert len(_NAMED) > 440
    assert skipped == 3


@pytest.mark.parametrize("entry", _NAMED)
def test_wpt_named_color_serializes_like_a_browser(entry: list[str]) -> None:
    assert parse_color(entry[0]).to_css() == entry[1]
    if entry[0] == entry[0].strip():
        assert parse_color(entry[0], strict=True).to_css() == entry[1]
    else:
        assert not is_color(entry[0], strict=True)


@pytest.mark.parametrize("entry", _DATA["color-invalid-named-color.html"])
def test_wpt_invalid_keyword_is_rejected_in_both_modes(entry: list[str]) -> None:
    assert not is_hex_body(entry[0].strip())
    assert not is_color(entry[0], strict=True)
    assert not is_color(entry[0])


def test_wpt_kelvin_sign_look_alikes_are_present_and_rejected() -> None:
    look_alikes = [e[0] for e in _DATA["color-invalid-named-color.html"] if KELVIN in e[0]]
    assert "blac" + KELVIN in look_alikes
    for text in look_alikes:
        assert not is_color(text)


@pytest.mark.parametrize(
    "entry", [e for e in _DATA["color-valid.html"] if e[0].startswith("#") or e[0].isalpha()]
)
def test_wpt_valid_hex_and_keywords_parse(entry: list[str]) -> None:
    if _out_of_scope(entry[0]):
        assert not is_color(entry[0])
        return
    color = parse_color(entry[0], strict=True)
    if entry[0].startswith("#"):
        assert color.to_css() == entry[1]
