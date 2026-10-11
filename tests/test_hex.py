import pytest

from hexrgba import HexColorError, is_hex, normalize, parse, to_hex


@pytest.mark.parametrize(
    "value,expected",
    [
        ("#f00", (255, 0, 0, 255)),
        ("#f008", (255, 0, 0, 136)),
        ("#ff0000", (255, 0, 0, 255)),
        ("#ff000080", (255, 0, 0, 128)),
    ],
)
def test_parse_handles_every_shorthand_form(
    value: str, expected: tuple[int, int, int, int]
) -> None:
    assert parse(value) == expected


def test_parse_accepts_colors_without_a_leading_hash() -> None:
    assert parse("00ff00") == (0, 255, 0, 255)
    assert parse("0f0") == (0, 255, 0, 255)


def test_parse_is_case_insensitive() -> None:
    assert parse("#AABBCC") == parse("#aabbcc")
    assert parse("#ABCD") == parse("#abcd")


def test_shorthand_expands_by_doubling_each_digit() -> None:
    assert parse("#abc") == (170, 187, 204, 255)
    assert parse("#1234") == (17, 34, 51, 68)


def test_missing_alpha_defaults_to_opaque() -> None:
    assert parse("#123456")[3] == 255


def test_surrounding_whitespace_is_ignored() -> None:
    assert parse("  #ff0000  ") == (255, 0, 0, 255)


def test_is_hex_accepts_valid_colors() -> None:
    assert is_hex("#fff")
    assert is_hex("1234")
    assert is_hex("#AABBCCDD")


@pytest.mark.parametrize("value", ["", "#", "#ff", "#fffff", "ggg", "#12345", "red", "#ff00gg"])
def test_is_hex_rejects_invalid_colors(value: str) -> None:
    assert not is_hex(value)


@pytest.mark.parametrize("value", ["", "#", "#ff", "nothex", "#12345", "#ff00zz"])
def test_parse_raises_on_invalid_input(value: str) -> None:
    with pytest.raises(HexColorError):
        parse(value)


def test_to_hex_without_alpha_is_six_digits() -> None:
    assert to_hex(255, 0, 128) == "#ff0080"


def test_to_hex_with_alpha_is_eight_digits() -> None:
    assert to_hex(255, 0, 128, 64) == "#ff008040"


def test_to_hex_rejects_out_of_range_channels() -> None:
    with pytest.raises(HexColorError):
        to_hex(256, 0, 0)
    with pytest.raises(HexColorError):
        to_hex(0, -1, 0)


def test_to_hex_rejects_booleans() -> None:
    with pytest.raises(HexColorError):
        to_hex(True, 0, 0)


def test_normalize_drops_alpha_when_opaque() -> None:
    assert normalize("#FF0000FF") == "#ff0000"
    assert normalize("#F00") == "#ff0000"


def test_normalize_keeps_alpha_when_translucent() -> None:
    assert normalize("#ff000080") == "#ff000080"
    assert normalize("#f008") == "#ff000088"


@pytest.mark.parametrize(
    "channels",
    [(0, 0, 0, 0), (255, 255, 255, 255), (12, 34, 56, 78), (255, 0, 128, 255)],
)
def test_round_trip_parse_to_hex(channels: tuple[int, int, int, int]) -> None:
    assert parse(to_hex(*channels)) == channels


def test_round_trip_without_alpha_is_opaque() -> None:
    assert parse(to_hex(10, 20, 30)) == (10, 20, 30, 255)
