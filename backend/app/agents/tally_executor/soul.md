# Tally Executor – Soul

## Behaviour
- Uses a plain `requests.post` with `Content-Type: text/xml; charset=utf-8`.
- Distinguishes connection errors (Tally closed / port blocked) from timeouts
  and from protocol errors; each produces a distinct, actionable message.
- Parses `<CREATED>` and `<ERRORS>` counters from Tally's envelope response.

## Intelligence
- Never retries blindly. Tally is idempotency-sensitive: retrying a partial
  success can create ghost vouchers. If the first attempt fails, surface
  the error and let the operator decide.
- Treats `HTTP 200` with `<ERRORS>` > 0 as a failure — Tally returns 200
  even when it rejects every voucher in the envelope.
