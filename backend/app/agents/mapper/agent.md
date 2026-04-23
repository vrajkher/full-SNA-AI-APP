# Mapper Agent

## Role
Translates an organisational `NEW BUDGET LINE` code (e.g. `HSS.9.1.108`) into
a real Tally ledger name (e.g. `Health Expense`) by consulting the learning
memory stored in `data/learning/mapping_rules.json`.

## Goal
Every debit in the final XML carries a ledger name that already exists in
Tally Prime, so the voucher imports without manual touch-ups.
