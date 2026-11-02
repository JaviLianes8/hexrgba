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
| 19 | Pending | Round 5: E-R5-01, E-R5-02 and E-R5-03 help contracts fixed below; independent re-verification remains pending |

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
Fix commit: `60dd2f100f9700699c3f1cdc8ab15e8887085e48`
(`fix round one certification findings`).
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

## QA round 2: findings and fixes

Date: 2026-11-02. Reviewed head: `3080a6fde0a65b9141e3db5a4710ffa4f913e5a4`.
Fix commit: `675e1a81e571753a71a50b34367d7ae9bb735e32`
(`fix round two certification findings`).
All six findings are accepted. Independent re-verification remains pending.
Public names, signatures and color arithmetic are unchanged.

| Lens | Finding | Correction and verification |
| --- | --- | --- |
| d | D-02 | The argument parser propagates output-write errors to the protected handler. Buffered and unbuffered closed-pipe tests cover normal output, help, version and all four subcommands; installed console and isolated module entry points return 1 with empty stderr. |
| e | E-R2-01 | Opaque foreground contracts require a distinct base `Color` with the foreground channels, for both `Color` and subclasses. N06 now fails both cases. |
| e | E-R2-02 | Transparent foreground contracts require a distinct base `Color` with the background channels, for base/subclass backgrounds at alpha 1, 128 and 255. N07 now fails all six cases. |
| e | E-R2-03 | Parsing uses underlying strings even when `__str__` returns another valid color or raises. `parse_color`, base/subclass `Color.parse` and contrast levels are covered. N09 now fails eight cases. |
| e | E-R2-04 | Strict hashless-hex rejection has the same exact private diagnostic for all four hex lengths through `parse_color` and base/subclass `Color.parse`. N17 now fails twelve cases. |
| e | E-R2-05 | Unnamed-color CLI conversion requires exit 2, empty stdout and an exact diagnostic that omits each supplied color. N23 now fails three cases. |

The regression tests preceded the implementation fix. Against the reviewed code,
the targeted run had **7 failures and 48 passes**: six unbuffered module help/version
cases and the installed-console check failed. The five lens-e findings are missing
contracts for behavior already implemented correctly; no implementation changes were
needed for them. Each reported mutation was replayed alone in a scratch copy and
exited 1 because of the new assertions, with no collection or syntax failures.

`ruff format --check .`, `ruff check .`, `mypy --strict src` and
`mypy --strict src tests` each exit 0. The full suite passes **456 tests, no skips**,
including doctests, fetched specifications, reference implementations, wheel/CLI e2e
and upgrade from PyPI 0.2.1. The installed e2e check exercises 28 combinations of
entry point, buffering and output command. Every test has a 300-second timeout.
The original D-02 reproduction also passes against a fresh installation built from
the sdist. This round ran locally on CPython 3.14.6; the preparation interpreter
matrix above is historical. The behavior change is recorded in CHANGELOG.

Evidence is retained under `scratch/hexrgba-cert/fix-r2/`: `baseline.log`, `full.log`,
`mutation-results.json`, individual mutation logs, and `sdist-repro.log`.
No findings are disputed.

## QA round 3: findings and fixes

Date: 2026-11-02. Reviewed head: `94a0dde469eb1e653c1fec42f627dab2c34c25d8`.
Fix commit: `87ff2bbea524cd230bc40bb4a2f85b8c6ad891a4`
(`enforce cli help contracts for certification round three`).
E-R3-01 is accepted. Independent re-verification remains pending.

| Lens | Finding | Correction and verification |
| --- | --- | --- |
| e | E-R3-01 | Root and all four subcommand help contracts require usage, required operands in order, documented operands and subcommands, flags, exact supported choice sets, exit 0 and empty stderr. The same assertions run against the installed console script and isolated module entry point. |

This finding concerns missing contracts for behavior already implemented correctly.
The five new source cases pass against the reviewed implementation; no runtime or
API changes are needed. Expectations are hand-written, independent of parser internals,
and tolerate line wrapping and argparse section headings. The shared help checker is
included in the sdist so its packaged tests and wheel verification remain runnable.
CHANGELOG records the added verification.

Each reported mutation was applied alone in a scratch copy. Both the source contracts
and a newly built and installed wheel reject every mutation with assertion failures.

| Mutation | Source test detecting it | Installed wheel result |
| --- | --- | --- |
| S17: replace subcommand help with a placeholder | `test_help_describes_supported_syntax` for all four subcommands | Help contract fails |
| S19: remove root syntax and options | `test_help_describes_supported_syntax` for root help | Help contract fails |
| S20: advertise unsupported `lab` conversion | `test_help_describes_supported_syntax` for convert | Help contract fails |

`ruff format --check .`, `ruff check .`, `mypy --strict src` and
`mypy --strict src tests` each exit 0. The full suite passes **461 tests, no skips**,
including doctests, fetched specifications, reference implementations, wheel/CLI e2e
and upgrade from PyPI 0.2.1. Help checks cover ten installed entry point/command
combinations. Every test has a 300-second timeout. This round ran locally on
CPython 3.14.6; the preparation interpreter matrix above is historical.

Evidence is retained under `scratch/hexrgba-cert/fix-r3/`: `full.log`,
`mutation-results.json`, and the individual `S17.log`, `S19.log`, `S20.log` files.
No findings are disputed.

## QA round 4: findings and fixes

Date: 2026-11-02. Reviewed head: `c05090373d5c46dba98f813725c4211ed7edf5ae`.
Fix commit: `fe840ecc104db8882f2773bc0c0186e55b9ff2c5`
(`enforce cli help semantics for certification round four`).
All three findings are accepted. Independent re-verification remains pending.

| Lens | Finding | Correction and verification |
| --- | --- | --- |
| e | E-R4-01 | Help independently promises CSS as the conversion default. Omitting `--to` and selecting the advertised default both produce `rgb(255, 0, 0)` for red. |
| e | E-R4-02 | Help pins foreground as the color on top and background as the color underneath. Translucent blue over red produces `#7f0080`; reversing the operands produces `#ff0000`. |
| e | E-R4-03 | Usage and option declarations pin boolean flags without values and choice options with values. Executable cases cover `--short`, both `--strict` forms, `--large`, every `--to` and `--level` choice, rejected extra values and rejected missing values. |

These findings are missing contracts for correctly implemented behavior. The eight
source help cases pass against the reviewed implementation. Runtime code, public API
and help text remain unchanged. The expectations are hand-written, independent of
parser internals, and shared with both installed console and isolated module checks.
CHANGELOG records the added verification.

Each exact reviewer patch was applied alone in a scratch copy. The source contracts
and a freshly built and installed wheel reject all three with assertion failures.

| Mutation | Source test detecting it | Installed wheel result |
| --- | --- | --- |
| N04: advertise hex as the conversion default | `test_help_matches_behavior[assert_conversion_default]` | Help contract fails |
| N05: swap foreground/background descriptions | `test_help_matches_behavior[assert_blend_roles]` | Help contract fails |
| N06: advertise `--short LENGTH` | `test_help_matches_behavior[assert_option_forms]` | Help contract fails |

`ruff format --check .`, `ruff check .`, `mypy --strict src` and
`mypy --strict src tests` each exit 0. The full suite passes **464 tests, no skips**,
including doctests, fetched specifications, reference implementations, wheel/CLI e2e
and upgrade from PyPI 0.2.1. Every test has a 300-second timeout. This round ran
locally on CPython 3.14.6; the preparation interpreter matrix above is historical.

Evidence is retained under `scratch/hexrgba-cert/fix-r4/`: `full.log`,
`mutation-results.json`, and the individual `N04.log`, `N05.log`, `N06.log` files.
No findings are disputed.

## QA round 5: findings and fixes

Date: 2026-11-02. Reviewed head: `6c37c6bf15d3eea5e8f4690ec1aa3c2f3ef666be`.
Fix commit: `bda739e4bc25d64771fc50775fa3c8f89219b2e0`
(`enforce cli input help contracts for certification round five`).
All three findings are accepted. Independent re-verification remains pending.

| Lens | Finding | Correction and verification |
| --- | --- | --- |
| e | E-R5-01 | Help promises lossless shortening only. RGB and RGBA pairs cover compressible channels, non-compressible RGB and non-compressible alpha, requiring exact output without rounding. |
| e | E-R5-02 | Normalize and convert help promise strict CSS grammar. Both commands reject bare hex of all four supported lengths and whitespace-wrapped hex in strict mode, accept hash-prefixed CSS hex, and accept the lenient forms without strict mode. |
| e | E-R5-03 | Both color operand descriptions promise hex and CSS named colors. Exact output checks cover hex, mixed-case RebeccaPurple and transparent, with and without strict mode. |

These findings concern missing contracts for correctly implemented behavior. All eleven
source help cases pass against the reviewed implementation. Runtime code, public API
and help text remain unchanged. Hand-written expectations connect the documented
semantics to executable examples through source and both installed entry points.
CHANGELOG records the added verification.

Each exact reviewer patch was applied alone in a scratch copy. Source contracts and
a freshly built and installed wheel reject all three with assertion failures.

| Mutation | Source test detecting it | Installed wheel result |
| --- | --- | --- |
| N08: promise lossy shortening | `test_help_matches_behavior[assert_lossless_shortening]` | Help contract fails |
| N09: promise bare hex in strict mode | `test_help_matches_behavior[assert_strict_inputs]` | Help contract fails |
| N10: deny named-color support | `test_help_matches_behavior[assert_named_inputs]` | Help contract fails |

`ruff format --check .`, `ruff check .`, `mypy --strict src` and
`mypy --strict src tests` each exit 0. The full suite passes **467 tests, no skips**,
including doctests, fetched specifications, reference implementations, wheel/CLI e2e
and upgrade from PyPI 0.2.1. Every test has a 300-second timeout. This round ran
locally on CPython 3.14.6; the preparation interpreter matrix above is historical.

Evidence is retained under `scratch/hexrgba-cert/fix-r5/`: `full.log`,
`mutation-results.json`, and the individual `N08.log`, `N09.log`, `N10.log` files.
No findings are disputed.

## QA round 6: findings and fixes

Date: 2026-11-02. Reviewed head: `097a8e5b5c35e31683a1b8d75d1523e27917adbb`.
Fix commit: `f1e733fb52f8c52a6068fd729ca1ccaff3632229`
(`enforce root help input contract for certification round six`).
E-R6-01 is accepted. Independent re-verification remains pending.

| Lens | Finding | Correction and verification |
| --- | --- | --- |
| e | E-R6-01 | Root help must advertise CSS hex and named colors. The shared named-input contract checks this description before exercising hex, lowercase and mixed-case rebeccapurple, and transparent through normalize and convert, with and without strict mode. Source and both installed entry points use the same assertions. |

This finding concerns missing regression coverage for correctly implemented behavior.
All eleven source help cases pass against the reviewed implementation. Runtime code,
public API and help text remain unchanged. Hand-written expectations pin the root
description independently of parser internals and tolerate line wrapping. CHANGELOG
records the added verification.

The exact round-six `N10.patch` was applied in a scratch copy. Three source assertions
reject the false root description: `test_help_describes_supported_syntax` for root
help, `test_help_matches_behavior[assert_option_forms]`, and
`test_help_matches_behavior[assert_named_inputs]`. A fresh mutant wheel was built and
installed outside the repository. The shared named-input contract independently fails
for both the console script and isolated module entry point; both still normalize
`rebeccapurple` to `#663399`, confirming the help contradiction.

`ruff format --check .`, `ruff check .`, `mypy --strict src` and
`mypy --strict src tests` each exit 0. The full suite passes **467 tests, no skips**
in 149.23 seconds, including doctests, fetched specifications, reference checks,
wheel/CLI e2e and upgrade from PyPI 0.2.1. Every test has a 300-second timeout.
This round ran locally on CPython 3.14.6; the preparation interpreter matrix above
is historical.

Evidence is retained under `scratch/hexrgba-cert/fix-r6/`: `full.log`,
`mutation-results.json`, `N10-source.log`, `N10-build.log`, `N10-console.log`, and
`N10-module.log`. No findings are disputed.

## QA round 7: findings and fixes

Date: 2026-11-02. Reviewed head: `771e33b1eeadbff796515e5df55dad819b8dbf4c`.
Fix commit: `0df04d1dc69919f5ba55f6d579d29a47fa0415c8`
(`enforce complete root help contracts for certification round seven`).
All six findings are accepted. Independent re-verification remains pending.

| Lens | Finding | Correction and verification |
| --- | --- | --- |
| e | E-R7-01 | The root normalize summary promises lowercase hex; mixed-case `#AaBBcC` must normalize to `#aabbcc`. |
| e | E-R7-02 | The root convert summary is pinned alongside an invocation without `--to`; `convert red` must emit `rgb(255, 0, 0)`. |
| e | E-R7-03 | The root contrast summary promises a WCAG ratio; black against white must emit `21.00:1`. |
| e | E-R7-04 | The root blend summary promises a color over its background; translucent blue over red must emit `#7f0080`, while reversed operands must emit `#ff0000`. |
| e | E-R7-05 | The complete root help body is checked, including every description paragraph. Named-color support is exercised by normalizing `rebeccapurple` to `#663399`. |
| e | E-R7-06 | The version option promises the program's version; `--version` must emit `hexrgba 1.0.0`. |

These findings concern missing contracts for correctly implemented behavior. The six
new source cases pass against the reviewed implementation. Runtime code, public API
and help text remain unchanged. The hand-written complete-body expectation tolerates
line wrapping, indentation and argparse's options-heading variants. It rejects added
or changed prose anywhere before the separately checked exit-code and example epilog.
Each promise is paired with executable output checks shared by source tests and both
installed entry points. The new helper is included in the sdist. CHANGELOG records
the added verification.

Each exact reviewer patch was applied alone in a separate scratch copy. All eleven
previous source help checks pass for each patch, reproducing the coverage gap. All
six new source cases then fail with assertions, without collection, syntax or timeout
errors. Fresh wheels were built and installed outside the repository for every patch.
Both entry points reject the false help while retaining the expected command output.

| Mutation | Source test detecting it | Installed console and isolated module |
| --- | --- | --- |
| M05: promise uppercase normalization | `test_root_help_matches_behavior[normalize]` | Both reject the help |
| M06: advertise default hex conversion | `test_root_help_matches_behavior[convert]` | Both reject the help |
| M07: promise percentage contrast | `test_root_help_matches_behavior[contrast]` | Both reject the help |
| M08: reverse compositing order | `test_root_help_matches_behavior[blend]` | Both reject the help |
| M09: add a paragraph denying names | `test_root_help_matches_behavior[description]` | Both reject the help |
| M10: describe the Python runtime version | `test_root_help_matches_behavior[version]` | Both reject the help |

`ruff format --check .`, `ruff check .`, `mypy --strict src` and
`mypy --strict src tests` each exit 0. The full suite passes **473 tests, no skips**
in 160.50 seconds, including doctests, fetched specifications, reference checks,
wheel/CLI e2e and upgrade from PyPI 0.2.1. Every test has a 300-second timeout.
This round ran locally on CPython 3.14.6; the preparation interpreter matrix above
is historical.

Evidence is retained under `scratch/hexrgba-cert/fix-r7/`: `full.log`,
`mutation-results.json`, and each mutation's `Mxx-before.log`, `Mxx-source.log`,
`Mxx-build.log`, `Mxx-console.json` and `Mxx-module.json`. No findings are disputed.

## QA round 8: findings and fixes

Date: 2026-11-03. Reviewed head: `618627a94b4cca1044468bb4a4771489955a5796`.
Fix commit: `9c8d84ce653c2627cb1f63fd8feedc5274482461`
(`enforce root usage and exit-code contracts for round eight`).
All three findings are accepted. Independent re-verification remains pending.

| Lens | Finding | Correction and verification |
| --- | --- | --- |
| e | E-R8-01 | The complete normalized root usage requires the command group without optional brackets. An empty invocation must exit 2 with an error on stderr and no stdout. |
| e | E-R8-02 | The complete root operand sequence excludes invented operands. Minimal invocations of all four commands succeed without a FILE operand and retain their expected output. |
| e | E-R8-03 | The complete exit-code summary is pinned to 0 for success, 1 for a failed contrast level, and 2 for bad usage or invalid color. Successful commands, passing and failing AA pairs, empty invocation and an invalid color exercise those promises. |

These findings concern missing contracts for correctly implemented behavior. Runtime
code, public API and help text remain unchanged. Three new regression cases first
failed against the original checker because it accepted each false help promise.
All nine root-help cases pass after strengthening the shared source and wheel checker.
The complete usage and exit-code expectations tolerate whitespace and line wrapping.
CHANGELOG records the added verification.

Each exact reviewer patch was applied alone in a separate scratch copy. The eleven
general source help checks still pass for each patch. All six strengthened root-help
behavior cases reject each patch with assertions. Fresh wheels were built and
installed outside the repository; both installed entry points reject all three
mutations while normalization still succeeds with its expected output.

| Mutation | Source test detecting it | Installed console and isolated module |
| --- | --- | --- |
| N08: advertise an optional command | `test_root_help_matches_behavior[normalize]` | Both reject the complete usage |
| N09: invent a required FILE operand | `test_root_help_matches_behavior[normalize]` | Both reject the complete usage |
| N10: advertise success exit code 3 | `test_root_help_matches_behavior[normalize]` | Both reject the exit-code summary |

`ruff format --check .`, `ruff check .`, `mypy --strict src` and
`mypy --strict src tests` each exit 0. The full suite passes **476 tests, no skips**
in 225.48 seconds, including doctests, fetched specifications, reference checks,
wheel/CLI e2e and upgrade from PyPI 0.2.1. Every test has a 300-second timeout.
This round ran locally on CPython 3.14.6; the preparation interpreter matrix above
is historical.

Evidence is retained under `scratch/hexrgba-cert/fix-r8/`: `red.log`, `full.log`,
`mutation-results.json`, and each mutation's `Nxx-before.log`, `Nxx-source.log`,
`Nxx-build.log`, `Nxx-console.json` and `Nxx-module.json`. No findings are disputed.

## Remaining stages

Preparation checks and the round 1, 2, 3, 4, 5, 6, 7 and 8 fixes are complete. The independent review and
five-lens re-verification remain pending. Merge and publication remain pending.
