# ST-000211 Test Scenarios — Free standard shipping at the threshold

**Story:** ST-000211 (WF-002 shipping threshold)
**Type:** behavioral | **Feature:** none (artifacts filed under `ST-000211` folders)
**Function under test:** `pricing.shipping_fee_cents(subtotal_cents, *, express=False)`
**Constants (contract):** threshold 5,000 cents; standard fee 500 cents; express fee 1,200 cents. All values are integer cents.

## Scope and exclusions

- Input validation is out of scope. Subtotals are nonnegative integers validated by the caller (story "Decisions and scope"), so no error-path scenarios exist for negative, non-integer, or `None` subtotals. The function defines no error behavior.
- No integration suite, network, database, or credentials exist for this repo.

## Scenarios

| ID | Category | Shipping | Subtotal (cents) | Expected fee (cents) | AC |
|---|---|---|---|---|---|
| SC-01 | Happy path (below threshold) | standard | 4,999 | 500 | AC1 |
| SC-02 | Boundary (at threshold) | standard | 5,000 | 0 | AC2 |
| SC-03 | Boundary (above threshold) | standard | 5,001 | 0 | AC3 |
| SC-04 | Edge (minimum subtotal) | standard | 0 | 500 | AC1 |
| SC-05 | Boundary (below threshold) | express | 4,999 | 1,200 | AC4 |
| SC-06 | Boundary (at threshold) | express | 5,000 | 1,200 | AC4 |
| SC-07 | Boundary (above threshold) | express | 5,001 | 1,200 | AC4 |

## AC mapping

- AC1 (standard below 5,000 -> 500): SC-01, SC-04
- AC2 (standard at 5,000 -> 0): SC-02
- AC3 (standard above 5,000 -> 0): SC-03
- AC4 (express 1,200 at every subtotal incl. boundary): SC-05, SC-06, SC-07
- AC5 (existing unit suite passes): run the existing suite, expect 6 tests OK (see commands)

## Commands (run from the repository root)

Scenario script, either form:

```
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests/feature/ST-000211/scripts -v
PYTHONDONTWRITEBYTECODE=1 python tests/feature/ST-000211/scripts/test_st_000211_scenarios.py -v
```

Existing suite (AC5 and regression):

```
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -v
```

Note: `-t .` is not usable because the scripts folder tree has no `__init__.py` packages (discovery raises "Start directory is not importable"); the script inserts the repo root into `sys.path` itself, so plain `-s` works.

Expected: scenario script 7 tests OK; existing suite 6 tests OK. No `__pycache__` or `.pyc` files should be created.
