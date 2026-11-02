"""Root and subcommand help must describe the supported command-line syntax."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from hexrgba._cli import main

_SPEC = importlib.util.spec_from_file_location(
    "e2e_help", Path(__file__).parent.parent / "scripts" / "e2e_help.py"
)
assert _SPEC is not None and _SPEC.loader is not None
_HELP = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_HELP)


@pytest.mark.parametrize("command", ["", "normalize", "convert", "contrast", "blend"])
def test_help_describes_supported_syntax(capsys: pytest.CaptureFixture[str], command: str) -> None:
    args = [command, "--help"] if command else ["--help"]
    with pytest.raises(SystemExit) as exc:
        main(args)
    out, err = capsys.readouterr()
    _HELP.assert_help(command, exc.value.code, out, err)
