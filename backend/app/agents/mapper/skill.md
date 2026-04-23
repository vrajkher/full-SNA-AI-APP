# Mapper – Skills

## run(rows: list[VoucherRow]) -> MappingResult
Resolves `mapped_ledger` on every row.

## Resolution Order
1. Exact key lookup in `mapping_rules.json`.
2. Prefix lookup (characters before the first `.`).
3. Fallback: use `budget_line` as-is and add it to `unmapped`.
