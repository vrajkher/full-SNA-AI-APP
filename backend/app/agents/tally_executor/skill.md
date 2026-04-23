# Tally Executor – Skills

## run(xml: str) -> TallyPushResult
POSTs the XML to Tally and returns a structured result.

## Response Schema
```json
{
  "success": true,
  "status_code": 200,
  "response_text": "<ENVELOPE>…</ENVELOPE>",
  "imported": 1,
  "errors": 0
}
```

## Error Modes
| Condition            | `success` | `status_code` | Message                                           |
|----------------------|-----------|----------------|---------------------------------------------------|
| Tally not reachable  | false     | 0              | "Tally connection failed. …"                      |
| Request timeout      | false     | 0              | "Request to Tally timed out."                     |
| HTTP 200, errors>0   | false     | 200            | Full response body (Tally's own error XML)        |
| HTTP 200, errors=0   | true      | 200            | Full response body                                |
