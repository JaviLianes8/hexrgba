"""Typed errors. Every error is a ``ValueError``, so 0.1.0 handlers keep working."""

from __future__ import annotations


class ColorError(ValueError):
    """Base class for every error this library raises about a color value."""


class HexColorError(ColorError):
    """Raised when a string is not a valid CSS hex color."""


class ChannelError(HexColorError):
    """Raised when a channel or alpha value is outside its range or of the wrong type."""


class ColorNameError(ColorError):
    """Raised when a string is neither a hex color nor a CSS named color keyword."""
