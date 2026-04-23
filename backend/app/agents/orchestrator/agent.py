"""Orchestrator Agent – drives the end-to-end pipeline."""

from __future__ import annotations

import uuid
from pathlib import Path

from app.agents.base import BaseAgent
from app.agents.extractor import ExtractorAgent
from app.agents.learning import LearningAgent
from app.agents.mapper import MapperAgent
from app.agents.reviewer import ReviewerAgent
from app.agents.tally_executor import TallyExecutorAgent
from app.agents.xml_generator import XMLGeneratorAgent
from app.core import settings
from app.models import PipelineResult
from app.services.learning_store import LearningStore
from app.services.run_store import run_store


class OrchestratorAgent(BaseAgent):
    name = "orchestrator"

    def __init__(self) -> None:
        super().__init__()
        self.store = LearningStore()
        self.extractor = ExtractorAgent()
        self.mapper = MapperAgent(store=self.store)
        self.reviewer = ReviewerAgent()
        self.xml_agent = XMLGeneratorAgent()
        self.tally = TallyExecutorAgent()
        self.learning = LearningAgent(store=self.store)

    def run(  # type: ignore[override]
        self,
        file_path: str | Path,
        push_to_tally: bool = False,
        bank_ledger: str | None = None,
    ) -> PipelineResult:
        run_id = str(uuid.uuid4())
        bank = bank_ledger or settings.DEFAULT_BANK_LEDGER
        self.logger.info("Run %s starting (file=%s, push=%s)", run_id, file_path, push_to_tally)

        try:
            extraction = self.extractor.run(file_path)
        except Exception as exc:  # noqa: BLE001
            self.logger.exception("Extraction failed")
            result = PipelineResult(
                run_id=run_id,
                success=False,
                stage="extractor",
                message=f"Extraction failed: {exc}",
            )
            run_store.save(result)
            return result

        if not extraction.rows:
            result = PipelineResult(
                run_id=run_id,
                success=False,
                stage="extractor",
                extraction=extraction,
                message="No successful rows found in the input file.",
            )
            run_store.save(result)
            return result

        mapping = self.mapper.run(extraction.rows)
        review = self.reviewer.run(mapping.rows)

        if not review.rows:
            result = PipelineResult(
                run_id=run_id,
                success=False,
                stage="reviewer",
                extraction=extraction,
                review=review,
                issues=review.issues,
                message="All rows failed validation; nothing to post.",
            )
            run_store.save(result)
            return result

        xml_result = self.xml_agent.run(review.rows, bank_ledger=bank)

        tally_result = None
        stage = "xml_generator"
        if push_to_tally:
            tally_result = self.tally.run(xml_result.xml)
            stage = "tally_executor"

        success = bool(xml_result.xml) and (tally_result.success if tally_result else True)
        msg = "XML generated."
        if tally_result is not None:
            msg = "Pushed to Tally successfully." if tally_result.success else f"Tally push failed: {tally_result.response_text[:200]}"

        result = PipelineResult(
            run_id=run_id,
            success=success,
            stage=stage,
            extraction=extraction,
            review=review,
            xml=xml_result,
            tally=tally_result,
            issues=review.issues,
            message=msg,
            data={
                "bank_ledger": bank,
                "unmapped": mapping.unmapped,
            },
        )
        run_store.save(result)
        return result
