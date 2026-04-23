"""Extractor Agent – reads Excel / CSV and filters Status == 'Success'."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from app.agents.base import BaseAgent
from app.models import ExtractionResult, VoucherRow

COLUMN_ALIASES: dict[str, list[str]] = {
    "budget_line": ["NEW BUDGET LINE", "New Budget Line", "BudgetLine", "BUDGET LINE"],
    "sr_no": ["Sr No.", "Sr No", "SrNo", "S.No.", "S No"],
    "sls_code": ["SLS Code", "SLSCode"],
    "agency_code": ["Agency Code", "AgencyCode"],
    "claim_no": ["Claim No.", "Claim No", "ClaimNo"],
    "beneficiary_name": ["Beneficiary Name", "BeneficiaryName", "Beneficiary"],
    "account_no": ["Account No.", "Account No", "AccountNo", "A/C No"],
    "net_amount": ["Net Amount", "NetAmount", "Amount"],
    "settlement_date": ["Settlement Date", "SettlementDate", "Date"],
    "status_code": ["Status Code", "StatusCode"],
    "status": ["Status"],
    "in_file_name": ["In File Name", "InFileName", "File Name"],
    "utr_no": ["UTR No.", "UTR No", "UTRNo", "UTR"],
    "cin_no": ["CIN No.", "CIN No", "CINNo", "CIN"],
    "reference_no": ["Reference No.", "Reference No", "ReferenceNo", "Reference"],
}


def _normalize_headers(df: pd.DataFrame) -> pd.DataFrame:
    rename: dict[str, str] = {}
    for target, aliases in COLUMN_ALIASES.items():
        for col in df.columns:
            if str(col).strip() in aliases:
                rename[col] = target
                break
    return df.rename(columns=rename)


class ExtractorAgent(BaseAgent):
    name = "extractor"

    def run(self, file_path: str | Path) -> ExtractionResult:  # type: ignore[override]
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Input file not found: {path}")

        self.logger.info("Reading %s", path)
        if path.suffix.lower() in {".xlsx", ".xls"}:
            df = pd.read_excel(path, dtype=str)
        elif path.suffix.lower() == ".csv":
            df = pd.read_csv(path, dtype=str)
        else:
            raise ValueError(f"Unsupported file type: {path.suffix}")

        df = _normalize_headers(df)
        total = len(df)

        if "status" in df.columns:
            df["status"] = df["status"].astype(str).str.strip()
            successful = df[df["status"].str.lower() == "success"].copy()
        else:
            self.logger.warning("No 'Status' column; treating every row as success")
            successful = df.copy()
            successful["status"] = "Success"

        skipped = total - len(successful)
        rows: list[VoucherRow] = []

        for idx, raw in successful.iterrows():
            try:
                row = self._row_to_voucher(raw)
                rows.append(row)
            except Exception as exc:  # noqa: BLE001
                self.logger.warning("Skipping row %s: %s", idx, exc)
                skipped += 1

        self.logger.info("Extracted %d successful rows (skipped=%d)", len(rows), skipped)
        return ExtractionResult(rows=rows, skipped=skipped, total_rows=total)

    @staticmethod
    def _row_to_voucher(raw: Any) -> VoucherRow:
        def get(col: str) -> str | None:
            val = raw.get(col) if hasattr(raw, "get") else None
            if val is None or (isinstance(val, float) and pd.isna(val)):
                return None
            s = str(val).strip()
            return s if s and s.lower() != "nan" else None

        amt_raw = get("net_amount") or "0"
        amt = float(str(amt_raw).replace(",", ""))

        date_raw = get("settlement_date")
        if not date_raw:
            raise ValueError("Missing settlement_date")
        parsed_date = pd.to_datetime(date_raw, dayfirst=True, errors="coerce")
        if pd.isna(parsed_date):
            raise ValueError(f"Invalid settlement_date: {date_raw}")

        sr_raw = get("sr_no")
        sr_no = int(float(sr_raw)) if sr_raw else None

        return VoucherRow(
            sr_no=sr_no,
            budget_line=get("budget_line") or "",
            sls_code=get("sls_code"),
            agency_code=get("agency_code"),
            claim_no=get("claim_no"),
            beneficiary_name=get("beneficiary_name"),
            account_no=get("account_no"),
            net_amount=amt,
            settlement_date=parsed_date.date(),
            status_code=get("status_code"),
            status=get("status"),
            in_file_name=get("in_file_name"),
            utr_no=get("utr_no"),
            cin_no=get("cin_no"),
            reference_no=get("reference_no"),
        )
