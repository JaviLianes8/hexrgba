# hexrgba

Parse, validate and normalize CSS hex colors and named colors, with exact alpha handling,
CSS `rgb()` / `rgba()` output, WCAG contrast and alpha blending. Typed, zero dependencies.

## Install

```
pip install hexrgba
```

## Usage

```python
from hexrgba import Color, contrast_ratio, is_hex, normalize, parse, parse_color, to_hex

is_hex("#f00")  # True
parse("#ff000080")  # (255, 0, 0, 128)
normalize("#F00")  # "#ff0000"
normalize("#AABBCC", short=True)  # "#abc"
to_hex(255, 0, 128, 64)  # "#ff008040"

color = parse_color("RebeccaPurple")  # Color(r=102, g=51, b=153, a=255)
color.hex  # "#663399"
color.to_css()  # "rgb(102, 51, 153)"
parse_color("#ff00ffed").to_css()  # "rgba(255, 0, 255, 0.93)"
parse_color("#00ffff").name  # "aqua"
Color.from_rgba(255, 0, 0, 0.5).hex  # "#ff000080"

contrast_ratio("#767676", "white")  # 4.54...
```

What it covers:

- **All four hex forms** (`#rgb`, `#rgba`, `#rrggbb`, `#rrggbbaa`) and **all 148 CSS named
  colors** plus `transparent`, matched ASCII case-insensitively as CSS requires.
- **Strict or lenient.** `strict=True` follows the CSS grammar (leading `#`, no surrounding
  whitespace). The default also accepts a missing `#` and surrounding whitespace.
- **A frozen `Color`** with `hex`, `to_hex(short=True)`, `to_css()`, `name`, `alpha`,
  `with_alpha()` and `from_rgba()`.
- **Exact alpha.** `alpha_to_byte` and `css_alpha` follow CSS Color 4; every alpha byte
  round-trips through its 0..1 float and through its CSS string.
- **WCAG 2.x** `relative_luminance`, `contrast_ratio` and `passes_contrast` (AA / AAA).
- **Blending** of a translucent color over a background with `blend`.
- **Typed errors**, all `ValueError`: `ColorError`, `HexColorError`, `ColorNameError`,
  `ChannelError`.

The full guide, with the exact rules and the sources they come from, is in
[GUIDE.md](GUIDE.md).

## Command line

```
hexrgba normalize "#FFAA00"            # #ffaa00
hexrgba normalize "#aabbcc" --short    # #abc
hexrgba convert "#ff00ffed" --to css   # rgba(255, 0, 255, 0.93)
hexrgba convert "#00ffff" --to name    # aqua
hexrgba contrast "#767676" white       # 4.54:1
hexrgba contrast "#777" white --level AA   # prints 4.47:1, exits 1
hexrgba blend "#0000ff80" red          # #7f0080
```

Quote a leading `#`: most shells read it as the start of a comment. Errors go to stderr
with exit code 1. `python -m hexrgba` works too.

## Why

`webcolors` is built around the CSS named-color tables, and most other color packages pull
in a wider model of color spaces. `hexrgba` stays small and exact: the hex and keyword
syntax of CSS, checked against the spec tables and the Web Platform Tests vectors, an
alpha conversion that never drifts, and the WCAG contrast math, with no dependencies.

## License

MIT. See [LICENSE](LICENSE).

## Links

- Website: https://lianes8studio.com
- GitHub: https://github.com/JaviLianes8
- LinkedIn: https://www.linkedin.com/in/jlianes/
