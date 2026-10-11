"""Core parsing, validation and normalization for CSS hex colors."""

from __future__ import annotations

_VALID_LENGTHS = frozenset({3, 4, 6, 8})
_HEX_DIGITS = frozenset("0123456789abcdefABCDEF")


class HexColorError(ValueError):
    """Raised when a string is not a valid CSS hex color."""


def _body(value: str) -> str:
    text = value.strip()
    return text[1:] if text.startswith("#") else text


def is_hex(value: str) -> bool:
    """Report whether value is a hex color in #rgb, #rgba, #rrggbb or #rrggbbaa form."""
    body = _body(value)
    return len(body) in _VALID_LENGTHS and all(ch in _HEX_DIGITS for ch in body)


def parse(value: str) -> tuple[int, int, int, int]:
    """Parse a hex color into (r, g, b, a) channels as integers from 0 to 255.

    Shorthand (#rgb, #rgba) is expanded by doubling each digit, the leading hash is
    optional, and a missing alpha channel defaults to 255 (fully opaque).
    """
    body = _body(value)
    if len(body) not in _VALID_LENGTHS or any(ch not in _HEX_DIGITS for ch in body):
        raise HexColorError(f"not a valid hex color: {value!r}")
    if len(body) in (3, 4):
        body = "".join(ch * 2 for ch in body)
    r = int(body[0:2], 16)
    g = int(body[2:4], 16)
    b = int(body[4:6], 16)
    a = int(body[6:8], 16) if len(body) == 8 else 255
    return r, g, b, a


def _channel(value: int, name: str) -> str:
    if not isinstance(value, int) or isinstance(value, bool):
        raise HexColorError(f"{name} must be an int from 0 to 255, got {value!r}")
    if not 0 <= value <= 255:
        raise HexColorError(f"{name} must be from 0 to 255, got {value}")
    return f"{value:02x}"


def to_hex(r: int, g: int, b: int, a: int | None = None) -> str:
    """Build a canonical lowercase hex string from channels.

    With no alpha the result is #rrggbb, with alpha it is #rrggbbaa.
    """
    out = "#" + _channel(r, "r") + _channel(g, "g") + _channel(b, "b")
    if a is not None:
        out += _channel(a, "a")
    return out


def normalize(value: str) -> str:
    """Return the canonical form: #rrggbb when fully opaque, #rrggbbaa otherwise."""
    r, g, b, a = parse(value)
    return to_hex(r, g, b) if a == 255 else to_hex(r, g, b, a)
