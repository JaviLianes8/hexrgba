"""Parse, validate and normalize CSS hex colors and named colors, with exact alpha,
CSS serialization, WCAG contrast and alpha blending."""

from __future__ import annotations

from ._alpha import alpha_to_byte, css_alpha
from ._blend import blend
from ._color import Color, is_color, parse_color
from ._errors import ChannelError, ColorError, ColorNameError, HexColorError
from ._hex import is_hex, normalize, parse, shorten, to_hex
from ._names import NAMED_COLORS
from ._wcag import contrast_ratio, passes_contrast, relative_luminance

__version__ = "0.2.0"

__all__ = [
    "NAMED_COLORS",
    "ChannelError",
    "Color",
    "ColorError",
    "ColorNameError",
    "HexColorError",
    "alpha_to_byte",
    "blend",
    "contrast_ratio",
    "css_alpha",
    "is_color",
    "is_hex",
    "normalize",
    "parse",
    "parse_color",
    "passes_contrast",
    "relative_luminance",
    "shorten",
    "to_hex",
]
