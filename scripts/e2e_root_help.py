"""Complete root help promises checked against source and installed commands."""

from __future__ import annotations

import re
import subprocess
from collections.abc import Callable
from pathlib import Path

Run = Callable[[list[str]], tuple[int, str, str]]

# Hand-written expectations, independent of the argument parser and color helpers.
_ROOT_USAGE = "usage: hexrgba [-h] [--version] {normalize,convert,contrast,blend} ..."
_EXIT_CODES = "exit codes: 0 success, 1 the pair fails --level, 2 bad usage or invalid color"
_ROOT_TEXT = """Normalize, convert, compare and blend CSS hex and named colors.
{normalize,convert,contrast,blend}
normalize print the canonical lower-case hex form
convert print the color in another notation
contrast print the WCAG contrast ratio of two colors
blend composite a color over a background
-h, --help show this help message and exit
--version show program's version number and exit
"""
CASES = {
    "normalize": ((["normalize", "#AaBBcC"], "#aabbcc\n"),),
    "convert": ((["convert", "red"], "rgb(255, 0, 0)\n"),),
    "contrast": ((["contrast", "black", "white"], "21.00:1\n"),),
    "blend": (
        (["blend", "#0000ff80", "red"], "#7f0080\n"),
        (["blend", "red", "#0000ff80"], "#ff0000\n"),
    ),
    "description": ((["normalize", "rebeccapurple"], "#663399\n"),),
    "version": ((["--version"], "hexrgba 1.0.0\n"),),
}


def assert_root_help(run: Run, topic: str) -> None:
    """Every root description paragraph and summary must agree with command output."""
    code, out, err = run(["--help"])
    assert (code, err) == (0, ""), (code, err)
    usage, separator, body = out.partition("\n\n")
    assert separator and " ".join(usage.split()) == _ROOT_USAGE, out
    body, separator, epilog = body.partition("exit codes:")
    assert separator, out
    summary, separator, _ = epilog.partition("examples (")
    assert separator and "exit codes: " + " ".join(summary.split()) == _EXIT_CODES, out
    # argparse renamed its options heading; wrapping and indentation are cosmetic.
    body = re.sub(r"(?m)^(?:positional arguments|options|optional arguments):\s*$", "", body)
    assert " ".join(body.split()) == " ".join(_ROOT_TEXT.split()), out
    # Required command syntax and both documented kinds of input failure agree.
    for args in ([], ["normalize", "not-a-color"]):
        code, out, err = run(args)
        assert (code, out) == (2, "") and "error:" in err, (args, code, out, err)
    assert run(["contrast", "black", "white", "--level", "AA"]) == (0, "21.00:1\n", "")
    assert run(["contrast", "white", "white", "--level", "AA"]) == (
        1,
        "1.00:1\n",
        "hexrgba: fails WCAG AA for normal text\n",
    )
    for args, expected in CASES[topic]:
        assert run(args) == (0, expected, ""), args


def check_root_help(python: str, tool: str, work: Path, env: dict[str, str]) -> None:
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

        for topic in CASES:
            assert_root_help(run, topic)
