"""WCAG 2.x relative luminance, contrast ratio and the AA / AAA text thresholds.

Formulas from the WCAG 2.2 definitions (W3C Recommendation, 12 December 2024):
https://www.w3.org/TR/WCAG22/#dfn-relative-luminance and
https://www.w3.org/TR/WCAG22/#dfn-contrast-ratio. Thresholds from success criteria
1.4.3 (https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum) and 1.4.6
(https://www.w3.org/WAI/WCAG22/Understanding/contrast-enhanced).
"""

from __future__ import annotations

from ._blend import blend, to_color
from ._color import Color
from ._errors import ColorError, shown, type_name

# (level, large text) -> minimum ratio. Compared without rounding, as WCAG requires.
_THRESHOLDS = {("AA", False): 4.5, ("AA", True): 3.0, ("AAA", False): 7.0, ("AAA", True): 4.5}


def _linear(byte: int) -> float:
    srgb = byte / 255
    return srgb / 12.92 if srgb <= 0.04045 else ((srgb + 0.055) / 1.055) ** 2.4


def relative_luminance(color: Color | str) -> float:
    """Return the WCAG relative luminance, 0.0 for black to 1.0 for white.

    ``L = 0.2126 * R + 0.7152 * G + 0.0722 * B`` on linearized sRGB channels, with the
    0.04045 threshold of the current definition. Alpha is ignored: composite a
    translucent color first with :func:`blend`.

    >>> relative_luminance("black"), relative_luminance("white")
    (0.0, 1.0)
    >>> round(relative_luminance("#767676"), 4)
    0.1812
    """
    c = to_color(color)
    return 0.2126 * _linear(c.r) + 0.7152 * _linear(c.g) + 0.0722 * _linear(c.b)


def contrast_ratio(foreground: Color | str, background: Color | str) -> float:
    """Return the WCAG contrast ratio ``(L1 + 0.05) / (L2 + 0.05)``, from 1.0 to 21.0.

    L1 is the lighter luminance, so the order of two opaque colors does not matter. A
    translucent foreground is first composited over the background with :func:`blend`
    and rounded to 8-bit channels, as a browser paints it.
    The background must be opaque, since what lies behind it is unknown: a translucent
    background raises ColorError.

    >>> contrast_ratio("black", "white")
    21.0
    >>> round(contrast_ratio("#767676", "white"), 2)
    4.54
    """
    bg = to_color(background)
    if not bg.is_opaque:
        raise ColorError(f"background must be opaque to measure contrast, got {bg.hex}")
    fg = blend(foreground, bg)
    first, second = relative_luminance(fg), relative_luminance(bg)
    lighter, darker = max(first, second), min(first, second)
    return (lighter + 0.05) / (darker + 0.05)


def passes_contrast(
    foreground: Color | str,
    background: Color | str,
    *,
    level: str = "AA",
    large: bool = False,
) -> bool:
    """Report whether the pair meets WCAG text contrast at ``level`` "AA" or "AAA".

    The minimum ratios are 4.5 (AA), 3 (AA, large text), 7 (AAA) and 4.5 (AAA, large
    text). ``level`` is case-insensitive. The ratio is not rounded first, so 4.499 fails
    4.5. Raises ValueError for an unknown level and TypeError when ``level`` is not a str
    or ``large`` is not a bool.

    >>> passes_contrast("#767676", "white"), passes_contrast("#777777", "white")
    (True, False)
    >>> passes_contrast("#777777", "white", large=True)
    True
    """
    if not isinstance(level, str):
        raise TypeError(f"level must be a str, got {type_name(level)}")
    if not isinstance(large, bool):
        raise TypeError(f"large must be a bool, got {type_name(large)}")
    key = (str.upper(level), large)
    if key not in _THRESHOLDS:
        raise ValueError(f"level must be 'AA' or 'AAA' in any case, got {shown(level)}")
    return contrast_ratio(foreground, background) >= _THRESHOLDS[key]
