"""Every commented example in the README Python block is true."""

import ast
from pathlib import Path

_README = (Path(__file__).parent.parent / "README.md").read_text("utf-8")


def _python_block() -> list[str]:
    block = _README.split("```python\n", 1)[1].split("```", 1)[0]
    return [line for line in block.splitlines() if line.strip()]


def test_readme_examples_hold() -> None:
    namespace: dict[str, object] = {}
    checked = 0
    for line in _python_block():
        code, _, comment = line.partition("  # ")
        if code.startswith(("from ", "import ")) or "=" in code.split("(")[0]:
            exec(code, namespace)
            continue
        try:
            expected = ast.literal_eval(comment)
        except (ValueError, SyntaxError):
            assert eval(code, namespace) is not None
            continue
        assert eval(code, namespace) == expected, line
        checked += 1
    assert checked >= 9


def test_readme_contrast_example_is_accurate() -> None:
    namespace: dict[str, object] = {}
    exec("from hexrgba import contrast_ratio", namespace)
    assert str(eval('contrast_ratio("#767676", "white")', namespace)).startswith("4.54")
