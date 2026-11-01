"""Build the wheel, install it in a throwaway venv and drive the installed command.

Run from anywhere: ``python scripts/e2e_wheel.py``. Exits 0 when every check passes.
Needs pip and network access for the build backend. Every example printed by
``hexrgba --help`` is executed against the installed script and must hold.
"""

from __future__ import annotations

import json
import os
import shlex
import subprocess
import sys
import tarfile
import tempfile
import zipfile
from email.parser import Parser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UPGRADE = ROOT / "scripts" / "upgrade_probe.py"


def run(cmd: list[str], *, cwd: Path, env: dict[str, str] | None = None) -> tuple[int, str, str]:
    done = subprocess.run(cmd, capture_output=True, cwd=cwd, env=env, check=False, timeout=600)
    return done.returncode, done.stdout.decode("utf-8"), done.stderr.decode("utf-8")


def check(label: str, condition: bool, detail: object = "") -> None:
    print(("ok   " if condition else "FAIL ") + label + ("" if condition else f": {detail!r}"))
    if not condition:
        raise SystemExit(1)


def help_examples(help_text: str) -> list[tuple[list[str], int, str]]:
    """Return (argv, exit code, stdout) for every ``hexrgba ... -> ...`` help line."""
    examples = []
    for line in help_text.splitlines():
        if not line.startswith("  hexrgba ") or "->" not in line:
            continue
        command, expected = (part.strip() for part in line.split("->", 1))
        code = 0
        if expected.startswith("exits 1:"):
            code, expected = 1, expected.removeprefix("exits 1:").split()[0]
        examples.append((shlex.split(command)[1:], code, expected))
    return examples


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="hexrgba-e2e-") as raw:
        work = Path(raw)
        dist = work / "dist"
        code, _, err = run(
            [sys.executable, "-m", "pip", "wheel", "--no-deps", "-w", str(dist), str(ROOT)],
            cwd=work,
        )
        check("wheel builds", code == 0, err[-2000:])
        wheel = next(dist.glob("hexrgba-*.whl"))
        names = zipfile.ZipFile(wheel).namelist()
        check("wheel ships py.typed", "hexrgba/py.typed" in names, names)
        check("wheel has no tests", not any(n.startswith(("tests/", "scripts/")) for n in names))
        check("wheel ships LICENSE", any(n.endswith("/licenses/LICENSE") for n in names), names)
        metadata_name = next(n for n in names if n.endswith("/METADATA"))
        metadata = Parser().parsestr(zipfile.ZipFile(wheel).read(metadata_name).decode())
        check("version metadata", metadata["Version"] == "1.0.0", metadata["Version"])
        check("Python floor", metadata["Requires-Python"] == ">=3.10")
        check(
            "no runtime dependencies",
            all("extra ==" in value for value in metadata.get_all("Requires-Dist", [])),
        )
        check(
            "stable classifier",
            "Development Status :: 5 - Production/Stable" in metadata.get_all("Classifier", []),
        )
        entry = [n for n in names if n.endswith("entry_points.txt")]
        text = zipfile.ZipFile(wheel).read(entry[0]).decode() if entry else ""
        check("console script declared", "hexrgba = hexrgba._cli:main" in text, text)

        code, _, err = run(
            [sys.executable, "-m", "build", "--sdist", "-o", str(dist), "."], cwd=ROOT
        )
        check("sdist builds", code == 0, err[-2000:])
        with tarfile.open(next(dist.glob("hexrgba-*.tar.gz"))) as sdist:
            members = [n.split("/", 1)[-1] for n in sdist.getnames()]
        check("sdist ships the manifest", "tests/upstream/MANIFEST.json" in members, members)
        check("sdist has no WPT page", not any(n.endswith(".html") for n in members), members)
        check(
            "sdist ships LICENSE and upgrade probe",
            "LICENSE" in members and "scripts/upgrade_probe.py" in members,
        )
        check(
            "sdist has no caches or work files",
            not any(
                part in {"__pycache__", ".pytest_cache", ".git", "scratch", "venv", "dist"}
                for name in members
                for part in name.split("/")
            ),
        )

        venv = work / "venv"
        check("venv created", run([sys.executable, "-m", "venv", str(venv)], cwd=work)[0] == 0)
        bindir = venv / ("Scripts" if os.name == "nt" else "bin")
        python = str(bindir / "python")
        if os.environ.get("HEXRGBA_E2E_PYPI") == "1":
            code, _, err = run([python, "-m", "pip", "install", "hexrgba==0.2.1"], cwd=work)
            check("PyPI 0.2.1 installs", code == 0, err[-2000:])
            probe = (
                "import hexrgba, pickle; from pathlib import Path; "
                "assert hexrgba.__version__ == '0.2.1'; "
                "assert hexrgba.parse('#1234') == (17, 34, 51, 68); "
                "Path('old.pickle').write_bytes(pickle.dumps(hexrgba.Color(1, 2, 3, 4)))"
            )
            check("PyPI baseline", run([python, "-I", "-c", probe], cwd=work)[0] == 0)
            code, before, err = run([python, "-I", str(UPGRADE)], cwd=work)
            check("PyPI consumer probe", code == 0, err)
        code, _, err = run(
            [python, "-m", "pip", "install", "--no-index", "--no-deps", str(wheel)], cwd=work
        )
        check("wheel installs", code == 0, err[-2000:])
        tool = str(bindir / "hexrgba")
        env = {"PATH": os.environ.get("PATH", ""), "SYSTEMROOT": os.environ.get("SYSTEMROOT", "")}

        code, out, _ = run([tool, "--version"], cwd=work, env=env)
        check("--version", code == 0 and out.strip() == "hexrgba 1.0.0", out)
        code, out, _ = run([tool, "--help"], cwd=work, env=env)
        check("--help shows examples", code == 0 and "examples" in out, out)
        examples = help_examples(out)
        check("help has examples", len(examples) >= 8, examples)
        for argv, want_code, want_out in examples:
            code, got, _ = run([tool, *argv], cwd=work, env=env)
            check(f"example {' '.join(argv)}", (code, got.strip()) == (want_code, want_out), got)

        code, out, err = run([tool, "normalize", "nope"], cwd=work, env=env)
        check("bad input exits 2 on stderr", (code, out) == (2, "") and "error" in err, err)
        code, out, _ = run([python, "-m", "hexrgba", "normalize", "BLACK"], cwd=work, env=env)
        check("python -m hexrgba", (code, out.strip()) == (0, "#000000"), out)
        probe = "import hexrgba; print(hexrgba.Color.parse('rebeccapurple').to_css())"
        code, out, _ = run([python, "-I", "-c", probe], cwd=work, env=env)
        check("library import", code == 0 and out.strip() == "rgb(102, 51, 153)", out)
        if os.environ.get("HEXRGBA_E2E_PYPI") == "1":
            code, after, err = run([python, "-I", str(UPGRADE)], cwd=work)
            check("upgraded consumer probe", code == 0, err)
            old, new = json.loads(before), json.loads(after)
            check("seeded API results unchanged", old["digest"] == new["digest"])
            check(
                "0.2.1 behavior recorded",
                old["changes"]
                == [
                    "AttributeError",
                    "AttributeError",
                    "True",
                    "ValueError",
                    "ValueError",
                    "Color",
                    "Color",
                    "hexrgba._color",
                ],
                old,
            )
            check(
                "documented 1.0.0 changes",
                new["changes"]
                == [
                    "False",
                    "TypeError",
                    "TypeError",
                    "TypeError",
                    "ChannelError",
                    "Shade",
                    "Shade",
                    "hexrgba",
                ],
                new,
            )
            probe = (
                "import hexrgba, pickle; from pathlib import Path; "
                "assert hexrgba.__version__ == '1.0.0'; "
                "assert hexrgba.parse('#1234') == (17, 34, 51, 68); "
                "assert pickle.loads(Path('old.pickle').read_bytes()) == hexrgba.Color(1, 2, 3, 4)"
            )
            check(
                "upgrade keeps values and pickles",
                run([python, "-I", "-c", probe], cwd=work)[0] == 0,
            )
    print("e2e: all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
