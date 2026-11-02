# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2026-11-01

### Stable

- The 19-name public API: hex and CSS named colors, immutable `Color`, exact byte
  alpha conversions, CSS serialization, WCAG contrast, blending and typed value errors.
- Python 3.10 through 3.14, zero runtime dependencies, and the four CLI commands.

### Changed

- `is_hex` returns `False` for non-strings. Text parsers (`parse`, `parse_color`,
  `normalize`, `shorten`, `Color.parse`, and color-taking helpers) raise `TypeError`
  for wrong argument types rather than accidental `AttributeError`.
- String and numeric subclasses are read through their underlying built-in values;
  `Color` stores plain `int` channels. Their overridden conversion, comparison or
  formatting methods no longer change results.
- `passes_contrast` rejects a non-string `level` and non-boolean `large` with
  `TypeError`; unknown string levels still raise `ValueError`.
- Error messages describe expected types, ranges and syntax without echoing input
  values or custom type names. This replaces truncated representation previews and
  integer bit lengths. Rejection never calls `repr` or traverses container contents.
- Type validation uses actual types without calling instance `__class__` hooks;
  genuine numeric and string subclasses retain their underlying built-in behavior.
- `Color` and the error classes identify and pickle as public `hexrgba` names;
  pickles written by 0.2.1 remain readable.
- `Color.parse` and `with_alpha` preserve a `Color` subclass instead of returning
  the base `Color`. Predicates are typed to accept `object` to match their runtime use.
- CLI usage errors omit argument contents and point to `--help` for syntax and choices.
  A closed output exits 1 without a traceback, including `--help` and `--version`.
- Unbuffered help and version output also exits 1 quietly on a closed pipe, including
  every subcommand's help through the module and installed console entry points.

### Clarified

- `blend` returns a new base `Color` with the composited RGBA channels; it does not
  reuse operands or preserve their subclasses.
- Translucent contrast uses ideal source-over arithmetic rounded once to bytes.
  Browser rendering may differ, including AA/AAA decisions near thresholds.

### Verified

- Runnable public examples, strict typing, specification and reference checks,
  seeded fuzz, wheel/CLI installation and upgrade, and mutation-tested contracts.
- Exact explicit opaque-alpha formatting, strict parsing through `Color` subclasses,
  alpha-independent luminance, and diagnostics at the former preview boundaries.
- Fresh base `Color` results for opaque and transparent blends, underlying string
  values despite `__str__` overrides, and private strict-hex and unnamed-color errors.
- Root and subcommand help syntax, required operands, flags and supported choices,
  including successful output through both installed entry points with empty stderr.

## [0.2.1] - 2026-10-13

### Changed

- The Web Platform Tests color parsing pages are no longer committed or shipped in the
  sdist: `scripts/fetch_upstream.py` fetches them at a pinned commit, checked against
  `tests/upstream/MANIFEST.json`, and hand-written cases keep the default suite meaningful
  without them.

## [0.2.0] - Unreleased

### Added

- `parse_color` and `is_color`: hex colors plus all 148 CSS named colors and
  `transparent`, matched ASCII case-insensitively, with a `strict` mode that follows the
  CSS grammar exactly.
- `Color`, a frozen, hashable value type with `hex`, `to_hex(short=...)`, `to_css()`,
  `name`, `alpha`, `is_opaque`, `with_alpha()`, `from_rgba()` and `as_tuple()`.
- `NAMED_COLORS`, the read-only CSS Color 4 named color table.
- `alpha_to_byte` and `css_alpha`: exact alpha conversion and the CSS legacy alpha
  serialization; every alpha byte round-trips through both.
- `shorten` and `normalize(..., short=True)` for the lossless `#rgb` / `#rgba` form.
- `relative_luminance`, `contrast_ratio` and `passes_contrast` (WCAG 2.x, AA and AAA).
- `blend`, simple alpha compositing of one color over another.
- `ColorError`, `ColorNameError` and `ChannelError`. `HexColorError` is now a
  `ColorError`, still a `ValueError`.
- The `hexrgba` command (`normalize`, `convert`, `contrast`, `blend`) and `python -m hexrgba`.
- `GUIDE.md`, with the exact rules and their sources.

## [0.1.0]

- First release: `is_hex`, `parse`, `normalize`, `to_hex` and `HexColorError`.
- Support for `#rgb`, `#rgba`, `#rrggbb` and `#rrggbbaa`, with optional leading hash,
  any case, shorthand expansion and alpha round-tripping.
