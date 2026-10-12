"""Seeded round-trip fuzz over the whole promise: every form parses back to itself."""

import random
import re

from hexrgba import (
    NAMED_COLORS,
    Color,
    alpha_to_byte,
    blend,
    contrast_ratio,
    css_alpha,
    is_color,
    is_hex,
    normalize,
    parse,
    parse_color,
    shorten,
)

_SEED = 20261012
_ROUNDS = 3000


def _colors() -> list[Color]:
    rng = random.Random(_SEED)
    return [Color(*(rng.randrange(256) for _ in range(4))) for _ in range(_ROUNDS)]


def _random_case(text: str, rng: random.Random) -> str:
    return "".join(ch.upper() if rng.random() < 0.5 else ch for ch in text)


def test_every_textual_form_parses_back_to_the_same_color() -> None:
    rng = random.Random(_SEED + 1)
    for color in _colors():
        forms = [color.hex, color.to_hex(short=True), _random_case(color.hex, rng)]
        forms.append(" " + color.hex[1:] + "\n")
        if color.name:
            forms.append(_random_case(color.name, rng))
        for form in forms:
            assert parse_color(form) == color, form


def test_canonical_forms_are_fixed_points() -> None:
    for color in _colors():
        assert normalize(color.hex) == color.hex
        assert shorten(shorten(color.hex)) == shorten(color.hex)
        assert parse_color(color.hex, strict=True).hex == color.hex
        assert is_hex(color.to_hex(short=True))


def test_float_alpha_and_css_alpha_round_trip() -> None:
    for color in _colors():
        assert Color.from_rgba(color.r, color.g, color.b, color.alpha) == color
        assert alpha_to_byte(float(css_alpha(color.a))) == color.a


def test_css_output_carries_the_exact_channels() -> None:
    for color in _colors():
        inner = color.to_css().split("(")[1].rstrip(")").split(", ")
        assert [int(v) for v in inner[:3]] == [color.r, color.g, color.b]
        if not color.is_opaque:
            assert alpha_to_byte(float(inner[3])) == color.a


def test_parse_and_parse_color_agree_on_hex() -> None:
    for color in _colors():
        assert parse(color.hex) == parse_color(color.hex).as_tuple()


def test_contrast_stays_in_range_and_blend_stays_opaque() -> None:
    colors = _colors()
    for fg, bg in zip(colors, reversed(colors), strict=True):
        backdrop = bg.with_alpha(1)
        assert 1.0 <= contrast_ratio(fg, backdrop) <= 21.0 + 1e-9
        assert blend(fg, backdrop).is_opaque


_STRICT_HEX = re.compile(r"#(?:[0-9A-Fa-f]{3,4}|[0-9A-Fa-f]{6}|[0-9A-Fa-f]{8})\Z")
_ALPHABET = "#0123456789abcdefABCDEFgGxXkK \t\n\u00a0\u212a\u0131-_.,()"
_KEYWORDS = [*NAMED_COLORS, "transparent"]


def _oracle(text: str) -> bool:
    folded = "".join(chr(ord(ch) + 32) if "A" <= ch <= "Z" else ch for ch in text)
    return bool(_STRICT_HEX.match(text)) or folded in _KEYWORDS


def _noise(rng: random.Random) -> str:
    if rng.random() < 0.4:
        base = list(rng.choice(_KEYWORDS))
        for _ in range(rng.randrange(3)):
            base.insert(rng.randrange(len(base) + 1), rng.choice(_ALPHABET))
        return "".join(base)
    return "".join(rng.choice(_ALPHABET) for _ in range(rng.randrange(10)))


def test_seeded_negative_fuzz_matches_the_css_grammar_oracle() -> None:
    rng = random.Random(_SEED + 1)
    samples = [_noise(rng) for _ in range(_ROUNDS * 3)]
    accepted = 0
    for text in samples:
        expected = _oracle(text)
        assert is_color(text, strict=True) is expected, repr(text)
        accepted += expected
    assert 0 < accepted < len(samples)
