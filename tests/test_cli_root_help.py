"""Root help descriptions must agree with each advertised command's behavior."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from hexrgba._cli import main

_SPEC = importlib.util.spec_from_file_location(
    "e2e_root_help", Path(__file__).parent.parent / "scripts" / "e2e_root_help.py"
)
assert _SPEC is not None and _SPEC.loader is not None
_HELP = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_HELP)


@pytest.mark.parametrize("topic", list(_HELP.CASES))
def test_root_help_matches_behavior(capsys: pytest.CaptureFixture[str], topic: str) -> None:
    def run(args: list[str]) -> tuple[int, str, str]:
        try:
            code = main(args)
        except SystemExit as exc:
            assert isinstance(exc.code, int)
            code = exc.code
        out, err = capsys.readouterr()
        return code, out, err

    _HELP.assert_root_help(run, topic)
