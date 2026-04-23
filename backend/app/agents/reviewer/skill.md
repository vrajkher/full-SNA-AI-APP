# Reviewer – Skills

## run(rows: list[VoucherRow]) -> ReviewResult
Returns the kept rows, all issues, the number of duplicates removed, and the
grand total.

## Validation Matrix
| Check                        | Severity | Outcome             |
|------------------------------|----------|---------------------|
| `net_amount > 0`             | error    | row dropped         |
| `budget_line` present        | error    | row dropped         |
| UTR uniqueness               | error    | row dropped         |
| Valid `settlement_date`      | error    | row dropped         |
| Ledger resolved              | warning  | row kept, flagged   |
| UTR present                  | warning  | row kept, flagged   |
