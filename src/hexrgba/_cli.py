"""Command-line interface: ``hexrgba normalize | convert | contrast | blend``."""

from __future__ import annotations

import argparse
import contextlib
import math
import os
import re
import sys
from collections.abc import Sequence
from typing import NoReturn

from . import __version__
from ._blend import blend
from ._color import Color, parse_color
from ._errors import ColorError
from ._wcag import contrast_ratio, passes_contrast

_EXAMPLES = """exit codes: 0 success, 1 the pair fails --level, 2 bad usage or invalid color

examples (quote a leading # so the shell does not read it as a comment):
  hexrgba normalize "#FFAA00"            ->  #ffaa00
  hexrgba normalize ffaa0080             ->  #ffaa0080
  hexrgba normalize "#aabbcc" --short    ->  #abc
  hexrgba normalize RebeccaPurple        ->  #663399
  hexrgba convert "#ff00ffed" --to css   ->  rgba(255, 0, 255, 0.93)
  hexrgba convert "#00ffff" --to name    ->  aqua
  hexrgba convert transparent --to channels  ->  0 0 0 0
  hexrgba contrast "#767676" white       ->  4.54:1
  hexrgba contrast "#777" white --level AA   ->  exits 1: 4.47:1 is below 4.5:1
  hexrgba blend "#0000ff80" red          ->  #7f0080
"""

_FORMATS = ("hex", "short", "css", "channels", "name")


# Exit codes: 0 success, 1 the pair fails --level (or the output closed early), 2 bad usage
# or an invalid color.
EXIT_FAILS_LEVEL = 1
EXIT_BAD_INPUT = 2
EXIT_OUTPUT_CLOSED = 1


class _Parser(argparse.ArgumentParser):
    """An argument parser whose usage errors quote at most 40 characters of any word."""

    def error(self, message: str) -> NoReturn:
        message = re.sub(r"\S{41,}", lambda word: word.group()[:40] + "...", message)
        super().error(message[:500])


def _build_parser() -> argparse.ArgumentParser:
    parser = _Parser(
        prog="hexrgba",
        description="Normalize, convert, compare and blend CSS hex and named colors.",
        epilog=_EXAMPLES,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--version", action="version", version=f"hexrgba {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    norm = sub.add_parser("normalize", help="print the canonical lower-case hex form")
    norm.add_argument("color", help="hex color or CSS named color")
    norm.add_argument("--short", action="store_true", help="use #rgb / #rgba when lossless")
    _add_strict(norm)

    conv = sub.add_parser("convert", help="print the color in another notation")
    conv.add_argument("color", help="hex color or CSS named color")
    conv.add_argument("--to", choices=_FORMATS, default="css", help="output (default css)")
    _add_strict(conv)

    con = sub.add_parser("contrast", help="print the WCAG contrast ratio of two colors")
    con.add_argument("foreground", help="text color (may be translucent)")
    con.add_argument("background", help="opaque background color")
    con.add_argument("--level", choices=("AA", "AAA"), help="exit 1 if the pair fails it")
    con.add_argument(
        "--large", action="store_true", help="with --level, use the large-text threshold"
    )

    ble = sub.add_parser("blend", help="composite a color over a background")
    ble.add_argument("foreground", help="color on top (usually translucent)")
    ble.add_argument("background", help="color underneath")
    return parser


def _add_strict(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--strict", action="store_true", help="follow the CSS grammar exactly")


def _convert(color: Color, target: str) -> str:
    if target == "hex":
        return color.hex
    if target == "short":
        return color.to_hex(short=True)
    if target == "channels":
        return " ".join(str(channel) for channel in color.as_tuple())
    if target == "name":
        if color.name is None:
            raise ColorError(f"no CSS named color equals {color.hex}")
        return color.name
    return color.to_css()


def _ratio_text(ratio: float) -> str:
    # Truncate rather than round, so a failing 4.499 never prints as a passing 4.50.
    return f"{math.floor(ratio * 100) / 100:.2f}:1"


def _run(args: argparse.Namespace) -> int:
    if args.command == "normalize":
        print(parse_color(args.color, strict=args.strict).to_hex(short=args.short))
    elif args.command == "convert":
        print(_convert(parse_color(args.color, strict=args.strict), args.to))
    elif args.command == "contrast":
        ratio = contrast_ratio(args.foreground, args.background)
        print(_ratio_text(ratio))
        if args.level and not passes_contrast(
            args.foreground, args.background, level=args.level, large=args.large
        ):
            kind = "large text" if args.large else "normal text"
            print(f"hexrgba: fails WCAG {args.level} for {kind}", file=sys.stderr)
            return EXIT_FAILS_LEVEL
    else:
        print(blend(args.foreground, args.background).hex)
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """Run the command-line interface and return a process exit code."""
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command == "contrast" and args.large and not args.level:
        parser.error("--large only applies together with --level")
    try:
        code = _run(args)
        sys.stdout.flush()
    except (ColorError, TypeError) as exc:
        print(f"hexrgba: error: {exc}", file=sys.stderr)
        return EXIT_BAD_INPUT
    except OSError:
        # Only printing can fail here: the reader went away (a closed pipe, which Windows
        # reports as EINVAL). Exit 1 quietly instead of a traceback at the final flush.
        _silence_stdout()
        return EXIT_OUTPUT_CLOSED
    return code


def _silence_stdout() -> None:
    with contextlib.suppress(OSError, ValueError):
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
