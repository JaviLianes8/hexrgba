"""Typed errors. Every error is a ``ValueError``, so 0.1.0 handlers keep working."""

from __future__ import annotations


class ColorError(ValueError):
    """Base class for every error this library raises about a color value."""


class HexColorError(ColorError):
    """Raised when a string is not a valid CSS hex color."""


class ChannelError(HexColorError):
    """Raised when a channel or alpha value is outside its range or of the wrong type.

    It subclasses HexColorError because 0.1.0 raised HexColorError for a bad channel in
    ``to_hex``, and handlers written for that keep working.
    """


_SHOWN_LIMIT = 40


def shown(value: object) -> str:
    """Return ``repr(value)`` cut to a short prefix, so huge inputs keep messages small."""
    text = repr(value)
    return text if len(text) <= _SHOWN_LIMIT else text[:_SHOWN_LIMIT] + "..."


class ColorNameError(ColorError):
    """Raised when a string is neither a hex color nor a CSS named color keyword."""
