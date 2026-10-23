"""Independent implementations as oracles, each run live when it is installed.

- Pillow ``ImageColor.getrgb`` (https://pypi.org/project/pillow/) reads all four hex forms.
- webcolors (https://pypi.org/project/webcolors/) holds its own CSS3 named color table.
- wcag-contrast-ratio 0.9 (https://pypi.org/project/wcag-contrast-ratio/) computes the
  WCAG ratio with its own code (and the older 0.03928 threshold, which no 8-bit value
  falls between).

Each test skips when its package is absent; `pip install pillow webcolors
wcag-contrast-ratio` runs them all.
"""

from __future__ import annotations

import random

import pytest

from hexrgba import NAMED_COLORS, Color, contrast_ratio, is_hex, parse, passes_contrast

_SEED = 20261023


def _hex_cases(rng: random.Random, count: int) -> list[str]:
    digits = "0123456789abcdefABCDEF"
    return [
        "#" + "".join(rng.choice(digits) for _ in range(rng.randrange(11))) for _ in range(count)
    ]


def test_hex_parsing_agrees_with_pillow() -> None:
    image_color = pytest.importorskip("PIL.ImageColor")
    rng = random.Random(_SEED)
    accepted = 0
    for text in _hex_cases(rng, 20_000):
        try:
            theirs = image_color.getrgb(text)
        except ValueError:
            assert not is_hex(text), text
            continue
        accepted += 1
        ours = parse(text)
        assert theirs == (ours if len(theirs) == 4 else ours[:3]), text
    assert 5_000 < accepted < 20_000


def test_named_colors_agree_with_webcolors() -> None:
    webcolors = pytest.importorskip("webcolors")
    names = webcolors.names("css3")
    # Its CSS3 table predates rebeccapurple, which CSS Color 4 added; every other row agrees.
    assert sorted(names) == sorted(set(NAMED_COLORS) - {"rebeccapurple"})
    for name in names:
        assert webcolors.name_to_hex(name, spec="css3") == NAMED_COLORS[name], name


def test_contrast_agrees_with_wcag_contrast_ratio() -> None:
    oracle = pytest.importorskip("wcag_contrast_ratio")
    rng = random.Random(_SEED + 1)
    pairs = [(Color(v, v, v), Color(255, 255, 255)) for v in range(256)]
    pairs += [
        (
            Color(*(rng.randrange(256) for _ in range(3))),
            Color(*(rng.randrange(256) for _ in range(3))),
        )
        for _ in range(20_000)
    ]
    for fg, bg in pairs:
        theirs = oracle.rgb(
            [c / 255 for c in fg.as_tuple()[:3]], [c / 255 for c in bg.as_tuple()[:3]]
        )
        ours = contrast_ratio(fg, bg)
        assert ours == pytest.approx(theirs, rel=1e-12, abs=0), (fg, bg)
        assert passes_contrast(fg, bg) is oracle.passes_AA(theirs), (fg, bg)
        assert passes_contrast(fg, bg, level="AAA", large=True) is oracle.passes_AAA(
            theirs, large=True
        )
