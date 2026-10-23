"""Hostile input: wrong types, subclasses that lie, huge values and huge strings."""

from __future__ import annotations

import time
from collections.abc import Callable

import pytest

from hexrgba import (
    ChannelError,
    Color,
    ColorError,
    alpha_to_byte,
    blend,
    contrast_ratio,
    css_alpha,
    is_color,
    is_hex,
    normalize,
    parse,
    parse_color,
    passes_contrast,
    relative_luminance,
    shorten,
    to_hex,
)

NOT_TEXT = [None, 5, 1.5, b"#fff", bytearray(b"red"), ["#fff"], object()]


@pytest.mark.parametrize("value", NOT_TEXT)
def test_predicates_say_false_for_anything_but_a_str(value: object) -> None:
    assert is_hex(value) is False
    assert is_color(value) is False and is_color(value, strict=True) is False


@pytest.mark.parametrize("value", NOT_TEXT)
@pytest.mark.parametrize("function", [parse, normalize, shorten, parse_color, Color.parse])
def test_parsers_raise_type_error_for_anything_but_a_str(
    function: Callable[[str], object], value: object
) -> None:
    with pytest.raises(TypeError, match=r"^color must be a str, got [A-Za-z]+$"):
        function(value)  # type: ignore[arg-type]


class Lying(int):
    def __format__(self, spec: str) -> str:
        return "zz"

    def __int__(self) -> int:
        return 300

    def __index__(self) -> int:
        return 300


class LyingFloat(float):
    def __le__(self, other: object) -> bool:
        return True

    def __ge__(self, other: object) -> bool:
        return True

    def __float__(self) -> float:
        return 0.0


class LyingStr(str):
    __slots__ = ()

    def strip(self, chars: str | None = None) -> str:
        return "red"


def test_int_subclasses_are_read_as_the_int_they_are() -> None:
    color = Color(Lying(18), Lying(52), Lying(86), Lying(120))
    assert color.hex == "#12345678" and type(color.r) is int and type(color.a) is int
    assert to_hex(Lying(255), 0, 0) == "#ff0000" and css_alpha(Lying(128)) == "0.5"
    assert alpha_to_byte(Lying(1)) == 255 and Color(1, 2, 3) == Color(Lying(1), 2, 3)


def test_float_subclasses_are_read_as_the_float_they_are() -> None:
    assert alpha_to_byte(LyingFloat(0.5)) == 128
    with pytest.raises(ChannelError):
        alpha_to_byte(LyingFloat(7.5))


def test_str_subclasses_are_read_as_the_text_they_are() -> None:
    assert parse_color(LyingStr("#00f")) == Color(0, 0, 255)
    assert parse(LyingStr(" #00f ")) == (0, 0, 255, 255)
    with pytest.raises(ColorError):
        parse_color(LyingStr("nonsense"))


class Unprintable:
    def __repr__(self) -> str:
        raise RuntimeError("no repr")


@pytest.mark.parametrize(
    "call",
    [
        lambda: Color(10**5000, 0, 0),
        lambda: Color(0, 0, -(10**5000)),
        lambda: to_hex(0, 0, 0, 2**200),
        lambda: css_alpha(-(2**129)),
        lambda: alpha_to_byte(10**5000),
        lambda: Color(Unprintable(), 0, 0),  # type: ignore[arg-type]
        lambda: alpha_to_byte(Unprintable()),  # type: ignore[arg-type]
        lambda: Color.from_rgba(0, 0, 0, float("nan")),
    ],
)
def test_channel_errors_stay_channel_errors_with_short_messages(call: Callable[[], object]) -> None:
    with pytest.raises(ChannelError) as caught:
        call()
    assert len(str(caught.value)) < 120


def test_huge_ints_are_described_by_their_size() -> None:
    with pytest.raises(ChannelError, match=r"got an int of 16610 bits$"):
        Color(10**5000, 0, 0)
    with pytest.raises(ChannelError, match=r"got a Unprintable object$"):
        alpha_to_byte(Unprintable())  # type: ignore[arg-type]


HUGE = "#" + "f" * 1_000_000


@pytest.mark.parametrize(
    "call",
    [
        lambda: parse(HUGE),
        lambda: normalize("z" * 1_000_000),
        lambda: parse_color(HUGE),
        lambda: parse_color(" " + HUGE, strict=True),
        lambda: parse_color(HUGE[1:], strict=True),
        lambda: parse_color("q" * 1_000_000),
        lambda: blend(HUGE, "red"),
        lambda: contrast_ratio("red", HUGE),
        lambda: relative_luminance(HUGE),
        lambda: passes_contrast("red", "blue", level="A" * 1_000_000),
    ],
)
def test_huge_input_gives_a_short_message(call: Callable[[], object]) -> None:
    with pytest.raises(ValueError) as caught:
        call()
    assert len(str(caught.value)) < 120 and "..." in str(caught.value)


def test_passes_contrast_checks_its_options() -> None:
    with pytest.raises(TypeError, match="level must be a str, got NoneType"):
        passes_contrast("red", "blue", level=None)  # type: ignore[arg-type]
    for large in ("yes", 1, None):
        with pytest.raises(TypeError, match="large must be a bool"):
            passes_contrast("red", "blue", large=large)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match=r"^level must be 'AA' or 'AAA' in any case, got 'A'$"):
        passes_contrast("red", "blue", level="A")


def _seconds(call: Callable[[], object]) -> float:
    best = float("inf")
    for _ in range(3):
        start = time.perf_counter()
        call()
        best = min(best, time.perf_counter() - start)
    return best


@pytest.mark.parametrize(
    "shape",
    [lambda n: " " * n, lambda n: "#" + "f" * n, lambda n: "a" * n, lambda n: " red" + " " * n],
)
def test_parsing_time_grows_linearly(shape: Callable[[int], str]) -> None:
    small, large = shape(250_000), shape(1_000_000)
    for check in (is_color, is_hex):
        slow = _seconds(lambda check=check: check(large))  # type: ignore[misc]
        assert slow < 12 * _seconds(lambda check=check: check(small)) + 0.05  # type: ignore[misc]
