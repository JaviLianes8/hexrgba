"""Parse, validate and normalize CSS hex colors and named colors, with exact alpha,
CSS serialization, WCAG contrast and alpha blending.

>>> from hexrgba import NAMED_COLORS, parse_color
>>> NAMED_COLORS["rebeccapurple"], len(NAMED_COLORS)
('#663399', 148)
>>> parse_color("#ff00ffed").to_css()
'rgba(255, 0, 255, 0.93)'
"""

from ._alpha import alpha_to_byte, css_alpha
from ._blend import blend
from ._color import Color, is_color, parse_color
from ._errors import ChannelError, ColorError, ColorNameError, HexColorError
from ._hex import is_hex, normalize, parse, shorten, to_hex
from ._names import NAMED_COLORS
from ._wcag import contrast_ratio, passes_contrast, relative_luminance

__version__ = "1.0.0"

# The public classes show and pickle as hexrgba.<Name>, so a pickle never depends on the
# private module that defines them. Their methods follow, so doctest finds the examples.
for _cls in (Color, ColorError, HexColorError, ChannelError, ColorNameError):
    _cls.__module__ = __name__
    for _member in vars(_cls).values():
        _function = getattr(_member, "__func__", _member)
        if callable(_function) and str(getattr(_function, "__module__", "")).startswith(
            "hexrgba._"
        ):
            _function.__module__ = __name__
del _cls, _member, _function

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
