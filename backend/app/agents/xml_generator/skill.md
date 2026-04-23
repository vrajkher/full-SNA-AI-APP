# XML Generator – Skills

## run(rows, bank_ledger=None, voucher_date=None, persist=True) -> XMLGenerationResult
Builds the voucher XML and, when `persist=True`, writes it to
`backend/app/data/outputs/voucher_<voucher_no>.xml`.

## Shape
```xml
<ENVELOPE>
  <HEADER><TALLYREQUEST>Import Data</TALLYREQUEST></HEADER>
  <BODY>
    <IMPORTDATA>
      <REQUESTDESC>…</REQUESTDESC>
      <REQUESTDATA>
        <TALLYMESSAGE>
          <VOUCHER VCHTYPE="Payment" ACTION="Create" …>
            <DATE>YYYYMMDD</DATE>
            <VOUCHERTYPENAME>Payment</VOUCHERTYPENAME>
            … N × ALLLEDGERENTRIES.LIST (debits, negative) …
            1  × ALLLEDGERENTRIES.LIST (credit,  positive, bank)
          </VOUCHER>
        </TALLYMESSAGE>
      </REQUESTDATA>
    </IMPORTDATA>
  </BODY>
</ENVELOPE>
```
