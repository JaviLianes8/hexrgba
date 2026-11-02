"""Help contracts shared by source tests and installed entry point checks."""

from __future__ import annotations

import re
import subprocess
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
        assert re.search(r"\[" + option + r"(?:\s|\])", usage), (command, option, usage)
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


def check_help(python: str, tool: str, work: Path, env: dict[str, str]) -> None:
    for entry in ([tool], [python, "-I", "-m", "hexrgba"]):
        for command in COMMANDS:
            args = [command, "--help"] if command else ["--help"]
            done = subprocess.run(
                [*entry, *args],
                capture_output=True,
                text=True,
                cwd=work,
                env=env,
                timeout=30,
                check=False,
            )
            assert_help(command, done.returncode, done.stdout, done.stderr)
