"""A watchdog protects the contract against blocking object representations."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def test_invalid_type_rejection_never_waits_for_repr() -> None:
    source = """
from threading import Event
from hexrgba import ChannelError, css_alpha

class Blocking:
    def __repr__(self):
        Event().wait()
        return 'unreachable'

try:
    css_alpha(Blocking())
except ChannelError:
    print('rejected')
"""
    done = subprocess.run(
        [sys.executable, "-c", source],
        env={**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[1] / "src")},
        capture_output=True,
        text=True,
        timeout=5,
        check=False,
    )
    assert (done.returncode, done.stdout.strip(), done.stderr) == (0, "rejected", "")
