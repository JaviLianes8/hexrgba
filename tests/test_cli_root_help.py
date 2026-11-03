"""Root help descriptions must agree with each advertised command's behavior."""

from __future__ import annotations

import importlib.util
from collections.abc import Callable
from pathlib import Path

import pytest

from hexrgba._cli import main

_SPEC = importlib.util.spec_from_file_location(
    "e2e_root_help", Path(__file__).parent.parent / "scripts" / "e2e_root_help.py"
)
assert _SPEC is not None and _SPEC.loader is not None
_HELP = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_HELP)


@pytest.fixture
def run_cli(capsys: pytest.CaptureFixture[str]) -> Callable[[list[str]], tuple[int, str, str]]:
    def run(args: list[str]) -> tuple[int, str, str]:
        try:
            code = main(args)
        except SystemExit as exc:
            assert isinstance(exc.code, int)
            code = exc.code
        out, err = capsys.readouterr()
        return code, out, err

    return run


@pytest.mark.parametrize("topic", list(_HELP.CASES))
def test_root_help_matches_behavior(
    run_cli: Callable[[list[str]], tuple[int, str, str]], topic: str
) -> None:
    _HELP.assert_root_help(run_cli, topic)


@pytest.mark.parametrize(
    ("original", "replacement"),
    [
        ("{normalize,convert,contrast,blend} ...", "[{normalize,convert,contrast,blend}] ..."),
        ("{normalize,convert,contrast,blend} ...", "FILE {normalize,convert,contrast,blend} ..."),
        ("exit codes: 0 success", "exit codes: 3 success"),
        ("4.47:1 is below 4.5:1", "4.47:1 is below 3:1"),
    ],
    ids=["optional-command", "invented-file", "false-success-code", "false-example-threshold"],
)
def test_root_help_contract_rejects_false_promises(
    run_cli: Callable[[list[str]], tuple[int, str, str]], original: str, replacement: str
) -> None:
    code, out, err = run_cli(["--help"])
    assert original in out
    false_help = code, out.replace(original, replacement, 1), err

    def run(args: list[str]) -> tuple[int, str, str]:
        if args == ["--help"]:
            return false_help
        return run_cli(args)

    with pytest.raises(AssertionError):
        _HELP.assert_root_help(run, "examples")
