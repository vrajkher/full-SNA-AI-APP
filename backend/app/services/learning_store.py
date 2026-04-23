"""JSON-backed learning memory used by the Mapper and Learning agents."""

from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Dict

from app.core import settings

_LOCK = threading.Lock()

DEFAULT_RULES: Dict[str, str] = {
    "HSS.9.1.108": "Health Expense",
    "HSS.9.1.109": "Medical Reimbursement",
    "HSS.9.2.101": "Insurance Premium",
    "HSS.9.3.101": "Travel Expense",
    "ADM.1.1.100": "Administrative Expense",
    "FIN.2.1.100": "Finance Charges",
    "SAL.3.1.100": "Salary Expense",
}


class LearningStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or settings.LEARNING_FILE
        self._init_if_missing()

    def _init_if_missing(self) -> None:
        if not self.path.exists():
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(json.dumps(DEFAULT_RULES, indent=2), encoding="utf-8")

    def rules(self) -> Dict[str, str]:
        with _LOCK:
            try:
                return json.loads(self.path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, FileNotFoundError):
                return dict(DEFAULT_RULES)

    def upsert(self, budget_line: str, ledger: str) -> None:
        if not budget_line or not ledger:
            return
        with _LOCK:
            rules = {}
            if self.path.exists():
                try:
                    rules = json.loads(self.path.read_text(encoding="utf-8"))
                except json.JSONDecodeError:
                    rules = {}
            rules[budget_line.strip()] = ledger.strip()
            self.path.write_text(json.dumps(rules, indent=2, sort_keys=True), encoding="utf-8")

    def delete(self, budget_line: str) -> None:
        with _LOCK:
            if not self.path.exists():
                return
            try:
                rules = json.loads(self.path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                return
            rules.pop(budget_line, None)
            self.path.write_text(json.dumps(rules, indent=2, sort_keys=True), encoding="utf-8")

    def bulk_replace(self, rules: Dict[str, str]) -> None:
        with _LOCK:
            self.path.write_text(
                json.dumps(rules, indent=2, sort_keys=True),
                encoding="utf-8",
            )
