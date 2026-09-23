# WF-002 — Free standard shipping at the threshold

**Status:** Ready for implementation
**Mode:** strict/local
**Risk:** low
**Canonical input:** frozen for baseline and candidate runs

## Problem

The checkout shipping calculator charges the standard shipping fee when an
order subtotal is exactly 5,000 cents. The product rule makes standard shipping
free at 5,000 cents or more.

## Acceptance criteria

1. Standard shipping costs 500 cents for a subtotal below 5,000 cents.
2. Standard shipping costs 0 cents for a subtotal of exactly 5,000 cents.
3. Standard shipping costs 0 cents for a subtotal above 5,000 cents.
4. Express shipping costs 1,200 cents at every subtotal, including the boundary.
5. The existing unit suite passes after the change.

## Decisions and scope

- All monetary values are integer cents. Order subtotals are nonnegative and
  validated by the caller; input validation is outside this story.
- Change only the fee rule needed for the acceptance criteria. Keep the public
  function name, signature, and fee constants stable.
- The fixture has no unresolved product decisions, external services, or
  credentials. No GitHub issue, pull request, or remote CI is part of this
  strict/local run.
- Developer implementation, Technical Lead review, QA verification, and Product
  Owner closure are distinct stages. Each stage must report its own evidence.
