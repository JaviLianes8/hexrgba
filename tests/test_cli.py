"""The command-line interface, driven in-process through main()."""

import importlib.util
from pathlib import Path

import pytest

from hexrgba import __version__
from hexrgba._cli import _EXAMPLES, main

_SPEC = importlib.util.spec_from_file_location(
    "e2e_wheel", Path(__file__).parent.parent / "scripts" / "e2e_wheel.py"
)
assert _SPEC is not None and _SPEC.loader is not None
_E2E = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_E2E)
help_examples = _E2E.help_examples


def _run(capsys: pytest.CaptureFixture[str], *args: str) -> tuple[int, str, str]:
    code = main(list(args))
    out, err = capsys.readouterr()
    return code, out, err


@pytest.mark.parametrize(
    "args,expected",
    [
        (["normalize", "#FFAA00"], "#ffaa00"),
        (["normalize", "ffaa0080"], "#ffaa0080"),
        (["normalize", "#aabbcc", "--short"], "#abc"),
        (["normalize", "RebeccaPurple"], "#663399"),
        (["convert", "#ff00ffed"], "rgba(255, 0, 255, 0.93)"),
        (["convert", "#ff00ffed", "--to", "css"], "rgba(255, 0, 255, 0.93)"),
        (["convert", "#00ffff", "--to", "name"], "aqua"),
        (["convert", "transparent", "--to", "channels"], "0 0 0 0"),
        (["convert", "#aabbccdd", "--to", "short"], "#abcd"),
        (["convert", "red", "--to", "hex"], "#ff0000"),
        (["contrast", "#767676", "white"], "4.54:1"),
        (["contrast", "black", "white", "--level", "AAA"], "21.00:1"),
        (["blend", "#0000ff80", "red"], "#7f0080"),
    ],
)
def test_documented_examples(
    capsys: pytest.CaptureFixture[str], args: list[str], expected: str
) -> None:
    code, out, err = _run(capsys, *args)
    assert (code, out.strip(), err) == (0, expected, "")


def test_contrast_below_the_level_exits_1_but_still_prints_the_ratio(
    capsys: pytest.CaptureFixture[str],
) -> None:
    code, out, err = _run(capsys, "contrast", "#777", "white", "--level", "AA")
    assert code == 1
    assert out.strip() == "4.47:1"
    assert "fails WCAG AA for normal text" in err


def test_contrast_large_text_threshold(capsys: pytest.CaptureFixture[str]) -> None:
    code, _, _ = _run(capsys, "contrast", "#777", "white", "--level", "AA", "--large")
    assert code == 0


def test_ratio_is_truncated_not_rounded(capsys: pytest.CaptureFixture[str]) -> None:
    # 5.699... must print 5.69, never a rounded-up 5.70.
    _, out, _ = _run(capsys, "contrast", "#E5E5E5", "#6221EA")
    assert out.strip() == "5.69:1"


@pytest.mark.parametrize(
    "args,message",
    [
        (["normalize", "nope"], "not a hex color or CSS named color"),
        (["normalize", "fff", "--strict"], "leading '#'"),
        (["convert", "#123456", "--to", "name"], "no CSS named color"),
        (["contrast", "black", "#ffffff80"], "opaque"),
        (["blend", "#ggg", "red"], "not a valid hex color"),
    ],
)
def test_errors_go_to_stderr_with_exit_2(
    capsys: pytest.CaptureFixture[str], args: list[str], message: str
) -> None:
    code, out, err = _run(capsys, *args)
    assert (code, out) == (2, "")
    assert err.startswith("hexrgba: error:") and message in err


def test_usage_errors_exit_2(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["convert", "red", "--to", "lab"])
    assert exc.value.code == 2
    assert "invalid choice" in capsys.readouterr().err


def test_large_without_level_is_a_usage_error(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["contrast", "#777", "white", "--large"])
    assert exc.value.code == 2
    assert "--large only applies together with --level" in capsys.readouterr().err


def test_a_huge_input_gives_a_short_message(capsys: pytest.CaptureFixture[str]) -> None:
    code, _, err = _run(capsys, "normalize", "z" * 1_000_000)
    assert code == 2
    assert len(err) < 200 and "..." in err


def test_help_shows_runnable_examples(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0
    out = capsys.readouterr().out
    assert 'hexrgba normalize "#FFAA00"' in out and "hexrgba blend" in out


def test_version(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit):
        main(["--version"])
    assert capsys.readouterr().out.strip() == f"hexrgba {__version__}"


def test_every_help_example_holds(capsys: pytest.CaptureFixture[str]) -> None:
    examples = help_examples(_EXAMPLES)
    assert len(examples) >= 8
    for argv, want_code, want_out in examples:
        code, out, _ = _run(capsys, *argv)
        assert (code, out.strip()) == (want_code, want_out), argv
