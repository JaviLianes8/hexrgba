# Local quality gate. Run before every commit. No CI runs in the cloud.
# The wheel end-to-end check runs with: $env:HEXRGBA_E2E = "1"; pytest tests/test_e2e_wheel.py
$ErrorActionPreference = "Stop"

ruff format --check .
if ($LASTEXITCODE -ne 0) { exit 1 }
ruff check .
if ($LASTEXITCODE -ne 0) { exit 1 }
mypy --strict src
if ($LASTEXITCODE -ne 0) { exit 1 }
pytest
if ($LASTEXITCODE -ne 0) { exit 1 }
