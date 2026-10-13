# Improvements round

Progress:

- [x] 1. Brainstorm written (this file)
- [x] 2. Implement the ranked items on `improve/hexrgba-round` (additive API, 0.2.0)
- [x] 3. Command-line interface (`hexrgba normalize | convert | contrast | blend`)
- [x] 4. Gates green: `ruff format --check .`, `ruff check .`, `mypy --strict src`, `pytest`
- [x] 5. Contracts, spec and WPT vectors, WCAG examples, seeded fuzz, real wheel e2e
- [x] 6. Pull request opened (#2)
- [x] 7. Independent review findings fixed, gates re-run, pushed

Ranked, substantial improvements for `hexrgba`, measured against the `0.1.0` surface:
`is_hex`, `parse`, `normalize`, `to_hex` and `HexColorError`. Every item is additive:
code written against `0.1.0` keeps its exact behaviour.

## Ground truth used in this round

Every vector that claims an external origin is copied from the source as fetched on
2026-10-12, and the file that holds it names the URL. Third-party test pages are not
committed: `tests/upstream/MANIFEST.json` pins them and `scripts/fetch_upstream.py` fetches them.

- CSS Color Module Level 4, W3C Candidate Recommendation Draft of 9 October 2026,
  <https://www.w3.org/TR/css-color-4/>: section 5.2 (hex notation), section 6.1 (the
  148-row named color table) and section 6.3 (`transparent`), section 16 (serializing
  alpha and sRGB values).
- Web Platform Tests, `css/css-color/parsing`, commit
  `786385c76ca1c01d40eba0234dc59384e2eb73d4`:
  `color-computed-hex-color.html`, `color-invalid-hex-color.html`,
  `color-computed-named-color.html`, `color-invalid-named-color.html`,
  `color-valid.html`.
- WCAG 2.2, W3C Recommendation 12 December 2024, <https://www.w3.org/TR/WCAG22/>:
  the definitions of relative luminance and contrast ratio. Published worked examples
  from <https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast>,
  <https://www.w3.org/WAI/WCAG22/Techniques/general/G183> and
  <https://www.w3.org/WAI/WCAG22/Techniques/general/G207>.
- Compositing and Blending Level 1, <https://www.w3.org/TR/compositing-1/>, section 5.1
  (simple alpha compositing).

## Ranked items

1. **Named colors and `transparent`.** All 148 keywords of the CSS Color 4 table plus
   `transparent`, matched ASCII case-insensitively as the spec requires. Non-ASCII look-alikes
   (the Kelvin sign in `blacK`, a WPT vector) must be rejected, which a naive
   `str.lower()` gets wrong.
2. **A typed, frozen `Color`.** Integer channels 0 to 255, hashable, with `parse`,
   `from_rgba`, `hex`, `to_hex(short=...)`, `to_css()`, `name`, `alpha`, `with_alpha`.
3. **Strict versus lenient parsing.** Strict follows the CSS grammar exactly (leading `#`
   required, no surrounding whitespace, ASCII case-insensitive). Lenient, the default and
   the `0.1.0` behaviour, also takes a missing `#` and surrounding whitespace.
4. **Short form when lossless.** `#aabbcc` to `#abc`, `#aabbccdd` to `#abcd`.
5. **Exact alpha between 0..255 and 0..1.** `alpha_to_byte` and the CSS legacy alpha
   serialization (`css_alpha`) from section 16.1.1. Every byte round-trips through both
   the exact float `a / 255` and the serialized CSS string; the test is exhaustive.
6. **`rgb()` / `rgba()` output.** The CSS serialization of sRGB values (section 16.2.2),
   checked against the WPT expected strings.
7. **WCAG relative luminance and contrast ratio**, with `passes_contrast` for the AA and
   AAA thresholds of success criteria 1.4.3 and 1.4.6.
8. **Blending over a background** by simple alpha compositing, computed with exact
   fractions and rounded half up once.
9. **Typed errors.** `ColorError` base, `HexColorError`, `ColorNameError`, `ChannelError`,
   all still `ValueError`.
10. **CLI.** `hexrgba normalize`, `convert`, `contrast`, `blend`, plus `python -m hexrgba`.
11. **Docs.** Docstrings on every public name, a `GUIDE.md` with the alpha round-trip
    contract and the deviations from browser behaviour that are on purpose.

## Not in scope

`currentcolor`, system colors and the functional notations as input (`rgb()`, `hsl()`,
`color()`) depend on a cascade or a much larger grammar. They stay out to keep the library
small and exact.
