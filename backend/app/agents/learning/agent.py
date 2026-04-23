"""Learning Agent – stores corrections and exposes the mapping memory."""

from __future__ import annotations

from app.agents.base import BaseAgent
from app.models import LearningState, LedgerCorrection
from app.services.learning_store import LearningStore


class LearningAgent(BaseAgent):
    name = "learning"

    def __init__(self, store: LearningStore | None = None) -> None:
        super().__init__()
        self.store = store or LearningStore()

    def run(self, corrections: list[LedgerCorrection]) -> LearningState:  # type: ignore[override]
        for c in corrections:
            self.store.upsert(c.budget_line, c.correct_ledger)
            self.logger.info("Learned: %s → %s", c.budget_line, c.correct_ledger)
        rules = self.store.rules()
        return LearningState(rules=rules, count=len(rules))

    def state(self) -> LearningState:
        rules = self.store.rules()
        return LearningState(rules=rules, count=len(rules))

    def forget(self, budget_line: str) -> LearningState:
        self.store.delete(budget_line)
        rules = self.store.rules()
        return LearningState(rules=rules, count=len(rules))
