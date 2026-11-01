# hexrgba 1.0.0 certification report

Preparation date: 2026-11-01. PyPI currently publishes 0.2.1 (JSON endpoint checked
live). The existing three release commits were retained. Main is `8619b02`.

Progress:
- [x] Stable API, exact exports, runnable examples, typed bounded errors (items 1-5)
- [x] Contracts, fetched specifications, reference implementations and seeded fuzz (6, 7, 9)
- [x] README, GUIDE, dated CHANGELOG and production metadata (11-13)
- [x] Wheel/CLI e2e, upgrade from PyPI 0.2.1, distribution inspection (8, 14)
- [x] Available interpreter matrix (10)
- [x] Four gates (15), plus strict types for tests
- [x] Mutation round (18)
- [ ] Independent reviewer (16)
- [ ] Five QA lenses (19)
- [x] PR handoff: [#4](https://github.com/JaviLianes8/hexrgba/pull/4); merge and publication remain pending

## API and compatibility

The 19 exports retain their parameter names, defaults and valid-input behavior.
`tests/test_contract_api.py` pins signatures, fields, immutability, subclass behavior,
pickle/copy support, error inheritance and examples. The CHANGELOG lists all changes
from 0.2.1, including argument errors, built-in subclass normalization, public pickle
names, subclass preservation and bounded CLI errors. Public values contain no `Any`.
An external consumer of the installed wheel also passes `mypy --strict`.

## Preparation scorecard

| Item | Status | Evidence |
| --- | --- | --- |
| 1 | PASS | Stable parameters/defaults; intentional changes in CHANGELOG and upgrade probe |
| 2 | PASS | Exact `__all__`, no other public attributes; tests pin the 19 names |
| 3 | PASS | Public function, class and method doctests; mapping example in package docs |
| 4 | PASS | Strict mypy on source/tests and installed consumer; `py.typed` in wheel |
| 5 | PASS | Typed errors, bounded messages, wrong-type and hostile-object contracts |
| 6 | PASS | Behavioral contracts for every export, CLI and Color member |
| 7 | PASS | Eleven re-fetched sources and three independently implemented libraries |
| 8 | PASS | Installed wheel, CLI subprocesses, in-place upgrade and old pickle |
| 9 | PASS | Seeded positive/negative fuzz, million-character input and scaling checks |
| 10 | PASS | All twelve available CPython builds; installed-wheel matrix below |
| 11 | PASS | Problem, scope, alternatives, absolute links, examples and twine check |
| 12 | PASS | CHANGELOG 1.0.0 dated 2026-11-01 |
| 13 | PASS | Production/Stable, 1.0.0, accurate Python floor/classifiers and project URLs |
| 14 | PASS | Wheel and sdist contents inspected, LICENSE present, no downloaded text |
| 15 | PASS | Four gates exit 0 independently; full suite 353 passed |
| 16 | Pending | Independent reviewer has not run |
| 17 | Ready | PR #4 from release/1.0.0 to main; merge and publication pending |
| 18 | PASS | Fifteen deliberate bugs killed; table below |
| 19 | Pending | Round 1: all five lenses reported findings; fixes below await re-review |

## Ground truth

All 11 entries of `tests/upstream/MANIFEST.json` were fetched in this session on
2026-11-01 with `scripts/fetch_upstream.py`; sizes and SHA-256 matched. Downloads stay
outside the distribution. `HEXRGBA_UPSTREAM` selects their local directory.

- CSS Color 4: https://www.w3.org/TR/2026/CRD-css-color-4-20261022/
  The 148-row table, allowed hex lengths and all 256 alpha serializations are checked
  against facts and formulas read from the fetched text.
- WCAG 2.2: https://www.w3.org/TR/2024/REC-WCAG22-20241212/
  Tests extract luminance coefficients, transfer function, contrast bias and thresholds;
  all 256 byte values in each channel are checked. Three WCAG example pages are also
  fetched at the manifest's pinned w3c/wcag commit and their examples checked.
- Compositing: https://www.w3.org/TR/2024/CRD-compositing-1-20240321/
  The source-over formulas are located in the fetched text; rational behavior tests
  cover opaque, transparent and half-alpha combinations.
- Five WPT files at commit `786385c76ca1c01d40eba0234dc59384e2eb73d4` are parsed
  directly by the tests. Exact raw URLs, licenses, hashes and sizes are in the manifest.
- Live references: Pillow 13.0.0 (20,000 seeded hex strings), webcolors 25.10.0 (all
  147 CSS3 keywords), wcag-contrast-ratio 0.9 (20,256 opaque pairs). All agree.
  Sources: https://pypi.org/project/pillow/, https://pypi.org/project/webcolors/,
  https://pypi.org/project/wcag-contrast-ratio/ (installed and run 2026-11-01).

## Checks completed

`ruff format --check .`, `ruff check .`, `mypy --strict src`, `mypy --strict src tests`
and `pytest` each exit 0. With `HEXRGBA_E2E=1` and `HEXRGBA_E2E_PYPI=1`, the suite
passes all 353 tests in 56.35 seconds. Every test has a 300-second limit.

The e2e script builds both distributions, installs the wheel in a fresh venv, executes
all ten help examples through the installed console script, checks invalid input and
`python -m hexrgba`, imports with `-I`, then confirms upgrade values and an old pickle.
The upgrade probe compares all 149 keywords and 1,000 seeded RGBA/background pairs
across the API (22 outputs per pair), plus eight explicit changed behaviors against
the installed 0.2.1 release. All stable results match and all eight changes are confirmed.
Both distributions pass `twine check --strict`. The wheel contains only the package,
typing marker and distribution metadata including LICENSE. The sdist contains source,
tests, the derived color table, manifest, three test utilities, README, GUIDE, CHANGELOG,
LICENSE and pyproject; no fetched pages, caches or scratch files.

Seeded tests cover 3,000 random RGBA values and 9,000 hostile strings; additional
million-character inputs verify bounded errors and linear scaling. Numeric and string
subclasses, unprintable objects, huge integers and closed CLI output are covered.

## Mutation round (item 18)

Each change was applied alone in a separate scratch copy. The unchanged contract suite
ran with `pytest tests -x`, no bytecode, and a 300-second timeout per test. All 15 real
bugs were killed by assertion failures, not by collection or syntax failures.

| ID | Injected bug | Test that failed |
| --- | --- | --- |
| M01 | Missing alpha becomes 254 | `test_blend_accepts_color_objects_and_names` |
| M02 | Shorthand appends zero instead of repeating digit | `test_serializes_like_css_color_4` |
| M03 | Red and blue swapped | `test_spec_example_0000ffcc_is_80_percent` |
| M04 | Boolean channels accepted | `test_css_alpha_rejects_non_bytes` |
| M05 | Normalization drops alpha 254 | `test_every_textual_form_parses_back_to_the_same_color` |
| M06 | Alpha conversion truncates instead of rounding | `test_every_byte_round_trips_through_the_exact_float` |
| M07b | Omit percentage 99 from CSS serialization search | `test_every_whole_percentage_serializes_with_two_decimals_at_most` |
| M08 | Strict parser permits surrounding whitespace | `test_surrounding_space_is_lenient_only` |
| M09 | Unicode case-folding accepts Kelvin-sign keyword | `test_rejected_in_both_modes` |
| M10 | Alpha divides by 256 | `test_alpha_float_is_exact_byte_over_255` |
| M11 | Blending ignores foreground | `test_opaque_foreground_wins_and_transparent_foreground_vanishes` |
| M12 | Red luminance weight 0.2127 | `test_contrast_agrees_with_wcag_contrast_ratio` |
| M13 | Translucent contrast background accepted | `test_errors_go_to_stderr_with_exit_2` |
| M14 | ChannelError loses HexColorError inheritance | `test_error_hierarchy_keeps_value_error` |
| M15 | CLI invalid input exits 1 | `test_errors_go_to_stderr_with_exit_2` |

One additional candidate, M07, removed only percentage 100. Exhaustive comparison of
all 256 valid bytes proved it equivalent: the fallback also emits `1` for byte 255.
It is excluded from the 15 bugs above; M07b removes percentage 99 as well and is killed.

## Installed interpreter matrix (item 10)

Tests and docs were extracted from the sdist without its `src` directory. Each
interpreter loaded the installed wheel in an isolated environment and ran the full
suite, package doctests and a CLI subprocess from that external directory. The single
skip is the build/e2e test, run separately with all 353 tests above. All fetched sources
and the three reference libraries were present. Embedded interpreters were copied to
scratch and given isolated package directories; other runtimes used fresh venvs.

| CPython | Passed | Skipped |
| --- | --- | --- |
| 3.10.11 (embedded) | 352 | 1 |
| 3.10.22 | 352 | 1 |
| 3.11.9 (embedded) | 352 | 1 |
| 3.11.11 (Blender runtime) | 352 | 1 |
| 3.11.18 | 352 | 1 |
| 3.12.10 (embedded) | 352 | 1 |
| 3.12.16 | 352 | 1 |
| 3.13.2 (embedded) | 352 | 1 |
| 3.13.18 | 352 | 1 |
| 3.14.6 | 352 | 1 |
| 3.14.10 | 352 | 1 |
| 3.14.10 free-threaded | 352 | 1 |

The launcher also listed obsolete paths that no longer exist; filesystem discovery
found the twelve distinct builds above. No supported minor version was unavailable.
The package files in the final wheel are byte-identical to the initial matrix wheel.
Initial launcher/dependency setup failures were corrected before these passing runs.

Final wheel SHA-256: `88288bbba6982a07ff6363373c01358eb0d73d04a27a7079b45b820bc78529e0`.
Final sdist SHA-256: `5222b7ca7976f1ad327f5c26d042ed7735c5f1e41835d870a5770a734d032372`.

## QA round 1: findings and fixes

Date: 2026-11-01. Reviewed head: `2d8e92f91948ad442117bdcf084959fdba35c862`.
Fix commit: the commit titled `fix round one certification findings` containing this section.
All ten findings are accepted. Each lens initially reported FAIL; independent
re-verification remains pending. Public names, signatures and color arithmetic are unchanged.

| Lens | Finding | Correction and verification |
| --- | --- | --- |
| a | A-001 | `blend` documents a new base `Color` and equivalent RGBA channels, including the transparent-black exception; subclass operand probes confirm this behavior. |
| b | B-001 | GUIDE and `contrast_ratio` describe ideal source-over arithmetic rounded once, possible rendering differences and threshold crossings. The documented example gives 4.513298 for the ideal composite and 4.493067 for the alternate opaque pixel. |
| c | C-01 | API errors omit input values and custom type names. CLI usage errors omit arguments and point to help. Sentinel tests cover parsers, numeric validators, contrast options and CLI syntax errors. |
| c | C-02 | Validation checks actual types without instance `__class__` hooks, preserving built-in subclass values and documented rejection types. Predicates and color helpers are covered. |
| c | C-03 | Removed representation formatting entirely. Object and shared-container rejection never calls `repr`; a subprocess watchdog covers a blocking representation. |
| d | D-01 | Protected stdout flushing includes argparse early exits. Closed-pipe subprocess tests cover normal commands, help, subcommand help and version, requiring exit 1 and empty stderr. |
| e | E-01 | Exact strings distinguish omitted alpha from explicit alpha 255; replayed M09 fails `test_explicit_opaque_alpha_is_retained`. |
| e | E-02 | Strict rejection and lenient acceptance cover hashless and whitespace-wrapped hex through `Color.parse` and a subclass; replayed M18 fails `test_color_parse_forwards_strict_mode`. |
| e | E-03 | Luminance equality covers four RGB triples and five alpha bytes, using objects and strings; replayed M39 fails `test_relative_luminance_ignores_alpha`. |
| e | E-04 | The unsafe 40-character preview contract is superseded by C-01/C-03. Exact diagnostics at representation lengths 40 and 41 now require no preview. Reintroducing a 41-character preview fails both boundary assertions. |

Behavioral regression tests were added before implementation changes: 33 failed and
39 passed against the reviewed code. After correction, the targeted suite passed all
168 cases. The original lens-c `test_findings.py` also passed all nine repro cases.
The three surviving behavior mutations were replayed separately in scratch copies;
each exited 1 due to the new assertion. The obsolete preview limit was removed, and
a replacement mutation that restores input rendering was rejected.

`ruff format --check .`, `ruff check .`, `mypy --strict src` and
`mypy --strict src tests` each exit 0. The full suite passes **415 tests, no skips**,
including doctests, fetched specifications, reference implementations, wheel/CLI e2e
and the upgrade from PyPI 0.2.1. Pytest-timeout enforces 300 seconds per test.
Eight additional closed-pipe cases pass against a freshly installed wheel, covering
both the console launcher and isolated module execution with empty stderr and exit 1.
This round ran locally on CPython 3.14.6; the preparation matrix above is historical.
All behavior changes and corrected documentation are recorded in CHANGELOG.

Evidence is retained under `scratch/hexrgba-cert/fix-r1/`: `baseline.log`, `full.log`,
`mutation-results.json`, `installed-closed-pipe.json` and the individual mutation logs.
No findings are disputed.

## Remaining stages

Preparation checks and the round 1 fixes are complete. The independent review and
five-lens re-verification remain pending. Merge and publication remain pending.
