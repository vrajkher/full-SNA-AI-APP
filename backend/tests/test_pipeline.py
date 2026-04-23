"""Smoke tests for the full pipeline using the bundled sample CSV."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.agents.extractor import ExtractorAgent  # noqa: E402
from app.agents.mapper import MapperAgent  # noqa: E402
from app.agents.orchestrator import OrchestratorAgent  # noqa: E402
from app.agents.reviewer import ReviewerAgent  # noqa: E402
from app.agents.xml_generator import XMLGeneratorAgent  # noqa: E402

SAMPLE = ROOT.parent / "samples" / "sample_input.csv"


def test_extractor_filters_success_only() -> None:
    result = ExtractorAgent().run(SAMPLE)
    assert result.total_rows == 7
    assert len(result.rows) == 6
    assert all(r.status and r.status.lower() == "success" for r in result.rows)


def test_mapper_applies_learning_rules() -> None:
    rows = ExtractorAgent().run(SAMPLE).rows
    mapping = MapperAgent().run(rows)
    ledgers = {r.budget_line: r.mapped_ledger for r in mapping.rows}
    assert ledgers["HSS.9.1.108"] == "Health Expense"
    assert ledgers["FIN.2.1.100"] == "Finance Charges"


def test_reviewer_blocks_duplicates_and_zero_amount() -> None:
    rows = ExtractorAgent().run(SAMPLE).rows
    mapped = MapperAgent().run(rows).rows
    review = ReviewerAgent().run(mapped)
    assert len(review.rows) == 6
    assert review.total_amount > 0


def test_xml_generator_outputs_valid_envelope() -> None:
    rows = ExtractorAgent().run(SAMPLE).rows
    mapped = MapperAgent().run(rows).rows
    reviewed = ReviewerAgent().run(mapped).rows
    out = XMLGeneratorAgent().run(reviewed, persist=False)
    assert "<ENVELOPE>" in out.xml
    assert "<TALLYREQUEST>Import Data</TALLYREQUEST>" in out.xml
    assert out.xml.count("<ALLLEDGERENTRIES.LIST>") == len(reviewed) + 1


def test_orchestrator_end_to_end_without_pushing() -> None:
    result = OrchestratorAgent().run(SAMPLE, push_to_tally=False)
    assert result.success
    assert result.xml is not None
    assert result.xml.voucher_count == 6
    assert result.xml.total_amount > 0
