"""Mapper Agent – resolves a budget-line code to a Tally ledger."""

from __future__ import annotations

from app.agents.base import BaseAgent
from app.models import MappingResult, VoucherRow
from app.services.learning_store import LearningStore


class MapperAgent(BaseAgent):
    name = "mapper"

    def __init__(self, store: LearningStore | None = None) -> None:
        super().__init__()
        self.store = store or LearningStore()

    def run(self, rows: list[VoucherRow]) -> MappingResult:  # type: ignore[override]
        mapped: list[VoucherRow] = []
        unmapped: list[str] = []
        rules = self.store.rules()

        for row in rows:
            ledger = self._resolve(row.budget_line, rules)
            if ledger is None:
                unmapped.append(row.budget_line)
                ledger = row.budget_line
            row.mapped_ledger = ledger
            mapped.append(row)

        if unmapped:
            self.logger.info("Unmapped budget lines: %s", sorted(set(unmapped)))
        return MappingResult(rows=mapped, unmapped=sorted(set(unmapped)))

    @staticmethod
    def _resolve(budget_line: str, rules: dict[str, str]) -> str | None:
        if not budget_line:
            return None
        if budget_line in rules:
            return rules[budget_line]
        prefix = budget_line.split(".")[0] if "." in budget_line else budget_line
        if prefix in rules:
            return rules[prefix]
        return None
