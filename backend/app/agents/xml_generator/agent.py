"""XML Generator Agent – builds Tally Prime payment-voucher XML."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from pathlib import Path
from xml.sax.saxutils import escape

from app.agents.base import BaseAgent
from app.core import settings
from app.models import VoucherRow, XMLGenerationResult


def _tally_date(d: date | datetime) -> str:
    return d.strftime("%Y%m%d")


def _fmt_amount(value: float) -> str:
    return f"{value:.2f}"


class XMLGeneratorAgent(BaseAgent):
    """Generates a single Payment voucher with N debits and 1 credit.

    Sign convention (Tally XML):
    - Debits → negative amount (outflow)
    - Credits → positive amount (inflow)
    """

    name = "xml_generator"

    def run(  # type: ignore[override]
        self,
        rows: list[VoucherRow],
        bank_ledger: str | None = None,
        voucher_date: date | None = None,
        persist: bool = True,
    ) -> XMLGenerationResult:
        if not rows:
            raise ValueError("Cannot generate XML with zero rows")

        bank_ledger = bank_ledger or settings.DEFAULT_BANK_LEDGER
        voucher_date = voucher_date or max(r.settlement_date for r in rows)
        total = round(sum(r.net_amount for r in rows), 2)
        voucher_no = f"ACCO-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        guid = str(uuid.uuid4())

        dr_entries = "".join(self._dr_entry(r) for r in rows)
        cr_entry = self._cr_entry(bank_ledger, total)

        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<ENVELOPE>
  <HEADER>
    <TALLYREQUEST>Import Data</TALLYREQUEST>
  </HEADER>
  <BODY>
    <IMPORTDATA>
      <REQUESTDESC>
        <REPORTNAME>Vouchers</REPORTNAME>
        <STATICVARIABLES>
          <SVCURRENTCOMPANY>##SVCurrentCompany</SVCURRENTCOMPANY>
        </STATICVARIABLES>
      </REQUESTDESC>
      <REQUESTDATA>
        <TALLYMESSAGE xmlns:UDF="TallyUDF">
          <VOUCHER VCHTYPE="{settings.VOUCHER_TYPE}" ACTION="Create" OBJVIEW="Accounting Voucher View">
            <DATE>{_tally_date(voucher_date)}</DATE>
            <EFFECTIVEDATE>{_tally_date(voucher_date)}</EFFECTIVEDATE>
            <VOUCHERTYPENAME>{escape(settings.VOUCHER_TYPE)}</VOUCHERTYPENAME>
            <VOUCHERNUMBER>{escape(voucher_no)}</VOUCHERNUMBER>
            <PARTYLEDGERNAME>{escape(bank_ledger)}</PARTYLEDGERNAME>
            <NARRATION>Accotech AI – Bulk payment run {voucher_no}</NARRATION>
            <ISDELETED>No</ISDELETED>
            <ISONACCOUNT>No</ISONACCOUNT>
            <GUID>{guid}</GUID>
{dr_entries}{cr_entry}
          </VOUCHER>
        </TALLYMESSAGE>
      </REQUESTDATA>
    </IMPORTDATA>
  </BODY>
</ENVELOPE>
"""

        output_path: str | None = None
        if persist:
            out = settings.OUTPUT_DIR / f"voucher_{voucher_no}.xml"
            out.write_text(xml, encoding="utf-8")
            output_path = str(out)
            self.logger.info("Wrote XML to %s", out)

        return XMLGenerationResult(
            xml=xml,
            voucher_count=len(rows),
            total_amount=total,
            output_path=output_path,
        )

    @staticmethod
    def _dr_entry(row: VoucherRow) -> str:
        ledger = row.mapped_ledger or row.budget_line
        amount = _fmt_amount(-abs(row.net_amount))
        narration = escape(row.narration)
        return f"""            <ALLLEDGERENTRIES.LIST>
              <LEDGERNAME>{escape(ledger)}</LEDGERNAME>
              <ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>
              <AMOUNT>{amount}</AMOUNT>
              <NARRATION>{narration}</NARRATION>
              <BILLALLOCATIONS.LIST>
                <NAME>{escape(row.utr_no or row.reference_no or row.claim_no or '')}</NAME>
                <BILLTYPE>New Ref</BILLTYPE>
                <AMOUNT>{amount}</AMOUNT>
              </BILLALLOCATIONS.LIST>
            </ALLLEDGERENTRIES.LIST>
"""

    @staticmethod
    def _cr_entry(bank_ledger: str, total: float) -> str:
        amount = _fmt_amount(abs(total))
        return f"""            <ALLLEDGERENTRIES.LIST>
              <LEDGERNAME>{escape(bank_ledger)}</LEDGERNAME>
              <ISDEEMEDPOSITIVE>No</ISDEEMEDPOSITIVE>
              <AMOUNT>{amount}</AMOUNT>
              <NARRATION>Accotech AI – Consolidated payment credit</NARRATION>
            </ALLLEDGERENTRIES.LIST>
"""
