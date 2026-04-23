# Extractor Agent

## Role
First agent in the chain. Reads Excel (`.xlsx`, `.xls`) and CSV inputs using
pandas, normalises the 15 expected columns, and filters the rows where
`Status == "Success"` into typed `VoucherRow` objects.

## Goal
Hand the downstream agents a clean, typed list of successful rows — with
numbers parsed as floats and dates parsed as `datetime.date` — so no other
agent has to know about the spreadsheet shape.

## Inputs
- A filesystem path to `.xlsx | .xls | .csv`

## Outputs
- `ExtractionResult(rows, skipped, total_rows)`
