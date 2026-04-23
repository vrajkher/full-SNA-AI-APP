# XML Generator – Soul

## Behaviour
- One Payment voucher per run with:
  - N debit `ALLLEDGERENTRIES.LIST` blocks (one per row)
  - one credit `ALLLEDGERENTRIES.LIST` block against the bank ledger
- Sign convention matches Tally:
  - Debits → negative `<AMOUNT>`, `ISDEEMEDPOSITIVE=Yes`
  - Credit → positive `<AMOUNT>`, `ISDEEMEDPOSITIVE=No`
- Bill allocations attach the UTR (or reference / claim) to the debit leg so
  Tally can re-identify the entry later.
- Voucher date defaults to the latest settlement date in the batch.

## Intelligence
- All strings pass through `xml.sax.saxutils.escape` to prevent XML injection
  from user-supplied beneficiary names.
- Voucher number is time-stamped (`ACCO-YYYYMMDDHHMMSS`) and GUID-tagged so
  repeated runs don't collide.
