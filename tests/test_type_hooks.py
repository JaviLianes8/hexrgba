"""Hand-written contracts for type checks without instance dispatch."""

from __future__ import annotations

from collections.abc import Callable

import pytest

from hexrgba import (
    ChannelError,
    Color,
    alpha_to_byte,
    blend,
    css_alpha,
    is_color,
    is_hex,
    parse_color,
    passes_contrast,
    relative_luminance,
)


class ClassHook:
    def __getattribute__(self, name: str) -> object:
        if name == "__class__":
            raise RuntimeError("class hook ran")
        return object.__getattribute__(self, name)


class HookInt(ClassHook, int):
    pass


class HookFloat(ClassHook, float):
    pass


class HookStr(ClassHook, str):
    pass


def test_predicates_do_not_consult_class_hooks() -> None:
    assert is_hex(ClassHook()) is False
    assert is_color(ClassHook()) is False
    assert is_hex(HookStr("#fff")) is True
    assert is_color(HookStr("red")) is True


def test_numeric_subclasses_do_not_consult_class_hooks() -> None:
    assert alpha_to_byte(HookInt(1)) == 255
    assert alpha_to_byte(HookFloat(0.5)) == 128
    assert css_alpha(HookInt(255)) == "1"
    assert Color(HookInt(1), 2, 3).r == 1


@pytest.mark.parametrize("function", [parse_color, relative_luminance])
def test_wrong_color_types_raise_type_error_without_class_hooks(
    function: Callable[[str], object],
) -> None:
    with pytest.raises(TypeError):
        function(ClassHook())  # type: ignore[arg-type]


def test_wrong_numeric_types_raise_channel_error_without_class_hooks() -> None:
    for function in (alpha_to_byte, css_alpha):
        with pytest.raises(ChannelError):
            function(ClassHook())  # type: ignore[arg-type]


def test_color_helpers_accept_string_subclasses_without_class_hooks() -> None:
    assert blend(HookStr("red"), "white") == Color(255, 0, 0)
    assert relative_luminance(HookStr("white")) == 1
    assert passes_contrast("black", "white", level=HookStr("aa"))
    with pytest.raises(TypeError):
        passes_contrast("black", "white", large=ClassHook())  # type: ignore[arg-type]
