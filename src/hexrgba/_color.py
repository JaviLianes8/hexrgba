"""The frozen ``Color`` value type and CSS color parsing (hex and named keywords)."""

from __future__ import annotations

from dataclasses import dataclass

from ._alpha import alpha_to_byte, css_alpha
from ._errors import ColorNameError, HexColorError, shown
from ._hex import check_channel, decode, is_hex_body, shorten, to_hex
from ._names import NAMED_COLORS

# CSS keywords are ASCII case-insensitive: only A-Z fold, so look-alikes such as
# the Kelvin sign (U+212A) never match "k" the way str.lower() would make them.
_ASCII_LOWER = str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz")
_NAME_BY_HEX: dict[str, str] = {}
for _name, _value in NAMED_COLORS.items():
    _NAME_BY_HEX.setdefault(_value, _name)


@dataclass(frozen=True, slots=True)
class Color:
    """An sRGB color with integer channels ``r``, ``g``, ``b`` and alpha ``a``, 0 to 255.

    Instances are immutable, hashable and compare by value. ``a`` defaults to 255
    (fully opaque). Construction raises ChannelError for any channel that is not an int
    from 0 to 255.
    """

    r: int
    g: int
    b: int
    a: int = 255

    def __post_init__(self) -> None:
        for name in ("r", "g", "b", "a"):
            check_channel(getattr(self, name), name)

    @classmethod
    def parse(cls, text: str, *, strict: bool = False) -> Color:
        """Parse a hex color or CSS named color; see :func:`parse_color`."""
        return parse_color(text, strict=strict)

    @classmethod
    def from_rgba(cls, r: int, g: int, b: int, alpha: float = 1.0) -> Color:
        """Build a color from byte channels and a 0..1 alpha (see :func:`alpha_to_byte`)."""
        return cls(r, g, b, alpha_to_byte(alpha))

    @property
    def alpha(self) -> float:
        """The alpha as a float from 0 to 1, exactly ``a / 255``."""
        return self.a / 255

    @property
    def is_opaque(self) -> bool:
        """True when the alpha byte is 255."""
        return self.a == 255

    @property
    def hex(self) -> str:
        """Canonical lower-case hex: #rrggbb when opaque, #rrggbbaa otherwise."""
        if self.is_opaque:
            return to_hex(self.r, self.g, self.b)
        return to_hex(self.r, self.g, self.b, self.a)

    @property
    def name(self) -> str | None:
        """The CSS keyword for this exact color, or None.

        ``transparent`` names (0, 0, 0, 0). When two keywords share a value (``aqua`` and
        ``cyan``, ``gray`` and ``grey``) the first in the spec's alphabetical table wins.
        """
        if self == _TRANSPARENT:
            return "transparent"
        return _NAME_BY_HEX.get(self.hex) if self.is_opaque else None

    def to_hex(self, *, short: bool = False) -> str:
        """Return :attr:`hex`, or the lossless #rgb / #rgba form when ``short=True``."""
        return shorten(self.hex) if short else self.hex

    def to_css(self) -> str:
        """Serialize as CSS does for sRGB values: ``rgb(r, g, b)`` when opaque, otherwise
        ``rgba(r, g, b, alpha)`` with the alpha from :func:`css_alpha`."""
        if self.is_opaque:
            return f"rgb({self.r}, {self.g}, {self.b})"
        return f"rgba({self.r}, {self.g}, {self.b}, {css_alpha(self.a)})"

    def with_alpha(self, alpha: float) -> Color:
        """Return a copy with a 0..1 alpha, converted by :func:`alpha_to_byte`."""
        return Color(self.r, self.g, self.b, alpha_to_byte(alpha))

    def as_tuple(self) -> tuple[int, int, int, int]:
        """Return ``(r, g, b, a)``, the same shape :func:`parse` returns."""
        return (self.r, self.g, self.b, self.a)

    def __str__(self) -> str:
        return self.hex


_TRANSPARENT = Color(0, 0, 0, 0)


def parse_color(text: str, *, strict: bool = False) -> Color:
    """Parse a CSS hex color (#rgb, #rgba, #rrggbb, #rrggbbaa), a named color or
    ``transparent`` into a :class:`Color`.

    Hex digits and keywords are matched ASCII case-insensitively, as CSS requires.
    ``strict=True`` follows the CSS grammar exactly: hex needs its leading ``#`` and no
    surrounding whitespace is allowed. The default lenient mode also accepts a missing
    ``#`` and strips surrounding whitespace, like :func:`parse`.

    Raises HexColorError for a malformed hex color, ColorNameError for an unknown
    keyword and TypeError when text is not a str.
    """
    if not isinstance(text, str):
        raise TypeError(f"color must be a str, got {type(text).__name__}")
    body = text.strip()
    if strict and body != text:
        error = HexColorError if body.startswith("#") else ColorNameError
        raise error(f"surrounding whitespace is not allowed in strict mode: {shown(text)}")
    if body.startswith("#"):
        return Color(*decode(body[1:], text))
    key = body.translate(_ASCII_LOWER)
    if key == "transparent":
        return _TRANSPARENT
    value = NAMED_COLORS.get(key)
    if value is not None:
        return Color(*decode(value[1:], text))
    if is_hex_body(body):
        if strict:
            raise HexColorError(f"hex color needs a leading '#' in strict mode: {shown(text)}")
        return Color(*decode(body, text))
    raise ColorNameError(f"not a hex color or CSS named color: {shown(text)}")


def is_color(text: str, *, strict: bool = False) -> bool:
    """Report whether :func:`parse_color` accepts text with the same ``strict`` setting."""
    try:
        parse_color(text, strict=strict)
    except (ValueError, TypeError):
        return False
    return True
