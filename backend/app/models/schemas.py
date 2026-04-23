"""Pydantic schemas used by the API and between agents."""

from __future__ import annotations

from datetime import date
from typing import Any, Optional

from pydantic import BaseModel, Field


class VoucherRow(BaseModel):
    """A single successful row from the input file."""

    sr_no: Optional[int] = None
    budget_line: str = Field(..., description="NEW BUDGET LINE column → DR ledger key")
    mapped_ledger: Optional[str] = Field(None, description="Resolved Tally ledger name")
    sls_code: Optional[str] = None
    agency_code: Optional[str] = None
    claim_no: Optional[str] = None
    beneficiary_name: Optional[str] = None
    account_no: Optional[str] = None
    net_amount: float
    settlement_date: date
    status_code: Optional[str] = None
    status: Optional[str] = None
    in_file_name: Optional[str] = None
    utr_no: Optional[str] = None
    cin_no: Optional[str] = None
    reference_no: Optional[str] = None

    @property
    def narration(self) -> str:
        beneficiary = (self.beneficiary_name or "").strip()
        utr = (self.utr_no or "").strip()
        if beneficiary and utr:
            return f"{beneficiary} | UTR: {utr}"
        return beneficiary or f"UTR: {utr}" or "Payment"


class ReviewIssue(BaseModel):
    sr_no: Optional[int] = None
    utr_no: Optional[str] = None
    severity: str = Field(..., pattern="^(error|warning)$")
    field: str
    message: str


class ExtractionResult(BaseModel):
    rows: list[VoucherRow]
    skipped: int = 0
    total_rows: int = 0


class MappingResult(BaseModel):
    rows: list[VoucherRow]
    unmapped: list[str] = []


class ReviewResult(BaseModel):
    rows: list[VoucherRow]
    issues: list[ReviewIssue] = []
    duplicates_removed: int = 0
    total_amount: float = 0.0


class XMLGenerationResult(BaseModel):
    xml: str
    voucher_count: int
    total_amount: float
    output_path: Optional[str] = None


class TallyPushResult(BaseModel):
    success: bool
    status_code: int
    response_text: str
    imported: Optional[int] = None
    errors: Optional[int] = None


class PipelineResult(BaseModel):
    run_id: str
    success: bool
    stage: str
    extraction: Optional[ExtractionResult] = None
    review: Optional[ReviewResult] = None
    xml: Optional[XMLGenerationResult] = None
    tally: Optional[TallyPushResult] = None
    issues: list[ReviewIssue] = []
    message: str = ""
    data: dict[str, Any] = {}


class LedgerCorrection(BaseModel):
    budget_line: str
    correct_ledger: str


class LearningState(BaseModel):
    rules: dict[str, str]
    count: int
