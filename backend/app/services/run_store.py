"""In-memory run cache: stores the most recent pipeline result per run id."""

from __future__ import annotations

import threading
from typing import Dict

from app.models import PipelineResult

_LOCK = threading.Lock()


class RunStore:
    _runs: Dict[str, PipelineResult] = {}

    def save(self, result: PipelineResult) -> None:
        with _LOCK:
            self._runs[result.run_id] = result

    def get(self, run_id: str) -> PipelineResult | None:
        with _LOCK:
            return self._runs.get(run_id)

    def list_ids(self) -> list[str]:
        with _LOCK:
            return list(self._runs.keys())


run_store = RunStore()
