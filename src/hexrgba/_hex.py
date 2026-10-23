"""Core parsing, validation and normalization for CSS hex colors."""

from __future__ import annotations

from ._errors import ChannelError, HexColorError, shown, text_argument

_VALID_LENGTHS = frozenset({3, 4, 6, 8})
_HEX_DIGITS = frozenset("0123456789abcdefABCDEF")


def _body(value: object) -> str:
    text = text_argument(value, "color").strip()
    return text[1:] if text.startswith("#") else text


def is_hex_body(body: str) -> bool:
    """Report whether body (no hash) has 3, 4, 6 or 8 ASCII hex digits."""
    return len(body) in _VALID_LENGTHS and all(ch in _HEX_DIGITS for ch in body)


def decode(body: str, original: str) -> tuple[int, int, int, int]:
    """Decode a hash-less hex body into channels, naming original in the error."""
    if not is_hex_body(body):
        raise HexColorError(f"not a valid hex color: {shown(original)}")
    if len(body) in (3, 4):
        body = "".join(ch * 2 for ch in body)
    r = int(body[0:2], 16)
    g = int(body[2:4], 16)
    b = int(body[4:6], 16)
    a = int(body[6:8], 16) if len(body) == 8 else 255
    return r, g, b, a


def is_hex(value: object) -> bool:
    """Report whether value is a hex color in #rgb, #rgba, #rrggbb or #rrggbbaa form.

    The leading ``#`` is optional and surrounding whitespace is ignored, as in
    :func:`parse`. It never raises: anything that is not a str gives False.

    >>> is_hex("#f00"), is_hex("ff000080"), is_hex("#12345"), is_hex(None)
    (True, True, False, False)
    """
    return isinstance(value, str) and is_hex_body(_body(value))


def parse(value: str) -> tuple[int, int, int, int]:
    """Parse a hex color into (r, g, b, a) channels as integers from 0 to 255.

    Shorthand (#rgb, #rgba) is expanded by doubling each digit, the leading hash is
    optional, surrounding whitespace is ignored and a missing alpha channel defaults to
    255 (fully opaque). Raises HexColorError for anything else and TypeError when value
    is not a str.

    >>> parse("#ff000080")
    (255, 0, 0, 128)
    >>> parse("abc")
    (170, 187, 204, 255)
    """
    return decode(_body(value), value)


def check_channel(value: int, name: str) -> int:
    """Return value as a plain int if it is an int from 0 to 255, else raise ChannelError."""
    if not isinstance(value, int) or isinstance(value, bool):
        raise ChannelError(f"{name} must be an int from 0 to 255, got {shown(value)}")
    # An int subclass is read through int itself, so its own methods cannot change it.
    plain = int.__int__(value)
    if not 0 <= plain <= 255:
        raise ChannelError(f"{name} must be from 0 to 255, got {shown(plain)}")
    return plain


def _channel(value: int, name: str) -> str:
    return f"{check_channel(value, name):02x}"


def to_hex(r: int, g: int, b: int, a: int | None = None) -> str:
    """Build a canonical lower-case hex string from channels.

    With no alpha the result is #rrggbb, with alpha it is #rrggbbaa (even for 255).
    Raises ChannelError for a channel that is not an int from 0 to 255.

    >>> to_hex(255, 0, 128)
    '#ff0080'
    >>> to_hex(255, 0, 128, 64)
    '#ff008040'
    """
    out = "#" + _channel(r, "r") + _channel(g, "g") + _channel(b, "b")
    if a is not None:
        out += _channel(a, "a")
    return out


def shorten(value: str) -> str:
    """Return the shortest lossless form of a hex color: #rgb or #rgba when every pair
    repeats its digit, otherwise the canonical #rrggbb or #rrggbbaa from normalize.

    >>> shorten("#AABBCC"), shorten("#aabbccdd"), shorten("#aabbcd")
    ('#abc', '#abcd', '#aabbcd')
    """
    full = normalize(value)
    pairs = [full[i : i + 2] for i in range(1, len(full), 2)]
    if all(pair[0] == pair[1] for pair in pairs):
        return "#" + "".join(pair[0] for pair in pairs)
    return full


def normalize(value: str, *, short: bool = False) -> str:
    """Return the canonical form: #rrggbb when fully opaque, #rrggbbaa otherwise.

    With ``short=True`` the result is shortened to #rgb or #rgba when that is lossless.
    Raises HexColorError like :func:`parse`.

    >>> normalize("#F00"), normalize("#FF0000FF"), normalize("#f008")
    ('#ff0000', '#ff0000', '#ff000088')
    >>> normalize("#AABBCC", short=True)
    '#abc'
    """
    r, g, b, a = parse(value)
    full = to_hex(r, g, b) if a == 255 else to_hex(r, g, b, a)
    return shorten(full) if short else full
