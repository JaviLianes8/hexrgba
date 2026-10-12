"""Exact conversions between an 8-bit alpha byte and the 0..1 alpha of CSS.

The serialization follows CSS Color Module Level 4, section 16.1.1 "Serializing legacy
alpha values" (https://www.w3.org/TR/css-color-4/#serializing-alpha-values).
"""

from __future__ import annotations

import math
from fractions import Fraction

from ._errors import ChannelError
from ._hex import check_channel


def alpha_to_byte(alpha: float) -> int:
    """Convert a 0..1 alpha into an alpha byte from 0 to 255.

    The value is multiplied by 255 and rounded to the nearest integer, halves rounding
    up, using the exact value of the float (no binary rounding drift). Both ``a / 255``
    and the string from :func:`css_alpha` convert back to the byte ``a`` they came from,
    for every ``a`` from 0 to 255.

    Raises ChannelError for booleans, non-numbers, NaN and values outside 0..1.
    """
    if isinstance(alpha, bool) or not isinstance(alpha, (int, float)):
        raise ChannelError(f"alpha must be a number from 0 to 1, got {alpha!r}")
    if not 0 <= alpha <= 1:
        raise ChannelError(f"alpha must be from 0 to 1, got {alpha!r}")
    return math.floor(Fraction(alpha) * 255 + Fraction(1, 2))


def css_alpha(byte: int) -> str:
    """Serialize an alpha byte as the CSS legacy alpha number, for example "0.5".

    If a whole percentage ``n`` (0 to 100) satisfies ``round(n * 2.55) == byte`` the
    result is ``n / 100``, so 237 gives "0.93". Otherwise it is ``byte / 0.255`` rounded
    to an integer and divided by 1000, so 236 gives "0.925". Halves round up, there is
    always a leading zero and trailing zeros are dropped; 255 gives "1" and 0 gives "0".
    """
    check_channel(byte, "alpha")
    for percent in range(101):
        if (percent * 255 + 50) // 100 == byte:
            return _decimal(percent, 100)
    return _decimal((byte * 2000 + 255) // 510, 1000)


def _decimal(numerator: int, denominator: int) -> str:
    """Render numerator / denominator (denominator 100 or 1000) without trailing zeros."""
    whole, rest = divmod(numerator, denominator)
    if rest == 0:
        return str(whole)
    width = len(str(denominator)) - 1
    return f"{whole}.{rest:0{width}d}".rstrip("0")
