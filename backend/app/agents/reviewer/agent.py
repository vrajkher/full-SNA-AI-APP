"""Reviewer Agent – validates and de-duplicates rows before XML generation."""

from __future__ import annotations

from datetime import date

from app.agents.base import BaseAgent
from app.models import ReviewIssue, ReviewResult, VoucherRow


class ReviewerAgent(BaseAgent):
    name = "reviewer"

    def run(self, rows: list[VoucherRow]) -> ReviewResult:  # type: ignore[override]
        issues: list[ReviewIssue] = []
        seen_utrs: set[str] = set()
        clean: list[VoucherRow] = []
        duplicates = 0

        for row in rows:
            row_issues = self._validate(row)
            error_issue = next((i for i in row_issues if i.severity == "error"), None)

            if row.utr_no and row.utr_no in seen_utrs:
                duplicates += 1
                issues.append(
                    ReviewIssue(
                        sr_no=row.sr_no,
                        utr_no=row.utr_no,
                        severity="error",
                        field="utr_no",
                        message=f"Duplicate UTR: {row.utr_no}",
                    )
                )
                issues.extend(row_issues)
                continue

            issues.extend(row_issues)
            if error_issue is not None:
                continue

            if row.utr_no:
                seen_utrs.add(row.utr_no)
            clean.append(row)

        total = round(sum(r.net_amount for r in clean), 2)
        self.logger.info(
            "Review done: kept=%d, duplicates=%d, issues=%d, total=%.2f",
            len(clean),
            duplicates,
            len(issues),
            total,
        )
        return ReviewResult(
            rows=clean,
            issues=issues,
            duplicates_removed=duplicates,
            total_amount=total,
        )

    @staticmethod
    def _validate(row: VoucherRow) -> list[ReviewIssue]:
        issues: list[ReviewIssue] = []
        if row.net_amount is None or row.net_amount <= 0:
            issues.append(
                ReviewIssue(
                    sr_no=row.sr_no,
                    utr_no=row.utr_no,
                    severity="error",
                    field="net_amount",
                    message="Amount must be greater than zero",
                )
            )
        if not row.budget_line:
            issues.append(
                ReviewIssue(
                    sr_no=row.sr_no,
                    utr_no=row.utr_no,
                    severity="error",
                    field="budget_line",
                    message="Missing NEW BUDGET LINE",
                )
            )
        if not row.mapped_ledger:
            issues.append(
                ReviewIssue(
                    sr_no=row.sr_no,
                    utr_no=row.utr_no,
                    severity="warning",
                    field="mapped_ledger",
                    message="Ledger not resolved from learning memory; using budget line as-is",
                )
            )
        if not isinstance(row.settlement_date, date):
            issues.append(
                ReviewIssue(
                    sr_no=row.sr_no,
                    utr_no=row.utr_no,
                    severity="error",
                    field="settlement_date",
                    message="Invalid settlement date",
                )
            )
        if not row.utr_no:
            issues.append(
                ReviewIssue(
                    sr_no=row.sr_no,
                    utr_no=row.utr_no,
                    severity="warning",
                    field="utr_no",
                    message="Missing UTR (duplicate check will be weaker)",
                )
            )
        return issues
