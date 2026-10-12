"""WCAG 2.2 relative luminance and contrast ratio.

Published examples are quoted from pages fetched 2026-10-12. WCAG prints ratios with one
decimal and is not consistent about rounding versus truncating (5.699 is printed 5.6,
1.185 is printed 1.2), so the check is that the exact ratio lies within 0.1 of it.
"""

import pytest

from hexrgba import ColorError, contrast_ratio, passes_contrast, relative_luminance

_NON_TEXT = "https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast"
_G183 = "https://www.w3.org/WAI/WCAG22/Techniques/general/G183"
_G207 = "https://www.w3.org/WAI/WCAG22/Techniques/general/G207"


@pytest.mark.parametrize(
    "fg,bg,published,source",
    [
        ("#949494", "white", 3.0, _NON_TEXT),
        ("#E5E5E5", "#6221EA", 5.6, _NON_TEXT),
        ("#FFF000", "white", 1.2, _NON_TEXT),
        ("#CCC", "#FFF", 1.6, _NON_TEXT),
        ("#3366CC", "#000000", 3.9, _G183),
        ("#E3660E", "#FFFFFF", 3.4, _G207),
    ],
)
def test_published_wcag_examples(fg: str, bg: str, published: float, source: str) -> None:
    assert abs(contrast_ratio(fg, bg) - published) < 0.1, source


def test_g183_link_color_claims_hold() -> None:
    # "3:1 contrast with black non-link text and 4.5:1 contrast with a white background"
    assert contrast_ratio("#3333FF", "#000000") >= 3
    assert contrast_ratio("#3333FF", "#FFFFFF") >= 4.5


def test_ratio_range_is_1_to_21() -> None:
    assert contrast_ratio("black", "white") == pytest.approx(21.0, abs=1e-12)
    assert contrast_ratio("#123456", "#123456") == 1.0


def test_ratio_is_symmetric_for_opaque_colors() -> None:
    assert contrast_ratio("navy", "gold") == contrast_ratio("gold", "navy")


def test_luminance_endpoints_and_channel_weights() -> None:
    assert relative_luminance("black") == 0.0
    assert relative_luminance("white") == pytest.approx(1.0, abs=1e-12)
    assert relative_luminance("#ff0000") == pytest.approx(0.2126)
    assert relative_luminance("#00ff00") == pytest.approx(0.7152)
    assert relative_luminance("#0000ff") == pytest.approx(0.0722)


def test_luminance_uses_the_linear_segment_below_the_threshold() -> None:
    assert relative_luminance("#0a0a0a") == pytest.approx((10 / 255) / 12.92)


def test_translucent_foreground_is_composited_first() -> None:
    assert contrast_ratio("#00000000", "white") == 1.0
    assert contrast_ratio("#000000ff", "white") == contrast_ratio("black", "white")


def test_translucent_background_is_rejected() -> None:
    with pytest.raises(ColorError, match="opaque"):
        contrast_ratio("black", "#ffffff80")


@pytest.mark.parametrize(
    "fg,level,large,expected",
    [
        ("#767676", "AA", False, True),
        ("#777777", "AA", False, False),
        ("#777777", "AA", True, True),
        ("#595959", "AAA", False, True),
        ("#767676", "AAA", False, False),
        ("#767676", "aaa", True, True),
    ],
)
def test_passes_contrast_thresholds(fg: str, level: str, large: bool, expected: bool) -> None:
    assert passes_contrast(fg, "white", level=level, large=large) is expected


def test_passes_contrast_rejects_unknown_levels() -> None:
    with pytest.raises(ValueError):
        passes_contrast("black", "white", level="A")
