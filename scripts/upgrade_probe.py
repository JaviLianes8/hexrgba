"""Compare deterministic consumer results before and after a wheel upgrade."""

from __future__ import annotations

import hashlib
import json
import random
from collections.abc import Callable

import hexrgba as h


def outcome(call: Callable[[], object]) -> str:
    try:
        value = call()
    except Exception as exc:
        return type(exc).__name__
    return str(value)


class Shade(h.Color):
    __slots__ = ()


def main() -> None:
    rng = random.Random(20261101)
    rows: list[object] = [list(h.NAMED_COLORS.items())]
    for name in (*h.NAMED_COLORS, "transparent"):
        color = h.parse_color(name)
        rows.append((color.as_tuple(), color.name, color.to_css(), h.is_color(name)))
    for _ in range(1000):
        channels = tuple(rng.randrange(256) for _ in range(4))
        color = h.Color(*channels)
        background = h.Color(*(rng.randrange(256) for _ in range(3)))
        rows.append(
            (
                color.as_tuple(),
                color.hex,
                color.name,
                color.alpha,
                color.is_opaque,
                color.to_css(),
                color.to_hex(short=True),
                h.to_hex(*channels),
                h.parse(color.hex),
                h.normalize(color.hex),
                h.shorten(color.hex),
                h.is_hex(color.hex),
                h.Color.parse(color.hex).as_tuple(),
                h.Color.from_rgba(*channels[:3], color.alpha).as_tuple(),
                color.with_alpha(0.3).as_tuple(),
                h.alpha_to_byte(color.alpha),
                h.css_alpha(color.a),
                h.blend(color, background).as_tuple(),
                h.relative_luminance(color),
                h.contrast_ratio(color, background),
                h.passes_contrast(color, background),
                h.passes_contrast(color, background, level="AAA", large=True),
            )
        )
    digest = hashlib.sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest()
    changes = [
        outcome(lambda: h.is_hex(None)),
        outcome(lambda: h.parse(None)),  # type: ignore[arg-type]
        outcome(lambda: h.passes_contrast("black", "white", large=1)),  # type: ignore[arg-type]
        outcome(lambda: h.passes_contrast("black", "white", level=None)),  # type: ignore[arg-type]
        outcome(lambda: h.Color(10**5000, 0, 0)),
        type(Shade.parse("red")).__name__,
        type(Shade(1, 2, 3).with_alpha(0.5)).__name__,
        h.Color.__module__,
    ]
    print(json.dumps({"digest": digest, "changes": changes}))


if __name__ == "__main__":
    main()
