"""The frozen Color type and strict versus lenient parsing."""

import dataclasses

import pytest

from hexrgba import (
    ChannelError,
    Color,
    ColorError,
    ColorNameError,
    HexColorError,
    is_color,
    parse,
    parse_color,
)


def test_color_defaults_to_opaque() -> None:
    assert Color(1, 2, 3).a == 255


def test_color_is_frozen_hashable_and_compares_by_value() -> None:
    color = Color(1, 2, 3, 4)
    with pytest.raises(dataclasses.FrozenInstanceError):
        color.r = 9  # type: ignore[misc]
    assert {color, Color(1, 2, 3, 4)} == {color}


@pytest.mark.parametrize("channels", [(256, 0, 0), (0, -1, 0), (0, 0, 1.0), (True, 0, 0)])
def test_color_rejects_bad_channels(channels: tuple[int, int, int]) -> None:
    with pytest.raises(ChannelError):
        Color(*channels)


def test_error_hierarchy_keeps_value_error() -> None:
    assert issubclass(ColorError, ValueError)
    assert issubclass(HexColorError, ColorError)
    assert issubclass(ChannelError, HexColorError)
    assert issubclass(ColorNameError, ColorError)


def test_hex_and_short_forms() -> None:
    assert Color(170, 187, 204).hex == "#aabbcc"
    assert Color(170, 187, 204).to_hex(short=True) == "#abc"
    assert Color(170, 187, 204, 221).to_hex(short=True) == "#abcd"
    assert Color(170, 187, 205).to_hex(short=True) == "#aabbcd"
    assert str(Color(255, 0, 0, 128)) == "#ff000080"


def test_to_css_uses_rgb_when_opaque_and_rgba_otherwise() -> None:
    assert Color(1, 2, 3).to_css() == "rgb(1, 2, 3)"
    assert Color(1, 2, 3, 0).to_css() == "rgba(1, 2, 3, 0)"


def test_alpha_float_is_exact_byte_over_255() -> None:
    assert Color(0, 0, 0, 51).alpha == 51 / 255
    assert Color.from_rgba(0, 0, 0, Color(0, 0, 0, 51).alpha).a == 51


def test_from_rgba_and_with_alpha_convert_the_float() -> None:
    assert Color.from_rgba(255, 0, 0, 0.5) == Color(255, 0, 0, 128)
    assert Color.from_rgba(255, 0, 0) == Color(255, 0, 0)
    assert Color(9, 9, 9).with_alpha(0) == Color(9, 9, 9, 0)


def test_as_tuple_matches_parse() -> None:
    assert parse_color("#12345678").as_tuple() == parse("#12345678")


def test_lenient_mode_takes_missing_hash_whitespace_and_case() -> None:
    assert parse_color("  FFAA00 ") == Color(255, 170, 0)
    assert parse_color(" Red\t") == Color(255, 0, 0)


def test_strict_mode_follows_the_css_grammar() -> None:
    assert parse_color("#FFAA00", strict=True) == Color(255, 170, 0)
    assert parse_color("RED", strict=True) == Color(255, 0, 0)
    with pytest.raises(HexColorError, match="leading '#'"):
        parse_color("ffaa00", strict=True)
    with pytest.raises(HexColorError, match="whitespace"):
        parse_color(" #ffaa00", strict=True)
    with pytest.raises(ColorNameError, match="whitespace"):
        parse_color("red ", strict=True)


@pytest.mark.parametrize("text", ["", "#", "#12345", "notacolor", "# fff", "#" + chr(0xFF11) * 3])
def test_parse_color_rejects_garbage(text: str) -> None:
    with pytest.raises(ColorError):
        parse_color(text)
    assert not is_color(text)


def test_error_types_name_the_failing_family() -> None:
    with pytest.raises(HexColorError):
        parse_color("#ggg")
    with pytest.raises(ColorNameError):
        parse_color("reddish")


def test_parse_color_rejects_non_strings() -> None:
    with pytest.raises(TypeError):
        parse_color(123)  # type: ignore[arg-type]
    assert not is_color(None)


def test_color_parse_is_parse_color() -> None:
    assert Color.parse("#abc", strict=True) == parse_color("#abc")
