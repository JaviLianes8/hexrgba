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
        assert choices and all(group == _CHOICES[command] for group in choices), (
            command,
            choices,
        )
        assert "{" in usage, usage
    else:
        assert not choices, (command, choices)
    if command:
        for operand in _OPERANDS[command].split():
            assert re.search(r"(?m)^\s+" + operand + r"\s+\S", syntax), (operand, syntax)
    if not command:
        for name in COMMANDS[1:]:
            assert re.search(r"(?m)^\s+" + name + r"\s+\S", syntax), (name, syntax)
    if command == "convert":
        assert re.search(r"--to\s+\{[^}]+\}\s+output \(default css\)", syntax), syntax
    if command == "blend":
        for operand, role in (
            ("foreground", "color on top (usually translucent)"),
            ("background", "color underneath"),
        ):
            assert re.search(r"(?m)^\s+" + operand + r"\s+" + re.escape(role) + r"\s*$", syntax), (
                syntax
            )


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
