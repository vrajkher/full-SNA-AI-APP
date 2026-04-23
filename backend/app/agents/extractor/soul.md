# Extractor – Soul

## Behaviour
- Schema-tolerant: accepts common header variants (`Sr No.` / `Sr No` / `SrNo`)
  via the `COLUMN_ALIASES` table.
- Lossy only by design: rows that don't have `Status = Success` are skipped,
  not repaired. Rows with corrupt dates or amounts are also skipped and
  counted.
- Locale-aware: dates are parsed with `dayfirst=True` to match Indian
  formats (DD/MM/YYYY).
- Treats blanks, `NaN`, and `"nan"` strings as missing.

## Intelligence
- Uses header aliases rather than positional reads so the same code works for
  SNA, banking, and claims exports.
- Centralises all I/O — no other agent touches pandas.
