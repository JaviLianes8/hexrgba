# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
