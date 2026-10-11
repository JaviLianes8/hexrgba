# hexrgba

Parse, validate and normalize CSS hex colors with full alpha and shorthand support.

## Install

```
pip install hexrgba
```

## Usage

```python
from hexrgba import is_hex, parse, normalize, to_hex

is_hex("#f00")          # True
is_hex("red")           # False

parse("#f00")           # (255, 0, 0, 255)
parse("#ff000080")      # (255, 0, 0, 128)
parse("00ff00")         # (0, 255, 0, 255), the leading hash is optional

normalize("#F00")       # "#ff0000"
normalize("#ff000080")  # "#ff000080"

to_hex(255, 0, 128)     # "#ff0080"
to_hex(255, 0, 128, 64) # "#ff008040"
```

The four CSS forms (`#rgb`, `#rgba`, `#rrggbb`, `#rrggbbaa`) are all accepted, with or
without the leading hash and in any case. Shorthand expands by doubling each digit, so
`#abc` parses the same as `#aabbcc`. `normalize` returns the canonical lowercase form:
`#rrggbb` when the color is fully opaque, `#rrggbbaa` otherwise. Invalid input raises
`HexColorError`.

## Why

`webcolors` is built around the CSS named-color tables (turning `red` into a value and
back), and most other color packages pull in a wider model of color spaces. There was no
small, zero-dependency, typed helper that just does clean hex work: validating a string,
reading it into `(r, g, b, a)` integers, and round-tripping back to a canonical hex string
with correct alpha handling. That is all `hexrgba` does.

## License

MIT. See [LICENSE](LICENSE).

## Links

- Website: https://lianes8studio.com
- GitHub: https://github.com/JaviLianes8
- LinkedIn: https://www.linkedin.com/in/jlianes/
