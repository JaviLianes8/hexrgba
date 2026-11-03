"""Complete subcommand help promises checked against source and installed commands."""

from __future__ import annotations

import re
import subprocess
from collections.abc import Callable
from pathlib import Path

Run = Callable[[list[str]], tuple[int, str, str]]

# Hand-written expectations, independent of the argument parser: the complete help of each
# subcommand, so no description paragraph, operand role, option promise or epilog can
# change unnoticed.
_TEXT = {
    "normalize": """usage: hexrgba normalize [-h] [--short] [--strict] color
color hex color or CSS named color
-h, --help show this help message and exit
--short use #rgb / #rgba when lossless
--strict follow the CSS grammar exactly""",
    "convert": """usage: hexrgba convert [-h] [--to {hex,short,css,channels,name}] [--strict] color
color hex color or CSS named color
-h, --help show this help message and exit
--to {hex,short,css,channels,name} output (default css)
--strict follow the CSS grammar exactly""",
    "contrast": """usage: hexrgba contrast [-h] [--level {AA,AAA}] [--large] foreground background
foreground text color (may be translucent)
background opaque background color
-h, --help show this help message and exit
--level {AA,AAA} exit 1 if the pair fails it
--large with --level, use the large-text threshold""",
    "blend": """usage: hexrgba blend [-h] foreground background
foreground color on top (usually translucent)
background color underneath
-h, --help show this help message and exit""",
}
COMMANDS = tuple(_TEXT)
_FAILS = "hexrgba: fails WCAG AA for normal text\n"


def _normalized(out: str) -> str:
    # argparse renamed its options heading; wrapping and indentation are cosmetic.
    out = re.sub(r"(?m)^(?:positional arguments|options|optional arguments):\s*$", "", out)
    return " ".join(out.split())


def _usage_error(result: tuple[int, str, str]) -> bool:
    code, out, err = result
    return code == 2 and out == "" and "error:" in err


def assert_sub_help(run: Run, command: str) -> None:
    """The complete help text must match, and each promise must match command output."""
    code, out, err = run([command, "--help"])
    assert (code, err) == (0, ""), (command, code, err)
    text = _normalized(out)
    assert text == " ".join(_TEXT[command].split()), (command, out)
    if command == "normalize":
        # "canonical lower-case hex form" of an upper-case input.
        assert run(["normalize", "#AABBCC"]) == (0, "#aabbcc\n", "")
    elif command == "convert":
        assert run(["convert", "red"]) == (0, "rgb(255, 0, 0)\n", "")
    elif command == "contrast":
        _assert_contrast(run, text)
    else:
        # No epilog: plain success exits 0, whichever operand is translucent.
        assert run(["blend", "#0000ff80", "red"]) == (0, "#7f0080\n", "")
        assert run(["blend", "red", "#0000ff80"]) == (0, "#ff0000\n", "")


def _assert_contrast(run: Run, text: str) -> None:
    # "text color (may be translucent)": a translucent foreground is measured.
    assert "foreground text color (may be translucent)" in text
    assert run(["contrast", "#00000080", "white"]) == (0, "4.00:1\n", "")
    # "opaque background color": a translucent background is rejected.
    assert "background opaque background color" in text
    code, out, err = run(["contrast", "black", "#ffffff80"])
    assert (code, out) == (2, "") and "background must be opaque" in err, (code, out, err)
    # "exit N if the pair fails it": the stated code is the observed one.
    stated = re.search(r"--level \{AA,AAA\} exit (\d+) if the pair fails it", text)
    assert stated is not None and int(stated[1]) == 1, text
    assert run(["contrast", "white", "white", "--level", "AA"]) == (1, "1.00:1\n", _FAILS)
    # "with --level": --large alone is a usage error, and with a level it lowers the bar.
    assert "--large with --level, use the large-text threshold" in text
    assert _usage_error(run(["contrast", "white", "white", "--large"]))
    assert run(["contrast", "#777", "white", "--level", "AA", "--large"]) == (0, "4.47:1\n", "")


def check_sub_help(python: str, tool: str, work: Path, env: dict[str, str]) -> None:
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

        for command in COMMANDS:
            assert_sub_help(run, command)
