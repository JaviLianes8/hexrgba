"""Help contracts shared by source tests and installed entry point checks."""

from __future__ import annotations

import re
import subprocess
from collections.abc import Callable
from pathlib import Path

# Hand-written expectations for the documented command-line interface.
COMMANDS = ("", "normalize", "convert", "contrast", "blend")
_OPERANDS = {
    "": "...",
    "normalize": "color",
    "convert": "color",
    "contrast": "foreground background",
    "blend": "foreground background",
}
_OPTIONS = {
    "": ("--version",),
    "normalize": ("--short", "--strict"),
    "convert": ("--to", "--strict"),
    "contrast": ("--level", "--large"),
    "blend": (),
}
_CHOICES = {
    "": frozenset(COMMANDS[1:]),
    "convert": frozenset(("hex", "short", "css", "channels", "name")),
    "contrast": frozenset(("AA", "AAA")),
}
_VALUES = {"--to": "{hex,short,css,channels,name}", "--level": "{AA,AAA}"}
Run = Callable[[list[str]], tuple[int, str, str]]


def assert_help(command: str, code: int, out: str, err: str) -> None:
    """Require usable syntax and exactly the supported flags and choices."""
    assert (code, err) == (0, ""), (command, code, err)
    syntax = out.split("exit codes:", 1)[0].split("examples (", 1)[0]
    usage = " ".join(syntax.split("\n\n", 1)[0].split())
    prefix = "usage: hexrgba " + (command + " " if command else "")
    assert usage.startswith(prefix), (command, usage)
    assert usage.endswith(" " + _OPERANDS[command]), (command, usage)
    assert "[-h]" in usage, usage
    flags = set(re.findall(r"(?<![\w-])--?[a-z][a-z-]*\b", syntax))
    assert flags == {"-h", "--help", *_OPTIONS[command]}, (command, flags)
    for option in _OPTIONS[command]:
        form = option + (" " + _VALUES[option] if option in _VALUES else "")
        assert f"[{form}]" in usage, (command, form, usage)
        assert re.search(r"(?m)^\s+" + re.escape(form) + r"(?: {2,}|\n)", syntax), (
            command,
            form,
            syntax,
        )
    choices = [
        frozenset(re.sub(r"\s", "", group).split(","))
        for group in re.findall(r"\{([^}]+)\}", syntax)
    ]
    if command in _CHOICES:
        assert choices and all(group == _CHOICES[command] for group in choices), (command, choices)
        assert "{" in usage, usage
    else:
        assert not choices, (command, choices)
    if command:
        for operand in _OPERANDS[command].split():
            assert re.search(r"(?m)^\s+" + operand + r"\s+\S", syntax), (operand, syntax)
    if not command:
        description = " ".join(syntax.split("\n\n")[1].split())
        assert description == "Normalize, convert, compare and blend CSS hex and named colors.", out
        for name in COMMANDS[1:]:
            assert re.search(r"(?m)^\s+" + name + r"\s+\S", syntax), (name, syntax)
    if command == "convert":
        assert re.search(r"--to\s+\{[^}]+\}\s+output \(default css\)", syntax), syntax
    if command in ("normalize", "convert"):
        for label, description in (
            ("color", "hex color or CSS named color"),
            ("--strict", "follow the CSS grammar exactly"),
        ):
            assert re.search(r"(?m)^\s+" + label + r"\s+" + description + r"\s*$", syntax), syntax
    if command == "normalize":
        assert re.search(r"(?m)^\s+--short\s+use #rgb / #rgba when lossless\s*$", syntax), syntax
    if command == "blend":
        for operand, role in (
            ("foreground", "color on top (usually translucent)"),
            ("background", "color underneath"),
        ):
            pattern = r"(?m)^\s+" + operand + r"\s+" + re.escape(role) + r"\s*$"
            assert re.search(pattern, syntax), syntax


def assert_conversion_default(run: Run) -> None:
    """The advertised CSS default must match omitted and explicit --to."""
    code, out, err = run(["convert", "--help"])
    assert_help("convert", code, out, err)
    default = re.search(r"default (\w+)", out)
    assert default is not None and default[1] == "css", out
    expected = (0, "rgb(255, 0, 0)\n", "")
    assert run(["convert", "red"]) == expected
    assert run(["convert", "red", "--to", default[1]]) == expected


def assert_blend_roles(run: Run) -> None:
    """Following the operand descriptions must put translucent blue over red."""
    code, out, err = run(["blend", "--help"])
    assert_help("blend", code, out, err)
    assert run(["blend", "#0000ff80", "red"]) == (0, "#7f0080\n", "")
    assert run(["blend", "red", "#0000ff80"]) == (0, "#ff0000\n", "")


def assert_option_forms(run: Run) -> None:
    """Printed flags accept no value; choice options require one listed value."""
    for command in COMMANDS:
        args = [command, "--help"] if command else ["--help"]
        assert_help(command, *run(args))
    for args, output in (
        (["normalize", "#aabbcc", "--short"], "#abc\n"),
        (["normalize", "#aabbcc", "--strict"], "#aabbcc\n"),
        (["convert", "#aabbcc", "--strict"], "rgb(170, 187, 204)\n"),
        (["contrast", "#777", "white", "--level", "AA", "--large"], "4.47:1\n"),
    ):
        assert run(args) == (0, output, ""), args
        code, out, err = run([*args, "3"])
        assert code == 2 and out == "" and "error:" in err, args
    for choice, output in (
        ("hex", "#ff0000"),
        ("short", "#f00"),
        ("css", "rgb(255, 0, 0)"),
        ("channels", "255 0 0 255"),
        ("name", "red"),
    ):
        assert run(["convert", "red", "--to", choice]) == (0, output + "\n", "")
    for level in ("AA", "AAA"):
        assert run(["contrast", "black", "white", "--level", level]) == (0, "21.00:1\n", "")
    for args in (["convert", "red", "--to"], ["contrast", "black", "white", "--level"]):
        code, out, err = run(args)
        assert code == 2 and out == "" and "error:" in err, args


def assert_lossless_shortening(run: Run) -> None:
    """Short output preserves every channel, including alpha, without rounding."""
    assert_help("normalize", *run(["normalize", "--help"]))
    for color, expected in (
        ("#aabbcc", "#abc"),
        ("#aabbccdd", "#abcd"),
        ("#123456", "#123456"),
        ("#aabbcc80", "#aabbcc80"),
    ):
        assert run(["normalize", color, "--short"]) == (0, expected + "\n", "")


def assert_strict_inputs(run: Run) -> None:
    """Strict CSS hex requires a hash and rejects surrounding whitespace."""
    for command in ("normalize", "convert"):
        assert_help(command, *run([command, "--help"]))
        options = ["--to", "hex"] if command == "convert" else []
        for color in ("abc", "abcd", "aabbcc", "aabbccdd", " #aabbcc "):
            code, out, err = run([command, color, *options, "--strict"])
            assert code == 2 and out == "" and "error:" in err, (command, color)
            valid = color.strip() if color.startswith(" ") else "#" + color
            expected = run([command, valid, *options, "--strict"])
            assert expected[0] == 0 and expected[2] == "", (command, valid, expected)
            assert run([command, color, *options]) == expected


def assert_named_inputs(run: Run) -> None:
    """Root and operand help promise hex and names that work in both modes."""
    assert_help("", *run(["--help"]))
    for command in ("normalize", "convert"):
        assert_help(command, *run([command, "--help"]))
        options = ["--to", "hex"] if command == "convert" else []
        for color, expected in (
            ("#663399", "#663399"),
            ("rebeccapurple", "#663399"),
            ("RebeccaPurple", "#663399"),
            ("transparent", "#00000000"),
        ):
            for strict in ([], ["--strict"]):
                assert run([command, color, *options, *strict]) == (0, expected + "\n", "")


def check_help(python: str, tool: str, work: Path, env: dict[str, str]) -> None:
    for entry in ([tool], [python, "-I", "-m", "hexrgba"]):

        def run(args: list[str], entry: list[str] = entry) -> tuple[int, str, str]:
            done = subprocess.run(
                [*entry, *args],
                capture_output=True,
                text=True,
                cwd=work,
                env=env,
                timeout=30,
                check=False,
            )
            return done.returncode, done.stdout, done.stderr

        assert_conversion_default(run)
        assert_blend_roles(run)
        assert_option_forms(run)
        assert_lossless_shortening(run)
        assert_strict_inputs(run)
        assert_named_inputs(run)
