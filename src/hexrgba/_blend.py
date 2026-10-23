"""Alpha compositing of one color over another.

Implements simple alpha compositing (source-over) from Compositing and Blending Level 1,
section 5.1 (https://www.w3.org/TR/compositing-1/#simplealphacompositing):

    co = Cs x as + Cb x ab x (1 - as)      ao = as + ab x (1 - as)      Co = co / ao
"""

from __future__ import annotations

import math
from fractions import Fraction

from ._color import Color, parse_color

_HALF = Fraction(1, 2)


def to_color(value: Color | str) -> Color:
    """Return value unchanged if it is a Color, else parse it leniently."""
    return value if isinstance(value, Color) else parse_color(value)


def composite(
    source: tuple[Fraction, Fraction, Fraction],
    source_alpha: Fraction,
    backdrop: tuple[Fraction, Fraction, Fraction],
    backdrop_alpha: Fraction,
) -> tuple[tuple[Fraction, Fraction, Fraction], Fraction]:
    """Composite exactly on 0..1 values, returning the un-premultiplied color and alpha."""
    out_alpha = source_alpha + backdrop_alpha * (1 - source_alpha)
    if out_alpha == 0:
        zero = Fraction(0)
        return (zero, zero, zero), zero
    channels = tuple(
        (cs * source_alpha + cb * backdrop_alpha * (1 - source_alpha)) / out_alpha
        for cs, cb in zip(source, backdrop, strict=True)
    )
    return (channels[0], channels[1], channels[2]), out_alpha


def _byte(unit: Fraction) -> int:
    return math.floor(unit * 255 + _HALF)


def blend(foreground: Color | str, background: Color | str) -> Color:
    """Composite foreground over background and return the result as a Color.

    The math is exact (fractions); each output channel is rounded to the nearest byte
    once, halves rounding up. An opaque foreground returns itself; a fully transparent
    foreground returns the background. If both are fully transparent the result is
    transparent black. Strings are parsed with :func:`parse_color` (lenient).

    >>> blend("#0000ff80", "red")
    Color(r=127, g=0, b=128, a=255)
    >>> blend("#0000ff80", "#ff000080").hex
    '#5500aac0'
    """
    fg = to_color(foreground)
    bg = to_color(background)
    (r, g, b), alpha = composite(
        (Fraction(fg.r, 255), Fraction(fg.g, 255), Fraction(fg.b, 255)),
        Fraction(fg.a, 255),
        (Fraction(bg.r, 255), Fraction(bg.g, 255), Fraction(bg.b, 255)),
        Fraction(bg.a, 255),
    )
    return Color(_byte(r), _byte(g), _byte(b), _byte(alpha))
