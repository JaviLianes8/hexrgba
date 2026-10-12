"""Simple alpha compositing, checked against the worked examples of Compositing and
Blending Level 1, section 5.1.1 (https://www.w3.org/TR/compositing-1/, fetched 2026-10-12).
"""

from fractions import Fraction as F

from hexrgba import Color, blend
from hexrgba._blend import composite

RED = (F(1), F(0), F(0))
BLUE = (F(0), F(0), F(1))
BLACK = (F(0), F(0), F(0))


def test_spec_example_opaque_shape_over_empty_background() -> None:
    assert composite(RED, F(1), BLACK, F(0)) == (RED, F(1))


def test_spec_example_opaque_over_opaque() -> None:
    assert composite(BLUE, F(1), RED, F(1)) == (BLUE, F(1))


def test_spec_example_half_transparent_over_opaque() -> None:
    assert composite(BLUE, F(1, 2), RED, F(1)) == ((F(1, 2), F(0), F(1, 2)), F(1))


def test_spec_example_half_over_half() -> None:
    (r, g, b), alpha = composite(BLUE, F(1, 2), RED, F(1, 2))
    assert alpha == F(3, 4)
    assert (r * alpha, g * alpha, b * alpha) == (F(1, 4), F(0), F(1, 2))
    # The spec prints the result truncated as RGB(0.33, 0, 0.66).
    assert (r, g, b) == (F(1, 3), F(0), F(2, 3))


def test_both_fully_transparent_gives_transparent_black() -> None:
    assert composite(RED, F(0), BLUE, F(0)) == (BLACK, F(0))
    assert blend("#ff000000", "#0000ff00") == Color(0, 0, 0, 0)


def test_opaque_foreground_wins_and_transparent_foreground_vanishes() -> None:
    assert blend("#123456", "#abcdef80") == Color(0x12, 0x34, 0x56)
    assert blend("#12345600", "#abcdef80") == Color(0xAB, 0xCD, 0xEF, 0x80)


def test_half_blue_over_red_rounds_once_half_up() -> None:
    # alpha 128/255: red keeps 127/255 of 255 = 127, blue gets 128.
    assert blend("#0000ff80", "red") == Color(127, 0, 128)


def test_blend_over_an_opaque_background_is_opaque() -> None:
    for a in range(256):
        assert blend(Color(10, 200, 30, a), Color(250, 5, 99)).a == 255


def test_blend_accepts_color_objects_and_names() -> None:
    assert blend(Color(0, 0, 0, 0), "rebeccapurple") == Color(0x66, 0x33, 0x99)
