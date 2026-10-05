# Sprint 1 — Source discovery & contracts

**Dates:** Oct 3, 2026 (planned Oct 5 – Oct 7; started early, finished early)
**Goal:** CMS files in DEV S3 sample/, feeds mapped, draft delivery contracts, simulator design — **Met**

## Delivered
| Ticket | Item |
|---|---|
| PAYER-9 | CMS Synthetic Medicare source downloaded and organized: beneficiary (11 years), 7 FFS claim types, Part D, 3 codebooks, user guide (~1 GB raw) |
| PAYER-10 | Compression script; 5 feeds landed in DEV `sample/` — 15 objects, 59.3 MiB (~922 MB raw) |
| PAYER-11 | Column layouts extracted for 5 feeds; feed mapping (grain, keys, driving dates, joins, DQ rules, gaps) |
| PAYER-12 | Delivery standards and feed contracts v0.9 |
| PAYER-13 | Source simulator design |

**Planned hours:** 10.5 · **Actual hours:** __

## Key findings
- All source files are **pipe-delimited despite the .csv extension**.
- Beneficiary layout is identical across 2015–2025 (185 columns).
- Claim files are line-level with claim-level amounts repeated per line: summing CLM_PMT_AMT across lines double-counts.
- Claim feeds will be split by **processing date** (NCH_WKLY_PROC_DT), so late-arriving claims occur naturally.
- Source has final-action claims only; the simulator must generate adjustments and voids.
- High compression ratios (carrier 28x) suggest many mostly-empty repeating columns — to confirm in profiling.

## What went well
- Assumptions verified against the real files (60 expected columns checked automatically, all found).
- Source data kept read-only outside the repo; compression and layouts produced by repeatable scripts.

## What didn't go well
- Part D data file initially missing (only the user guide was saved) — caught by the inventory check.
- Folder names had spaces and a typo — renamed before any script depended on them.
- Virtual environment not active in one session — caught before running the boto3 upload.

## Changes for next sprint
- Run the inventory/verification step before closing any data ticket.
- Check the prompt shows `(.venv)` at the start of every session.