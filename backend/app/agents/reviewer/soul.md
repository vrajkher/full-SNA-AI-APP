# Reviewer – Soul

## Behaviour
- Classifies findings as `error` (row is dropped) or `warning` (row passes,
  but the UI highlights it).
- Error categories:
  - `net_amount <= 0`
  - missing `budget_line`
  - duplicate `utr_no`
  - invalid / missing `settlement_date`
- Warning categories:
  - `mapped_ledger` not resolved (fell back to raw budget-line)
  - missing `utr_no` (dedupe is weaker)

## Intelligence
- Keeps the first occurrence of a UTR and rejects subsequent ones; this
  preserves the chronological order from the spreadsheet.
- Surfaces the *full* set of issues to the UI, so the user sees every
  problem in one pass instead of fixing them one at a time.
