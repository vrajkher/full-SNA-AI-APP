# Extractor – Skills

## run(file_path) -> ExtractionResult
Read, normalise, filter, and return typed rows.

## Column Mapping
| Source header         | Target field        |
|-----------------------|---------------------|
| NEW BUDGET LINE       | `budget_line`       |
| Sr No.                | `sr_no`             |
| SLS Code              | `sls_code`          |
| Agency Code           | `agency_code`       |
| Claim No.             | `claim_no`          |
| Beneficiary Name      | `beneficiary_name`  |
| Account No.           | `account_no`        |
| Net Amount            | `net_amount`        |
| Settlement Date       | `settlement_date`   |
| Status Code           | `status_code`       |
| Status                | `status` (filter)   |
| In File Name          | `in_file_name`      |
| UTR No.               | `utr_no`            |
| CIN No.               | `cin_no`            |
| Reference No.         | `reference_no`      |
