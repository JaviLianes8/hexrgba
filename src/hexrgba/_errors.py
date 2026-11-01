"""Typed errors. Every error is a ``ValueError``, so 0.1.0 handlers keep working."""

from __future__ import annotations

from typing import cast


class ColorError(ValueError):
    """Base class for every error this library raises about a color value.

    >>> from hexrgba import ColorError, contrast_ratio
    >>> try:
    ...     contrast_ratio("black", "#ffffff80")
    ... except ColorError as error:
    ...     print(error)
    background must be opaque to measure contrast
    """


class HexColorError(ColorError):
    """Raised when a string is not a valid CSS hex color.

    >>> from hexrgba import HexColorError, parse
    >>> try:
    ...     parse("#12345")
    ... except HexColorError as error:
    ...     print(error)
    not a valid hex color; expected 3, 4, 6 or 8 ASCII hex digits
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
    r must be from 0 to 255
    """


class ColorNameError(ColorError):
    """Raised when a string is neither a hex color nor a CSS named color keyword.

    >>> from hexrgba import ColorNameError, parse_color
    >>> try:
    ...     parse_color("reddish")
    ... except ColorNameError as error:
    ...     print(error)
    not a hex color or CSS named color
    """


def text_argument(value: object, what: str) -> str:
    """Return value as an exact str, or raise TypeError without inspecting its contents."""
    if not issubclass(type(value), str):
        raise TypeError(f"{what} must be a str")
    return str.__str__(cast(str, value))
