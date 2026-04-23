# Learning – Skills

## run(corrections: list[LedgerCorrection]) -> LearningState
Insert / update one or more mapping rules and return the full current rule
set.

## state() -> LearningState
Return all currently known rules plus their count.

## forget(budget_line: str) -> LearningState
Drop one rule. The mapper's fallback still works (budget-line passthrough),
so nothing breaks — but that budget-line will appear in `unmapped` next time.
