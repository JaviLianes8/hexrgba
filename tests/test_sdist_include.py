"""Every script that a shipped test or script loads must itself ship in the sdist."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_LOADED = re.compile(r"""["']scripts["']\s*/\s*["'](\w+\.py)["']""")
_IMPORTED = re.compile(r"^\s*from\s+(\w+)\s+import\s", re.MULTILINE)


def sdist_include() -> set[str]:
    # A small reader keeps this runnable on 3.10, which has no tomllib.
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    block = text.split("[tool.hatch.build.targets.sdist]", 1)[1].split("]", 1)[0]
    return set(re.findall(r'"([^"]+)"', block))


def script_references(source: str, scripts: set[str]) -> set[str]:
    loaded = {f"scripts/{name}" for name in _LOADED.findall(source)}
    imported = {f"scripts/{name}.py" for name in _IMPORTED.findall(source)}
    return loaded | (imported & scripts)


def shipped_sources(include: set[str]) -> list[Path]:
    tests = sorted((ROOT / "tests").glob("*.py")) if "tests/*.py" in include else []
    scripts = [ROOT / entry for entry in sorted(include) if entry.startswith("scripts/")]
    return tests + [path for path in scripts if path.is_file()]


def test_reference_scanner_finds_loads_and_imports() -> None:
    # Built in pieces so this file does not itself reference a script.
    source = 'p = ROOT / "scr' + 'ipts" / "a.py"\n    from b import c\nfrom os import sep\n'
    found = script_references(source, {"scripts/a.py", "scripts/b.py"})
    assert found == {"scripts/a.py", "scripts/b.py"}


def test_every_referenced_script_ships_in_the_sdist() -> None:
    include = sdist_include()
    scripts = {f"scripts/{path.name}" for path in (ROOT / "scripts").glob("*.py")}
    missing = {
        f"{source.relative_to(ROOT).as_posix()} -> {ref}"
        for source in shipped_sources(include)
        for ref in script_references(source.read_text(encoding="utf-8"), scripts)
        if ref not in include
    }
    assert not missing, sorted(missing)
