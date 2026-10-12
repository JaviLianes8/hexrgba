# hexrgba guide

This guide states the exact rules `hexrgba` follows and where each one comes from. All
sources were fetched on 2026-10-12.

| Topic | Source |
| --- | --- |
| Hex syntax, named colors, `transparent`, serialization | [CSS Color Module Level 4](https://www.w3.org/TR/css-color-4/), Candidate Recommendation Draft of 9 October 2026, sections 5.2, 6.1, 6.3 and 16 |
| Golden parsing vectors | [Web Platform Tests `css/css-color/parsing`](https://github.com/web-platform-tests/wpt/tree/786385c76ca1c01d40eba0234dc59384e2eb73d4/css/css-color/parsing), commit `786385c` |
| Luminance and contrast | [WCAG 2.2](https://www.w3.org/TR/WCAG22/), Recommendation of 12 December 2024 |
| Blending | [Compositing and Blending Level 1](https://www.w3.org/TR/compositing-1/), section 5.1 |

## Parsing

`parse_color(text, *, strict=False)` returns a `Color`. It accepts:

- `#rgb`, `#rgba`, `#rrggbb` and `#rrggbbaa`. Short forms expand by doubling each digit,
  so `#123` is `#112233`. Without an alpha pair the color is opaque (alpha byte 255).
- The 148 keywords of the CSS named color table (it includes `rebeccapurple` and both
  spellings of every gray), and `transparent`, which is `rgba(0, 0, 0, 0)`.

Hex digits and keywords are **ASCII** case-insensitive: only `A` to `Z` fold. That matters
because Python's `str.lower()` folds more: the Kelvin sign `U+212A` lowers to `k`, so a
naive parser would accept `blac` + Kelvin sign as `black`. CSS rejects it, the WPT suite
tests it, and so does `hexrgba`.

| Mode | Leading `#` | Surrounding whitespace | Upper case |
| --- | --- | --- | --- |
| `strict=True` | required for hex | rejected | accepted (CSS is case-insensitive) |
| lenient (default) | optional | stripped | accepted |

No keyword is made only of hex digits, so lenient mode can never confuse a name with a
hash-less hex color; a test pins that.

`currentcolor`, system colors and the functional notations (`rgb()`, `hsl()`, `color()`)
are not accepted as input: they need a cascade or a much larger grammar.

The `0.1.0` functions (`is_hex`, `parse`, `normalize`, `to_hex`) keep their exact
behaviour: hex only, lenient, `(r, g, b, a)` tuples.

## Output

- `Color.hex` and `normalize()` give canonical lower-case `#rrggbb` when opaque and
  `#rrggbbaa` otherwise.
- `to_hex(short=True)`, `normalize(..., short=True)` and `shorten()` give `#rgb` or `#rgba`
  only when that is lossless (`#aabbcc` to `#abc`, `#aabbcd` stays long).
- `Color.to_css()` follows "CSS serialization of sRGB values" (section 16.2.2): `rgb(r, g, b)`
  when the alpha byte is 255, else `rgba(r, g, b, alpha)`, comma separated with one space.
  The WPT expected strings are used as the test oracle.
- `Color.name` gives the keyword for an exact match, or `None`. Where two keywords share a
  value (`aqua` and `cyan`, `fuchsia` and `magenta`, `gray` and `grey`) the first in the
  spec's alphabetical table wins.

## Alpha: 0..255 versus 0..1

The alpha is stored as a byte, `Color.a`, from 0 to 255. There are two float views and
one way back:

- `Color.alpha` is exactly `a / 255`.
- `css_alpha(a)` is the CSS legacy alpha string (section 16.1.1). If a whole percentage
  `n` satisfies `round(n * 2.55) == a`, the result is `n / 100` (237 gives `0.93`, 204
  gives `0.8`, 128 gives `0.5`). Otherwise it is `a / 0.255` rounded and divided by 1000
  (236 gives `0.925`). Halves round up. The arithmetic is exact, not binary floating point.
- `alpha_to_byte(x)` multiplies by 255 and rounds halves up. A float is read as its
  shortest decimal form, the number you typed: `0.3` is 76.5 and gives 77, where the
  binary value just below 0.3 would give 76.

**Round-trip contract**, tested for all 256 bytes:

```python
alpha_to_byte(a / 255) == a
alpha_to_byte(float(css_alpha(a))) == a
```

So `#rrggbbaa` to `Color.alpha` (or to the `rgba()` string) and back to hex is lossless.
The other direction cannot be: a byte has 256 values, so `alpha_to_byte(0.123)` gives 31,
and `css_alpha(31)` is `0.12`, which reads back as 31, not as 0.123.

One note on the spec: for byte 236 its prose example prints `0.92549`, but its own
numbered steps give `0.925`. `hexrgba` follows the numbered steps.

## Contrast

`relative_luminance(color)` is `0.2126 R + 0.7152 G + 0.0722 B` on linearized sRGB
channels, using the `0.04045` threshold of the current WCAG definition (older texts said
`0.03928`; no 8-bit value falls between the two, so results are identical). Alpha is
ignored.

`contrast_ratio(fg, bg)` is `(L1 + 0.05) / (L2 + 0.05)` with `L1` the lighter, from 1 to 21.
A translucent foreground is first blended over the background. The background must be
opaque, because what lies behind it is unknown.

`passes_contrast(fg, bg, level="AA", large=False)` compares without rounding, as WCAG
requires (4.499 fails 4.5):

| Level | Normal text | Large text |
| --- | --- | --- |
| AA (1.4.3) | 4.5 | 3 |
| AAA (1.4.6) | 7 | 4.5 |

The test suite checks the worked examples published by WCAG (for example `#949494` on
white is 3:1, `#E3660E` on white is 3.4:1). WCAG prints those with one decimal and does not
round consistently, so each is checked to within 0.1.

## Blending

`blend(fg, bg)` is source-over simple alpha compositing:

```
ao = as + ab (1 - as)
Co = (Cs as + Cb ab (1 - as)) / ao
```

It is computed with exact fractions and each channel is rounded to a byte once, halves
up. If both inputs are fully transparent the result is transparent black.

## Errors

All errors are `ValueError` subclasses, so `0.1.0` handlers keep working:

- `ColorError`: base class; also raised for a translucent contrast background.
- `HexColorError`: malformed hex, or a hash-less hex in strict mode.
- `ChannelError` (a `HexColorError`): a channel or alpha outside its range or of the
  wrong type, including booleans.
- `ColorNameError`: neither hex nor a known keyword.

`parse_color` raises `TypeError` for a non-string. `is_color` and `is_hex` never raise.

## Command line

```
hexrgba normalize COLOR [--short] [--strict]
hexrgba convert COLOR [--to hex|short|css|channels|name] [--strict]
hexrgba contrast FOREGROUND BACKGROUND [--level AA|AAA] [--large]
hexrgba blend FOREGROUND BACKGROUND
```

`contrast` prints the ratio truncated to two decimals (a failing 4.499 never shows as
4.50); with `--level` it exits 1 when the pair fails. Every failure, including usage
errors, prints to stderr and exits 1. Every example in `hexrgba --help` is executed by the
test suite and by the wheel end-to-end check.
