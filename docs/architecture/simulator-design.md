# Source simulator — design (v1)

- **Ticket:** PAYER-13 · **Build:** Sprint 5 (PAYER-40, PAYER-41)
- **Purpose:** act as the upstream claims and eligibility systems: turn CMS Synthetic Medicare files into production-style deliveries that follow `docs/contracts/`, and deliberately break the contract on a planned schedule.

## 1. Inputs and outputs
| | Location |
|---|---|
| Source data (read only) | `cms_raw_source/` (outside the repo) |
| Local working area | `cms_sim_work/<env>/` (outside the repo): generated files before upload, state, answer key |
| Deliveries | `s3://mb-payer-landing-<env>-<account id>/inbound/<feed>/load_date=YYYY-MM-DD/` |
| Configuration | `simulator/config/` in the repo: feeds, rates, drop calendar |

## 2. Business-date model
- Claim and pharmacy records are assigned to a **business date** = their driving date (`NCH_WKLY_PROC_DT`, `PD_DT`/`SRVC_DT`).
- A **cutover date** splits history:
  - before cutover → **backfill** files (large, loaded once with COPY INTO)
  - on/after cutover → **one daily delivery per business date**, Mon–Sat
- The cutover date is chosen after Sprint 2 profiling, so that daily deliveries cover enough days for every planned incident (target: 30–60 business dates).
- Eligibility: weekly full snapshot on Sundays; daily change files generated from eligibility events (section 5).

## 3. Reading the source
- Pipe-delimited, header row; **all columns read as text** (`dtype=str`, `keep_default_na=False`) so codes, IDs and ZIPs keep leading zeros and blanks stay blank.
- Large files are processed in chunks, never loaded whole into memory.
- Output columns keep the source order; appended columns (`CLM_STATUS_CD`, `CLM_VERSION_NUM`, `EXTRACT_TS`) go last, per `feed-contracts.md`.

## 4. Claim versioning
- First delivery of a claim: `CLM_STATUS_CD = O`, `CLM_VERSION_NUM = 1`.
- On later business dates, a configurable share of previously delivered claims is re-sent:
  - **Adjustment (A):** next version number, selected amounts changed.
  - **Void (V):** next version number, amounts negated.
- Defaults (configurable): 3% adjusted within 30 days, 0.5% voided.
- Every version issued is recorded in state so it is never duplicated or skipped.

## 5. Eligibility deliveries
- **Weekly full (Sunday):** all member rows for the current and prior reference year.
- **Daily change (Mon–Sat):** full rows for members affected by an event that day: new enrollment, termination, death date added, retroactive termination (injected).

## 6. Environments
| Env | Data | Behavior |
|---|---|---|
| DEV | ~1% of members, chosen by hash of BENE_ID; same members across all feeds | Fast iteration; injections optional |
| TEST | Frozen regression set generated once with a fixed seed | Same files every run; answer key lists expected results |
| PROD | All members | Daily deliveries with the full drop calendar of injected problems |

Uploading to PROD requires `--confirm-prod` (same guard as `scripts/upload_to_s3.py`).

## 7. Control files
For each data file, written after it: record count, sum of the feed's control-sum column, extract timestamp, sha256 of the `.gz` — per `delivery-standards.md` §4. Injectors that corrupt files run **before** the control file is computed, unless the injection is specifically a control-file mismatch.

## 8. Problem injection
### 8.1 Drop calendar (`simulator/config/drop_calendar.yaml`)
```yaml
# day = Nth daily business date after cutover
- day: 2
  feed: claims_professional
  injector: duplicate_file
- day: 3
  feed: claims_professional
  injector: overlap_rows
  params: {percent: 5, from_day: 1}
- day: 4
  feed: claims_professional
  injector: add_column
  params: {name: TELEHEALTH_IND, values: [Y, N]}
- day: 13
  feed: claims_professional
  injector: skip_delivery
```

### 8.2 Injector catalog
| Injector | Breaks | Expected detection |
|---|---|---|
| duplicate_file | Same content, new file name | File hash check |
| overlap_rows | Rows repeated from an earlier day | Unique key test in staging |
| add_column | New column appended | Header/contract check, schema evolution |
| reorder_columns | Columns reordered / renamed | Header/contract check |
| bad_types | `$1,200`, `N/A`, wrong date format | Row-level validation / TRY_ casts |
| malformed_rows | Unescaped delimiter, truncated last line | Load errors, COPY_HISTORY |
| late_claims | Service dates 60–90 days before business date | Incremental lookback design |
| orphan_members | Claims for members not yet in eligibility | Relationships test |
| invalid_codes | Bad ICD-10, NPI failing check digit, future dates | Custom generic tests |
| empty_file | Header only, count 0 | Valid per contract (no activity) |
| skip_delivery | No file | SLA check, source freshness |
| volume_spike | 10x rows | Row-count anomaly check |
| wrong_format | Comma delimiter, BOM | File-format parse errors |
| control_mismatch | Control count/sum disagrees with file | Reconciliation procedure |
| retro_termination | Member terminated back-dated | Snapshot / restatement |

### 8.3 Answer key (`cms_sim_work/<env>/answer_key.jsonl`)
One JSON line per injection:
```json
{"day": 3, "business_date": "2025-03-04", "feed": "claims_professional",
 "file": "CLM_PROF_20250304_01.txt.gz", "injector": "overlap_rows",
 "affected_keys": 2411, "expected_detection": "unique key test in staging"}
```
After each incident is handled, the answer key is compared with what the pipeline actually caught.

## 9. Reproducibility and state
- Random seed = fixed project seed + business date → regenerating a day gives identical files.
- `state.json` per environment: last business date delivered, files sent (name, hash), claim versions issued.
- Re-running a delivered day is refused unless `--force` is given (and then a new sequence number is used).

## 10. Command-line interface (planned)
python -m simulator backfill --env dev
python -m simulator run --env prod --days 1 --confirm-prod
python -m simulator status --env prod
python -m simulator reset --env dev

All commands support `--dry-run`.

## 11. Security
- Dedicated IAM user `payer-simulator`, separate access key.
- Permissions: `s3:PutObject` on `inbound/*` of the landing buckets only. No read, list or delete outside `inbound/`.
- The simulator never touches `quarantine/` or `archive/` — those belong to the receiver.

## 12. Open items
- [ ] Choose the cutover date after Sprint 2 profiling (needs driving-date min/max and daily volumes).
- [ ] Confirm source date format so injected bad dates are realistic.
- [ ] Decide adjustment fields changed per feed (paid amount only, or also codes).