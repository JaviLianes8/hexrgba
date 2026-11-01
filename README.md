# hexrgba

[![Lianes8 Certified](https://lianes8studio.com/certified/lianes8-certified-badge.svg)](https://lianes8studio.com/certified)

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
  whitespace). The default also accepts a missing `#` and strips surrounding
  Python whitespace (`str.strip()`).
- **A frozen `Color`** with `hex`, `to_hex(short=True)`, `to_css()`, `name`, `alpha`,
  `with_alpha()` and `from_rgba()`.
- **Exact alpha.** `alpha_to_byte` and `css_alpha` follow CSS Color 4; every alpha byte
  round-trips through its 0..1 float and through its CSS string.
- **WCAG 2.x** `relative_luminance`, `contrast_ratio` and `passes_contrast` (AA / AAA).
- **Blending** of a translucent color over a background with `blend`.
- **Typed value errors**: `ColorError`, `HexColorError`, `ColorNameError`, `ChannelError`.
  Wrong text argument types raise `TypeError`; predicates return `False`.

The full guide, with the exact rules and the sources they come from, is in
[GUIDE.md](https://github.com/JaviLianes8/hexrgba/blob/main/GUIDE.md).
See the [CHANGELOG](https://github.com/JaviLianes8/hexrgba/blob/main/CHANGELOG.md)
for the changes from 0.2.1.

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

Quote a leading `#`: most shells read it as the start of a comment. Errors go to stderr.
Exit codes: 0 success, 1 the pair fails `--level` or the output closes early,
2 bad usage or an invalid color. `python -m hexrgba` works too.

## Why

[webcolors](https://webcolors.readthedocs.io/en/latest/) provides CSS3 named-color
conversion; [Pillow](https://pillow.readthedocs.io/en/stable/reference/ImageColor.html)
parses colors as part of its image library. Use those when they already fit your project.
`hexrgba` brings hex and CSS Color 4 keywords, byte alpha serialization, WCAG contrast
and source-over blending together in a small typed library with no runtime dependencies.
It does not parse functional CSS input such as `rgb()` or implement other color spaces.

## Development

`pip install -e ".[dev]"` installs the development tools. `scripts/check.ps1` runs the
four gates. `python scripts/fetch_upstream.py` fetches the pinned specifications and
WPT files; their tests skip when absent. Set `HEXRGBA_UPSTREAM` to store them elsewhere.
Install `pillow webcolors wcag-contrast-ratio` to run the independent reference checks.
Set `HEXRGBA_E2E=1` for the wheel/CLI test and `HEXRGBA_E2E_PYPI=1` to include an
upgrade from PyPI 0.2.1. Set `TEMP` and `TMP` to a scratch directory and pass
`pytest --basetemp=PATH` to keep temporary files there.

## License

MIT. See [LICENSE](https://github.com/JaviLianes8/hexrgba/blob/main/LICENSE).

## Links

- Website: https://lianes8studio.com
- GitHub: https://github.com/JaviLianes8
- LinkedIn: https://www.linkedin.com/in/jlianes/
