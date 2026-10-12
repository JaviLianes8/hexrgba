"""Exact alpha conversion and the CSS Color 4 legacy alpha serialization (section 16.1.1).

Spec examples are quoted from https://www.w3.org/TR/css-color-4/ as fetched 2026-10-12.
"""

import pytest

from hexrgba import ChannelError, Color, alpha_to_byte, css_alpha


def test_every_byte_round_trips_through_the_exact_float() -> None:
    for byte in range(256):
        assert alpha_to_byte(byte / 255) == byte


def test_every_byte_round_trips_through_the_css_string() -> None:
    for byte in range(256):
        assert alpha_to_byte(float(css_alpha(byte))) == byte


def test_every_whole_percentage_serializes_with_two_decimals_at_most() -> None:
    # "must at least be sufficient to round-trip integer percentage values"
    for percent in range(101):
        byte = (percent * 255 + 50) // 100  # round(percent * 2.55), halves up, exactly
        assert float(css_alpha(byte)) == percent / 100


def test_spec_example_237_is_0_93() -> None:
    assert css_alpha(237) == "0.93"


def test_spec_steps_give_236_three_decimals() -> None:
    # 236 / 0.255 = 925.49..., rounded to 925, divided by 1000. The spec's prose example
    # prints "0.92549", which does not follow its own numbered steps; the steps win.
    assert css_alpha(236) == "0.925"


def test_spec_example_0000ffcc_is_80_percent() -> None:
    assert Color.parse("#0000ffcc").to_css() == "rgba(0, 0, 255, 0.8)"


def test_spec_example_ff00ffed_serializes_as_0_93() -> None:
    assert Color.parse("#ff00ffed").to_css() == "rgba(255, 0, 255, 0.93)"


@pytest.mark.parametrize(
    "byte,text", [(0, "0"), (255, "1"), (128, "0.5"), (127, "0.498"), (1, "0.004"), (26, "0.1")]
)
def test_css_alpha_values(byte: int, text: str) -> None:
    assert css_alpha(byte) == text


def test_css_alpha_never_has_trailing_zeros_or_a_bare_point() -> None:
    for byte in range(256):
        text = css_alpha(byte)
        assert not text.endswith(".") and not (("." in text) and text.endswith("0"))
        assert len(text.partition(".")[2]) <= 3


@pytest.mark.parametrize(
    "alpha,byte", [(0.5, 128), (0.0, 0), (1, 255), (0.8, 204), (0, 0), (0.3, 77), (0.7, 179)]
)
def test_alpha_to_byte_rounds_half_up(alpha: float, byte: int) -> None:
    assert alpha_to_byte(alpha) == byte


@pytest.mark.parametrize("bad", [-0.01, 1.01, float("nan"), float("inf"), True, "0.5", None])
def test_alpha_to_byte_rejects_bad_values(bad: object) -> None:
    with pytest.raises(ChannelError):
        alpha_to_byte(bad)  # type: ignore[arg-type]


@pytest.mark.parametrize("bad", [-1, 256, 1.5, True])
def test_css_alpha_rejects_non_bytes(bad: object) -> None:
    with pytest.raises(ChannelError):
        css_alpha(bad)  # type: ignore[arg-type]
