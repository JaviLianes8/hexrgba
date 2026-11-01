"""The command line under hostile use: huge arguments and an output that closes early."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

from hexrgba._cli import main

SRC = str(Path(__file__).resolve().parents[1] / "src")


@pytest.mark.parametrize(
    "args",
    [
        ["convert", "red", "--to", "x" * 1_000_000],
        ["contrast", "red", "blue", "--level", "A" * 1_000_000],
        ["y" * 1_000_000],
        ["normalize", "red", "--" + "z" * 1_000_000],
        ["normalize", "red", "extra", *(["w" * 1000] * 1000)],
    ],
)
def test_usage_errors_omit_huge_arguments(
    capsys: pytest.CaptureFixture[str], args: list[str]
) -> None:
    with pytest.raises(SystemExit) as exc:
        main(args)
    assert exc.value.code == 2
    err = capsys.readouterr().err
    assert err.splitlines()[-1].endswith(
        "error: invalid command or arguments; use --help for syntax and choices"
    )


@pytest.mark.parametrize("command", ["normalize", "convert", "blend", "contrast"])
def test_a_huge_color_gives_a_short_error_in_every_command(
    capsys: pytest.CaptureFixture[str], command: str
) -> None:
    args = [command, "#" + "f" * 1_000_000] + (["red"] if command in ("blend", "contrast") else [])
    assert main(args) == 2
    out, err = capsys.readouterr()
    assert out == "" and len(err) < 200 and err.startswith("hexrgba: error:")


@pytest.mark.parametrize(
    "args",
    [["convert", "red"], ["--help"], ["--version"], ["normalize", "--help"]],
)
def test_a_closed_output_exits_1_quietly(args: list[str]) -> None:
    read_end, write_end = os.pipe()
    os.close(read_end)
    try:
        done = subprocess.run(
            [sys.executable, "-m", "hexrgba", *args],
            stdout=write_end,
            stderr=subprocess.PIPE,
            env={**os.environ, "PYTHONPATH": SRC},
            timeout=120,
            check=False,
        )
    finally:
        os.close(write_end)
    assert (done.returncode, done.stderr) == (1, b"")
