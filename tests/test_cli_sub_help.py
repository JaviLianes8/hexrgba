"""Complete subcommand help must agree with each subcommand's observed behavior."""

from __future__ import annotations

import importlib.util
from collections.abc import Callable
from pathlib import Path

import pytest

from hexrgba._cli import main

_SPEC = importlib.util.spec_from_file_location(
    "e2e_sub_help", Path(__file__).parent.parent / "scripts" / "e2e_sub_help.py"
)
assert _SPEC is not None and _SPEC.loader is not None
_HELP = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_HELP)

Run = Callable[[list[str]], tuple[int, str, str]]


@pytest.fixture
def run_cli(capsys: pytest.CaptureFixture[str]) -> Run:
    def run(args: list[str]) -> tuple[int, str, str]:
        try:
            code = main(args)
        except SystemExit as exc:
            assert isinstance(exc.code, int)
            code = exc.code
        out, err = capsys.readouterr()
        return code, out, err

    return run


@pytest.mark.parametrize("command", list(_HELP.COMMANDS))
def test_subcommand_help_matches_behavior(run_cli: Run, command: str) -> None:
    _HELP.assert_sub_help(run_cli, command)


def _description(out: str) -> str:
    usage, separator, rest = out.partition("\n\n")
    return usage + separator + "Print the color as upper-case hex.\n\n" + rest


@pytest.mark.parametrize(
    ("command", "falsify"),
    [
        (
            "contrast",
            lambda out: out.replace(
                "opaque background color", "background color (may be translucent)"
            ),
        ),
        (
            "contrast",
            lambda out: out.replace(
                "text color (may be translucent)", "text color (must be opaque)"
            ),
        ),
        ("contrast", lambda out: out.replace("exit 1 if the pair", "exit 2 if the pair")),
        (
            "contrast",
            lambda out: out.replace(
                "with --level, use the large-text threshold",
                "use the large-text threshold (implies --level AA)",
            ),
        ),
        ("normalize", _description),
        ("blend", lambda out: out + "\nexit codes: 3 success\n"),
    ],
    ids=[
        "translucent-background",
        "opaque-foreground",
        "false-level-code",
        "large-implies-level",
        "false-description",
        "false-epilog",
    ],
)
def test_subcommand_help_contract_rejects_false_promises(
    run_cli: Run, command: str, falsify: Callable[[str], str]
) -> None:
    code, out, err = run_cli([command, "--help"])
    false_out = falsify(out)
    assert false_out != out
    false_help = code, false_out, err

    def run(args: list[str]) -> tuple[int, str, str]:
        if args == [command, "--help"]:
            return false_help
        return run_cli(args)

    with pytest.raises(AssertionError):
        _HELP.assert_sub_help(run, command)
