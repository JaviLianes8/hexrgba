"""WCAG 2.2 luminance, contrast and thresholds read out of the fetched W3C pages.

The pages are fetched by `python scripts/fetch_upstream.py` (dated WCAG 2.2 snapshot and the
w3c/wcag commit pinned in tests/upstream/MANIFEST.json, fetched 2026-10-23); these tests
skip until then.
"""

from __future__ import annotations

import math
import re
from fractions import Fraction

import pytest
from spec_text import number, plain

from hexrgba import contrast_ratio
from hexrgba import relative_luminance as luminance
from hexrgba._wcag import _THRESHOLDS

WCAG = "wcag22-20241212.html"


def test_relative_luminance_matches_the_formula_in_the_wcag_text() -> None:
    text = plain(WCAG)
    weights = number(r"L = ([\d.]+) \* R \+ ([\d.]+) \* G \+ ([\d.]+) \* B", text)
    cut, slope, offset, scale, power = number(
        r"if RsRGB <= ([\d.]+) then R = RsRGB/([\d.]+) else R = "
        r"\(\(RsRGB\+([\d.]+)\)/([\d.]+)\) \^ ([\d.]+)",
        text,
    )

    def linear(byte: int) -> float:
        unit = Fraction(byte, 255)
        if unit <= cut:
            return float(unit / slope)
        return math.pow(float((unit + offset) / scale), float(power))

    for byte in range(256):
        for channel in range(3):
            rgb = [0, 0, 0]
            rgb[channel] = byte
            want = float(weights[channel]) * linear(byte)
            got = luminance(f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}")
            assert got == pytest.approx(want, rel=1e-12, abs=1e-15), (channel, byte)


def test_contrast_ratio_matches_the_wcag_definition() -> None:
    text = plain(WCAG)
    (bias, other) = number(r"contrast ratio \(L1 \+ ([\d.]+)\) / \(L2 \+ ([\d.]+)\)", text)
    assert bias == other
    assert "Contrast ratios can range from 1 to 21" in text
    for fg, bg in [("#767676", "white"), ("navy", "gold"), ("#123", "#fedcba"), ("red", "lime")]:
        lighter, darker = sorted((luminance(fg), luminance(bg)), reverse=True)
        want = (lighter + float(bias)) / (darker + float(bias))
        assert contrast_ratio(fg, bg) == pytest.approx(want, rel=1e-12)


def test_text_thresholds_are_the_ones_of_criteria_1_4_3_and_1_4_6() -> None:
    text = plain(WCAG)
    rule = (
        r"has a contrast ratio of at least ([\d.]+):1, except for the following: Large Text"
        r" Large-scale text and images of large-scale text have a contrast ratio of at least"
        r" ([\d.]+):1"
    )
    found = [tuple(Fraction(v) for v in pair) for pair in re.findall(rule, text)]
    assert found[:2] == [(Fraction(9, 2), 3), (7, Fraction(9, 2))]
    for (normal, large), level in zip(found[:2], ("AA", "AAA"), strict=True):
        assert _THRESHOLDS[(level, False)] == normal and _THRESHOLDS[(level, True)] == large


NTC = "wcag-understanding-non-text-contrast.html"
EXAMPLES = [
    (NTC, "grey #949494 against white, with a contrast ratio of 3:1", "#949494", "white", 3.0),
    (
        NTC,
        "light grey check (#E5E5E5), which has a contrast ratio of 5.6:1 with the purple box"
        " (#6221EA)",
        "#E5E5E5",
        "#6221EA",
        5.6,
    ),
    (NTC, "the yellow (#FFF000) to white contrast ratio of 1.2:1", "#FFF000", "white", 1.2),
    (
        NTC,
        "gray (#CCC) outline has an insufficient contrast of 1.6:1 against the white (#FFF)",
        "#CCC",
        "#FFF",
        1.6,
    ),
    (
        "wcag-technique-G183.html",
        "medium-light blue (#3366CC) and the regular text is black (#000000)",
        "#3366CC",
        "#000000",
        3.9,
    ),
    (
        "wcag-technique-G207.html",
        "orange (#E3660E) is tested against the white background (#FFFFFF) and it has a"
        " contrast ratio of 3.4:1",
        "#E3660E",
        "#FFFFFF",
        3.4,
    ),
]


@pytest.mark.parametrize(("page", "sentence", "fg", "bg", "ratio"), EXAMPLES)
def test_published_examples_are_in_the_fetched_pages(
    page: str, sentence: str, fg: str, bg: str, ratio: float
) -> None:
    text = plain(page)
    assert sentence in text and f"{ratio:g}:1" in text
    # The pages print one decimal and round or truncate inconsistently: within 0.1.
    assert abs(contrast_ratio(fg, bg) - ratio) < 0.1
