# Delivery standards — all feeds (v0.9 draft)

- **Ticket:** PAYER-12 · **Status:** Draft — finalized as v1.0 after Sprint 2 profiling (PAYER-20)
- **Source owner:** Claims & Eligibility Systems (simulated by `simulator/`)
- **Receiver:** Data Platform team (Manasa Bitla)
- **Applies to:** all feeds in `feed-contracts.md`

## 1. Delivery location
`s3://mb-payer-landing-<env>-<account id>/inbound/<feed>/load_date=YYYY-MM-DD/`
- Production deliveries go to the PROD bucket only. Lower environments receive test or de-identified files.
- The source has write access to `inbound/` only. `quarantine/` and `archive/` are managed by the receiver.

## 2. File naming
`<FEEDCODE>_<YYYYMMDD>_<NN>.txt.gz`
- `YYYYMMDD` = business date (the processing/paid date the file covers).
- `NN` = sequence number, starting at `01`. A resend or additional file for the same date uses the next number. A file name is never reused.
- Example: `CLM_PROF_20260301_01.txt.gz`

## 3. File format
| Property | Standard |
|---|---|
| Delimiter | Pipe (`\|`) |
| Header row | Yes, exactly matching the contracted layout |
| Text qualifier | Double quote, only when a value contains a pipe, quote or newline |
| Encoding | UTF-8 without BOM |
| Line endings | LF |
| Compression | gzip (`.gz`) |
| Dates | As in the source layout — exact format confirmed in Sprint 2 profiling |
| Amounts | Plain decimal, `.` separator, no currency symbols or thousands separators, negatives with leading `-` |
| Nulls | Empty field (nothing between delimiters) |

## 4. Control file
Every data file is followed by a control file with the same name plus `.ctl.json`:
```json
{
  "file_name": "CLM_PROF_20260301_01.txt.gz",
  "feed": "claims_professional",
  "business_date": "2026-03-01",
  "record_count": 48210,
  "control_sum_column": "CLM_PMT_AMT",
  "control_sum": 3824117.52,
  "extract_ts": "2026-03-02T04:12:09Z",
  "sha256": "<hash of the .gz file>"
}
```
- `record_count` excludes the header row.
- `control_sum` is a hash total: the plain sum of the named column across all rows. It is used for reconciliation, not as a business figure.
- The control file is written **last**. The receiver does not load a data file until its control file has arrived.

## 5. Empty days
A day with no activity is delivered as a header-only data file plus a control file with `record_count: 0`. A missing file is an SLA breach, not "no activity".

## 6. Validation and failure handling
**File-level checks** — failure quarantines the whole file (`quarantine/<feed>/`) and notifies the source:
- File name does not match the pattern
- Header does not match the contracted layout
- Control file missing after the SLA, or record count / control sum mismatch
- File already received (same sha256 as a previously loaded file)
- Unreadable file (bad compression, wrong delimiter, wrong encoding)

**Row-level checks** — failing rows are rejected to an error table with a reason; valid rows load:
- Invalid date or amount format
- Missing business key
- Feed-specific rules in `feed-contracts.md`

If more than **1%** of rows fail row-level checks, the whole file is quarantined instead.

## 7. Resends and corrections
- Corrected files are sent with the next sequence number and a matching control file.
- The receiver deduplicates on business key + version and on file hash.
- The source states in the notification which earlier file a resend replaces.

## 8. Schema change management
- Minimum **30 days' notice** for any layout change.
- **Additive changes** (new columns) are appended at the end of the layout → minor contract version (e.g. v1.1).
- **Breaking changes** (rename, reorder, remove, type change) → major contract version (e.g. v2.0), with a parallel-run period.
- The contract version in effect is recorded in this repository; changes go through a pull request.

## 9. Retention
- Successfully loaded files are moved to `archive/<feed>/load_date=YYYY-MM-DD/`.
- Archive moves to infrequent-access storage after 30 days (bucket lifecycle rule).

## 10. Contacts and escalation
| Situation | Action |
|---|---|
| File missing at SLA | Alert receiver on-call; contact source owner |
| File quarantined | Notify source owner with file name and failure reason; request resend |
| Breaking change without notice | Quarantine; escalate to source owner and data platform lead |