"""Hand-written contracts for operand identity, underlying text and private errors."""

from __future__ import annotations

from collections.abc import Callable

import pytest

from hexrgba import Color, HexColorError, blend, parse_color, passes_contrast
from hexrgba._cli import main


class Shade(Color):
    pass


@pytest.mark.parametrize("cls", [Color, Shade])
def test_opaque_blend_returns_a_new_base_color(cls: type[Color]) -> None:
    foreground = cls(1, 2, 3)
    background = Color(255, 255, 255)
    result = blend(foreground, background)
    assert result is not foreground and result is not background
    assert type(result) is Color
    assert result.as_tuple() == (1, 2, 3, 255)


@pytest.mark.parametrize("cls", [Color, Shade])
@pytest.mark.parametrize("alpha", [1, 128, 255])
def test_transparent_blend_returns_a_new_base_color(cls: type[Color], alpha: int) -> None:
    background = cls(1, 2, 3, alpha)
    result = blend("transparent", background)
    assert result is not background
    assert type(result) is Color
    assert result.as_tuple() == (1, 2, 3, alpha)


class MisleadingText(str):
    def __str__(self) -> str:
        return "blue"


class UnprintableText(str):
    def __str__(self) -> str:
        raise AssertionError("string conversion must not run")


@pytest.mark.parametrize("cls", [MisleadingText, UnprintableText])
@pytest.mark.parametrize("parse", [parse_color, Color.parse, Shade.parse])
def test_parsing_uses_underlying_string(cls: type[str], parse: Callable[[str], Color]) -> None:
    assert parse(cls("red")).as_tuple() == (255, 0, 0, 255)
    assert parse(cls("#1234")).as_tuple() == (17, 34, 51, 68)


@pytest.mark.parametrize("cls", [MisleadingText, UnprintableText])
def test_contrast_level_uses_underlying_string(cls: type[str]) -> None:
    assert passes_contrast("#777", "white", level=cls("AA"), large=True)
    assert not passes_contrast("#777", "white", level=cls("AAA"), large=True)


@pytest.mark.parametrize("parse", [parse_color, Color.parse, Shade.parse])
@pytest.mark.parametrize("text", ["abc", "1234", "010203", "12345678"])
def test_strict_hashless_diagnostics_are_input_independent(
    parse: Callable[..., Color], text: str
) -> None:
    with pytest.raises(HexColorError) as caught:
        parse(text, strict=True)
    assert str(caught.value) == "hex color needs a leading '#' in strict mode"
    assert text not in str(caught.value)


@pytest.mark.parametrize("text", ["#010203", "#123456", "#12345678"])
def test_unnamed_cli_color_diagnostics_are_input_independent(
    capsys: pytest.CaptureFixture[str], text: str
) -> None:
    assert main(["convert", text, "--to", "name"]) == 2
    out, err = capsys.readouterr()
    assert out == ""
    assert err == "hexrgba: error: no CSS named color equals the supplied color\n"
    assert text not in err
