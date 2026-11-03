"""The complete promise of every public name: signature, result and failure types."""

from __future__ import annotations

import copy
import dataclasses
import inspect
import pickle

import pytest

import hexrgba
from hexrgba import (
    NAMED_COLORS,
    ChannelError,
    Color,
    ColorError,
    ColorNameError,
    HexColorError,
)

SIGNATURES = {
    "alpha_to_byte": "(alpha: 'float') -> 'int'",
    "blend": "(foreground: 'Color | str', background: 'Color | str') -> 'Color'",
    "contrast_ratio": "(foreground: 'Color | str', background: 'Color | str') -> 'float'",
    "css_alpha": "(byte: 'int') -> 'str'",
    "is_color": "(text: 'object', *, strict: 'bool' = False) -> 'bool'",
    "is_hex": "(value: 'object') -> 'bool'",
    "normalize": "(value: 'str', *, short: 'bool' = False) -> 'str'",
    "parse": "(value: 'str') -> 'tuple[int, int, int, int]'",
    "parse_color": "(text: 'str', *, strict: 'bool' = False) -> 'Color'",
    "passes_contrast": "(foreground: 'Color | str', background: 'Color | str', *, "
    "level: 'str' = 'AA', large: 'bool' = False) -> 'bool'",
    "relative_luminance": "(color: 'Color | str') -> 'float'",
    "shorten": "(value: 'str') -> 'str'",
    "to_hex": "(r: 'int', g: 'int', b: 'int', a: 'int | None' = None) -> 'str'",
}

METHODS = {
    "parse": "(text: 'str', *, strict: 'bool' = False) -> 'Color'",
    "from_rgba": "(r: 'int', g: 'int', b: 'int', alpha: 'float' = 1.0) -> 'Color'",
    "to_hex": "(self, *, short: 'bool' = False) -> 'str'",
    "to_css": "(self) -> 'str'",
    "with_alpha": "(self, alpha: 'float') -> 'Color'",
    "as_tuple": "(self) -> 'tuple[int, int, int, int]'",
}
PROPERTIES = ("alpha", "is_opaque", "hex", "name")


@pytest.mark.parametrize("name", sorted(SIGNATURES))
def test_function_signatures_are_pinned(name: str) -> None:
    assert str(inspect.signature(getattr(hexrgba, name))) == SIGNATURES[name]


@pytest.mark.parametrize("name", sorted(METHODS))
def test_color_method_signatures_are_pinned(name: str) -> None:
    assert str(inspect.signature(getattr(Color, name))) == METHODS[name]


def test_color_is_a_frozen_slotted_dataclass_with_pinned_fields() -> None:
    fields = [(f.name, f.default) for f in dataclasses.fields(Color)]
    assert fields == [
        ("r", dataclasses.MISSING),
        ("g", dataclasses.MISSING),
        ("b", dataclasses.MISSING),
        ("a", 255),
    ]
    assert Color.__slots__ == ("r", "g", "b", "a")
    assert all(isinstance(inspect.getattr_static(Color, p), property) for p in PROPERTIES)
    color = Color(1, 2, 3, 4)
    with pytest.raises(dataclasses.FrozenInstanceError):
        color.a = 5  # type: ignore[misc]
    assert repr(color) == "Color(r=1, g=2, b=3, a=4)" and str(color) == "#01020304"


def test_colors_and_errors_pickle_and_copy_as_public_names() -> None:
    for value in (Color(1, 2, 3), Color(0, 0, 0, 0)):
        again = pickle.loads(pickle.dumps(value))
        assert again == value and hash(again) == hash(value)
        assert copy.copy(value) == value == copy.deepcopy(value)
    assert b"hexrgba._" not in pickle.dumps(Color(1, 2, 3))
    for cls in (ColorError, HexColorError, ChannelError, ColorNameError):
        assert cls.__module__ == "hexrgba" and Color.__module__ == "hexrgba"
        error = pickle.loads(pickle.dumps(cls("bad")))
        assert (type(error), str(error)) == (cls, "bad")


def test_error_hierarchy_is_exactly_the_documented_one() -> None:
    assert ColorError.__mro__[1:] == ValueError.__mro__
    assert HexColorError.__bases__ == (ColorError,)
    assert ChannelError.__bases__ == (HexColorError,)
    assert ColorNameError.__bases__ == (ColorError,)


def test_every_public_name_is_documented_with_an_example() -> None:
    for name in hexrgba.__all__:
        if name == "NAMED_COLORS":
            assert ">>> " in (hexrgba.__doc__ or "") and "NAMED_COLORS" in hexrgba.__doc__
            continue
        assert ">>> " in (inspect.getdoc(getattr(hexrgba, name)) or ""), name
    for member in (*METHODS, *PROPERTIES):
        assert ">>> " in (inspect.getdoc(getattr(Color, member)) or ""), member


def test_named_colors_is_a_read_only_mapping_of_str_to_canonical_hex() -> None:
    assert len(NAMED_COLORS) == 148
    assert all(isinstance(k, str) and isinstance(v, str) for k, v in NAMED_COLORS.items())
    with pytest.raises(TypeError):
        NAMED_COLORS["red"] = "#000000"  # type: ignore[index]
    with pytest.raises(AttributeError):
        NAMED_COLORS.clear()  # type: ignore[attr-defined]


def test_subclasses_keep_their_type_through_the_constructors() -> None:
    class Shade(Color):
        __slots__ = ()

    assert type(Shade.parse("red")) is Shade
    assert type(Shade.from_rgba(1, 2, 3, 0.5)) is Shade
    assert type(Shade(1, 2, 3).with_alpha(0)) is Shade
    assert Shade(0, 0, 0, 0).name == "transparent"


def test_the_package_exports_nothing_else() -> None:
    public = {name for name in vars(hexrgba) if not name.startswith("_")}
    assert public == set(hexrgba.__all__)
