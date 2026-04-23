# Mapper – Soul

## Behaviour
- Exact match first: full budget-line code → ledger.
- Prefix fallback second: the first dot-separated segment → ledger (lets one
  rule cover a whole cost centre family).
- Safe default: if nothing matches, pass the budget-line through as the ledger
  name and tag it in `unmapped`. The Reviewer will log a warning so the user
  can correct it via the Learning API.

## Intelligence
- Reads the latest JSON on every run; there is no in-process cache, which
  means mid-session corrections are picked up without a restart.
- Collaborates with the Learning Agent: the two share the same
  `LearningStore` instance in the Orchestrator.
