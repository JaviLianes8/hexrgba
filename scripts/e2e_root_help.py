"""Complete root help promises checked against source and installed commands."""

from __future__ import annotations

import re
import shlex
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
    # The AA threshold lies between the failing 4.47 example and this passing 4.54 pair.
    "examples": ((["contrast", "#767676", "white", "--level", "AA"], "4.54:1\n"),),
}
_EXAMPLES = """examples (quote a leading # so the shell does not read it as a comment):
hexrgba normalize "#FFAA00" -> #ffaa00
hexrgba normalize ffaa0080 -> #ffaa0080
hexrgba normalize "#aabbcc" --short -> #abc
hexrgba normalize RebeccaPurple -> #663399
hexrgba convert "#ff00ffed" --to css -> rgba(255, 0, 255, 0.93)
hexrgba convert "#00ffff" --to name -> aqua
hexrgba convert transparent --to channels -> 0 0 0 0
hexrgba contrast "#767676" white -> 4.54:1
hexrgba contrast "#777" white --level AA -> exits 1: 4.47:1 is below 4.5:1
hexrgba blend "#0000ff80" red -> #7f0080
"""
# WCAG 2.2 success criteria 1.4.3 and 1.4.6: (level, large text) -> minimum ratio.
_THRESHOLDS = {("AA", False): 4.5, ("AA", True): 3.0, ("AAA", False): 7.0, ("AAA", True): 4.5}


def assert_root_help(run: Run, topic: str) -> None:
    """Every root description paragraph and summary must agree with command output."""
    code, out, err = run(["--help"])
    assert (code, err) == (0, ""), (code, err)
    usage, separator, body = out.partition("\n\n")
    assert separator and " ".join(usage.split()) == _ROOT_USAGE, out
    body, separator, epilog = body.partition("exit codes:")
    assert separator, out
    summary, separator, examples = epilog.partition("examples (")
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
    if topic == "examples":
        assert_examples(run, "examples (" + examples)


def assert_examples(run: Run, text: str) -> None:
    """Every example's complete result, including a stated threshold, must hold."""
    lines = [" ".join(line.split()) for line in text.strip().splitlines()]
    assert lines == _EXAMPLES.strip().splitlines(), text
    for line in lines[1:]:
        command, result = line.split(" -> ")
        args = shlex.split(command)[1:]
        code, out, err = run(args)
        failure = re.fullmatch(r"exits 1: (\d+\.\d\d):1 is below (\d+(?:\.\d+)?):1", result)
        if failure is None:
            assert (code, out, err) == (0, result + "\n", ""), (line, code, out, err)
            continue
        level = args[args.index("--level") + 1]
        large = "--large" in args
        threshold = _THRESHOLDS[(level, large)]
        assert float(failure[2]) == threshold and float(failure[1]) < threshold, line
        kind = "large text" if large else "normal text"
        expected = (1, failure[1] + ":1\n", f"hexrgba: fails WCAG {level} for {kind}\n")
        assert (code, out, err) == expected, (line, code, out, err)


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
