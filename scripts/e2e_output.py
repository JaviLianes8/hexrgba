"""Closed-output contracts for installed module and console entry points."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path


def check_closed_output(python: str, tool: str, work: Path, env: dict[str, str]) -> None:
    commands = [
        ["convert", "red"],
        ["--help"],
        ["--version"],
        *[[name, "--help"] for name in ("normalize", "convert", "contrast", "blend")],
    ]
    for unbuffered in (False, True):
        child_env = {**env, "PYTHONUNBUFFERED": "1" if unbuffered else ""}
        module = [python, "-I", *(["-u"] if unbuffered else []), "-m", "hexrgba"]
        for entry in ([tool], module):
            for args in commands:
                reader, writer = os.pipe()
                os.close(reader)
                try:
                    done = subprocess.run(
                        [*entry, *args],
                        stdout=writer,
                        stderr=subprocess.PIPE,
                        cwd=work,
                        env=child_env,
                        timeout=30,
                        check=False,
                    )
                finally:
                    os.close(writer)
                assert (done.returncode, done.stderr) == (1, b""), (
                    entry,
                    args,
                    unbuffered,
                    done.returncode,
                    done.stderr,
                )
