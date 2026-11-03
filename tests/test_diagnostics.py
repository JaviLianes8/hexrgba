"""Hand-written contracts for private, bounded input diagnostics."""

from __future__ import annotations

from collections.abc import Callable

import pytest

from hexrgba import (
    Color,
    ColorError,
    HexColorError,
    alpha_to_byte,
    blend,
    css_alpha,
    normalize,
    parse,
    parse_color,
    passes_contrast,
    relative_luminance,
    shorten,
    to_hex,
)
from hexrgba._cli import main

SECRET = "password=private_42"


@pytest.mark.parametrize(
    "call",
    [
        lambda: parse(SECRET),
        lambda: normalize(SECRET),
        lambda: shorten(SECRET),
        lambda: parse_color(SECRET),
        lambda: Color.parse(SECRET),
        lambda: parse_color(" " + SECRET, strict=True),
        lambda: blend(SECRET, "red"),
        lambda: relative_luminance(SECRET),
        lambda: css_alpha(SECRET),  # type: ignore[arg-type]
        lambda: alpha_to_byte(SECRET),  # type: ignore[arg-type]
        lambda: to_hex(SECRET, 0, 0),  # type: ignore[arg-type]
        lambda: passes_contrast("red", "white", level=SECRET),
    ],
)
def test_errors_do_not_disclose_input(call: Callable[[], object]) -> None:
    with pytest.raises(ValueError) as caught:
        call()
    assert SECRET not in str(caught.value)


@pytest.mark.parametrize("length", [40, 41])
def test_error_privacy_at_former_representation_boundary(length: int) -> None:
    value = "#" + "f" * (length - 3)
    assert len(repr(value)) == length
    with pytest.raises(HexColorError) as caught:
        parse(value)
    assert str(caught.value) == "not a valid hex color; expected 3, 4, 6 or 8 ASCII hex digits"


@pytest.mark.parametrize(
    "args",
    [
        ["normalize", SECRET],
        [SECRET],
        ["normalize", "red", "--unknown=" + SECRET],
        ["normalize", "red", SECRET],
        ["convert", "red", "--to", SECRET],
        ["contrast", "red", "white", "--level", SECRET],
    ],
)
def test_cli_diagnostics_do_not_disclose_input(
    capsys: pytest.CaptureFixture[str], args: list[str]
) -> None:
    code: int | str | None
    try:
        code = main(args)
    except SystemExit as error:
        code = error.code
    assert code == 2
    out, err = capsys.readouterr()
    assert out == "" and "error:" in err and SECRET not in err


class ReprProbe:
    calls = 0

    def __repr__(self) -> str:
        self.calls += 1
        return SECRET


@pytest.mark.parametrize("function", [css_alpha, alpha_to_byte])
def test_rejection_does_not_render_objects_or_shared_containers(
    function: Callable[[int], object],
) -> None:
    probe = ReprProbe()
    graph: object = probe
    for _ in range(20):
        graph = [graph, graph]
    for value in (probe, graph, {"secret": probe}, [probe]):
        with pytest.raises(ColorError):
            function(value)  # type: ignore[arg-type]
        assert probe.calls == 0


def test_errors_do_not_disclose_custom_type_names() -> None:
    value = type(SECRET, (), {})()
    with pytest.raises(TypeError) as caught:
        parse_color(value)
    assert SECRET not in str(caught.value)
