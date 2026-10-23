"""Typed errors. Every error is a ``ValueError``, so 0.1.0 handlers keep working."""

from __future__ import annotations


class ColorError(ValueError):
    """Base class for every error this library raises about a color value.

    >>> from hexrgba import ColorError, contrast_ratio
    >>> try:
    ...     contrast_ratio("black", "#ffffff80")
    ... except ColorError as error:
    ...     print(error)
    background must be opaque to measure contrast, got #ffffff80
    """


class HexColorError(ColorError):
    """Raised when a string is not a valid CSS hex color.

    >>> from hexrgba import HexColorError, parse
    >>> try:
    ...     parse("#12345")
    ... except HexColorError as error:
    ...     print(error)
    not a valid hex color: '#12345'
    """


class ChannelError(HexColorError):
    """Raised when a channel or alpha value is outside its range or of the wrong type.

    It subclasses HexColorError because 0.1.0 raised HexColorError for a bad channel in
    ``to_hex``, and handlers written for that keep working.

    >>> from hexrgba import ChannelError, to_hex
    >>> try:
    ...     to_hex(256, 0, 0)
    ... except ChannelError as error:
    ...     print(error)
    r must be from 0 to 255, got 256
    """


class ColorNameError(ColorError):
    """Raised when a string is neither a hex color nor a CSS named color keyword.

    >>> from hexrgba import ColorNameError, parse_color
    >>> try:
    ...     parse_color("reddish")
    ... except ColorNameError as error:
    ...     print(error)
    not a hex color or CSS named color: 'reddish'
    """


_SHOWN_LIMIT = 40
# An int wider than this is described by its size: printing it costs quadratic time and
# beyond 4300 digits Python refuses to print it at all.
_SHOWN_BITS = 128


def shown(value: object) -> str:
    """Return ``repr(value)`` cut to a short prefix, so huge inputs keep messages small.

    It never raises: a huge int is described by its size and an object whose ``repr``
    fails is described by its type.
    """
    if isinstance(value, int) and int.bit_length(value) > _SHOWN_BITS:
        return f"an int of {int.bit_length(value)} bits"
    if isinstance(value, str):
        # Only a prefix is printed, so only a prefix is copied, whatever the input size.
        value = str.__getitem__(value, slice(0, _SHOWN_LIMIT + 1))
    try:
        text = repr(value)
    except Exception:
        return f"a {type_name(value)} object"
    return text if len(text) <= _SHOWN_LIMIT else text[:_SHOWN_LIMIT] + "..."


def type_name(value: object) -> str:
    """Return the name of the type of value, cut like :func:`shown`."""
    name = str(type(value).__name__)
    return name if len(name) <= _SHOWN_LIMIT else name[:_SHOWN_LIMIT] + "..."


def text_argument(value: object, what: str) -> str:
    """Return value as an exact ``str``, or raise TypeError naming ``what``."""
    if not isinstance(value, str):
        raise TypeError(f"{what} must be a str, got {type_name(value)}")
    return str.__str__(value)
