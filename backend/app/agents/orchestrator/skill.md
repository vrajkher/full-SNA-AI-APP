# Orchestrator – Skills

## run(file_path, push_to_tally=False, bank_ledger=None) -> PipelineResult
End-to-end execution. Calls the six downstream agents and writes the result
to `RunStore`.

## Pipeline Steps
1. `ExtractorAgent.run(file_path)`
2. `MapperAgent.run(rows)`
3. `ReviewerAgent.run(mapped_rows)`
4. `XMLGeneratorAgent.run(clean_rows, bank_ledger=bank)`
5. *(optional)* `TallyExecutorAgent.run(xml)`

## Side-effects
- Writes generated XML to `backend/app/data/outputs/voucher_<ts>.xml`
- Saves the `PipelineResult` to the in-memory `RunStore` (keyed by `run_id`)
