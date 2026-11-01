# hexrgba 1.0.0 certification report

Preparation date: 2026-11-01. PyPI currently publishes 0.2.1 (JSON endpoint checked
live). The existing three release commits were retained. Main is `8619b02`.

Progress:
- [x] Stable API, exact exports, runnable examples, typed bounded errors (items 1-5)
- [x] Contracts, fetched specifications, reference implementations and seeded fuzz (6, 7, 9)
- [x] README, GUIDE, dated CHANGELOG and production metadata (11-13)
- [x] Wheel/CLI e2e, upgrade from PyPI 0.2.1, distribution inspection (8, 14)
- [ ] Available interpreter matrix (10)
- [x] Four gates (15), plus strict types for tests
- [ ] Mutation round (18)
- [ ] Independent reviewer (16)
- [ ] Five QA lenses (19)
- [ ] PR handoff (17); merge and publication remain pending

## API and compatibility

The 19 exports retain their parameter names, defaults and valid-input behavior.
`tests/test_contract_api.py` pins signatures, fields, immutability, subclass behavior,
pickle/copy support, error inheritance and examples. The CHANGELOG lists all changes
from 0.2.1, including argument errors, built-in subclass normalization, public pickle
names, subclass preservation and bounded CLI errors. Public values contain no `Any`.

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

`ruff format --check .`, `ruff check .`, `mypy --strict src tests` and `pytest`
pass. The suite has 352 passing tests with one opt-in wheel test skipped; that test's
script passed separately with `HEXRGBA_E2E_PYPI=1`. Every test has a 300-second limit.

The e2e script builds both distributions, installs the wheel in a fresh venv, executes
all ten help examples through the installed console script, checks invalid input and
`python -m hexrgba`, imports with `-I`, then confirms upgrade values and an old pickle.
Both distributions pass `twine check --strict`. The wheel contains only the package,
typing marker and distribution metadata including LICENSE. The sdist contains source,
tests, the derived color table, manifest, two test utilities, README, GUIDE, CHANGELOG,
LICENSE and pyproject; no fetched pages, caches or scratch files.

Seeded tests cover 3,000 random RGBA values and 9,000 hostile strings; additional
million-character inputs verify bounded errors and linear scaling. Numeric and string
subclasses, unprintable objects, huge integers and closed CLI output are covered.

## Remaining stages

Interpreter and mutation results will be recorded below. Independent review and the
five QA lenses have no recorded verdict yet. Merge and publication are out of scope
for this preparation report.
