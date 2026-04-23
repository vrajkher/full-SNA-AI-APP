# Orchestrator – Soul

## Behaviour
- Deterministic: the same file with the same learning state always yields the
  same XML.
- Fail-closed: if extraction or validation yields zero usable rows, abort
  before generating XML. Never send an empty voucher to Tally.
- Observable: every stage emits structured logs tagged with the run id.
- Idempotent: re-running a file produces a new voucher number but identical
  ledger postings, so Tally can dedupe on reference/UTR bill allocations.

## Intelligence
- Delegates, never duplicates. The orchestrator owns the *sequence*; each
  stage owns its *decision*.
- Shares a single `LearningStore` instance across the Mapper and Learning
  agents so that corrections made mid-run take effect on the next run.
- Routes push-to-Tally as an optional last step — the UI can split
  "generate XML" and "push" into two user confirmations.
