# Orchestrator Agent

## Role
Mission-control for the Accotech AI pipeline. Receives an Excel/CSV file and a
"push" flag, then coordinates Extractor → Mapper → Reviewer → XML Generator →
Tally Executor, persisting the final result in the RunStore for the UI to
inspect.

## Goal
Produce either a valid Tally Payment voucher XML (dry-run) or a successful
Tally Prime import, with a complete audit trail of every row that was accepted,
rejected, or deduplicated.

## Inputs
- Absolute path to the uploaded spreadsheet
- `push_to_tally: bool`
- Optional `bank_ledger` override (default `HDFC Bank`)

## Outputs
- `PipelineResult` with per-stage artefacts, issues, unmapped budget lines,
  generated XML, and (when `push=True`) the Tally response.

## Failure Contract
Never raises. Every failure is captured as a `PipelineResult` with
`success=False`, a `stage` marker, and a human-readable `message`.
