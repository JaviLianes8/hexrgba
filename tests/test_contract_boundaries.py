"""Hand-written formatting, strict parsing and luminance boundary contracts."""

from __future__ import annotations

import pytest

from hexrgba import Color, HexColorError, relative_luminance, to_hex


class Shade(Color):
    pass


def test_explicit_opaque_alpha_is_retained() -> None:
    assert to_hex(1, 2, 3) == "#010203"
    assert to_hex(1, 2, 3, 255) == "#010203ff"


@pytest.mark.parametrize("cls", [Color, Shade])
@pytest.mark.parametrize("text", ["abc", " #abc", "#abc ", "\t#abc\n"])
def test_color_parse_forwards_strict_mode(cls: type[Color], text: str) -> None:
    with pytest.raises(HexColorError):
        cls.parse(text, strict=True)
    result = cls.parse(text)
    assert type(result) is cls
    assert result.as_tuple() == (170, 187, 204, 255)


@pytest.mark.parametrize("rgb", [(255, 0, 0), (0, 255, 0), (0, 0, 255), (18, 52, 86)])
@pytest.mark.parametrize("alpha", [0, 1, 128, 254, 255])
def test_relative_luminance_ignores_alpha(rgb: tuple[int, int, int], alpha: int) -> None:
    opaque = relative_luminance(Color(*rgb))
    translucent = Color(*rgb, alpha)
    assert relative_luminance(translucent) == opaque
    assert relative_luminance(translucent.hex) == opaque
