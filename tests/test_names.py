"""The named color table against the CSS Color 4 spec table and the Pillow oracle."""

import json
from pathlib import Path

import pytest

from hexrgba import NAMED_COLORS, Color, ColorNameError, parse_color
from hexrgba._hex import is_hex_body

# Extracted programmatically from https://www.w3.org/TR/css-color-4/#named-colors,
# fetched 2026-10-12; see the fixture's own source fields.
_SPEC = json.loads(
    (Path(__file__).parent / "fixtures" / "css-color-4-named-colors.json").read_text("utf-8")
)["colors"]


def test_table_matches_the_spec_row_for_row_in_order() -> None:
    assert list(NAMED_COLORS.items()) == [tuple(row) for row in _SPEC]


def test_table_has_148_opaque_keywords_including_rebeccapurple() -> None:
    assert len(NAMED_COLORS) == 148
    assert NAMED_COLORS["rebeccapurple"] == "#663399"
    assert "transparent" not in NAMED_COLORS


def test_values_are_canonical_lower_case_hex() -> None:
    for value in NAMED_COLORS.values():
        assert value == value.lower() and len(value) == 7 and value.startswith("#")


def test_the_mapping_is_read_only() -> None:
    with pytest.raises(TypeError):
        NAMED_COLORS["red"] = "#000000"  # type: ignore[index]


def test_transparent_is_transparent_black() -> None:
    assert parse_color("transparent") == Color(0, 0, 0, 0)
    assert parse_color("TRANSPARENT", strict=True).name == "transparent"


def test_no_keyword_can_be_mistaken_for_a_hash_less_hex_color() -> None:
    assert not any(is_hex_body(name) for name in NAMED_COLORS)


def test_keywords_are_ascii_case_insensitive() -> None:
    assert parse_color("DarkSlateGray") == parse_color("darkslategray")


def test_non_ascii_case_folding_is_not_applied() -> None:
    # U+212A KELVIN SIGN lower-cases to "k" in Unicode, but CSS only folds A-Z.
    with pytest.raises(ColorNameError):
        parse_color("blac" + chr(0x212A))
    # U+0130 LATIN CAPITAL I WITH DOT ABOVE must not fold to "i" either.
    with pytest.raises(ColorNameError):
        parse_color(chr(0x130) + "ndigo")


def test_name_prefers_the_first_keyword_in_spec_order() -> None:
    assert parse_color("cyan").name == "aqua"
    assert parse_color("magenta").name == "fuchsia"
    assert parse_color("grey").name == "gray"


def test_every_keyword_round_trips_through_its_value() -> None:
    for name, value in NAMED_COLORS.items():
        color = parse_color(name)
        assert color.hex == value
        assert color.name is not None
        assert NAMED_COLORS[color.name] == value


def test_unnamed_and_translucent_colors_have_no_name() -> None:
    assert Color(1, 2, 3).name is None
    assert Color(255, 0, 0, 128).name is None


def test_every_keyword_agrees_with_pillow() -> None:
    image_color = pytest.importorskip("PIL.ImageColor")
    for name, value in NAMED_COLORS.items():
        assert image_color.getrgb(name) == parse_color(value).as_tuple()[:3], name
