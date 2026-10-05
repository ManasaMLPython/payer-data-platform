# Feed contracts (v0.9 draft)

Common rules: `delivery-standards.md`. Column layouts: `source_layouts/`. Mapping and grain: `feed-mapping.md`.
SLA times are US Eastern.

## Summary
| Feed | Feed code | Schedule | SLA | Load type | Business key | Control sum column |
|---|---|---|---|---|---|---|
| claims_professional | CLM_PROF | Daily, Mon–Sat | 06:00 | Delta by NCH_WKLY_PROC_DT | CLM_ID + LINE_NUM + CLM_VERSION_NUM | CLM_PMT_AMT |
| claims_inpatient | CLM_INP | Daily, Mon–Sat | 06:00 | Delta by NCH_WKLY_PROC_DT | CLM_ID + CLM_LINE_NUM + CLM_VERSION_NUM | CLM_PMT_AMT |
| claims_outpatient | CLM_OUTP | Daily, Mon–Sat | 06:00 | Delta by NCH_WKLY_PROC_DT | CLM_ID + CLM_LINE_NUM + CLM_VERSION_NUM | CLM_PMT_AMT |
| pharmacy | RX_PDE | Daily, Mon–Sat | 06:00 | Delta by PD_DT (fallback SRVC_DT) | PDE_ID + CLM_VERSION_NUM | TOT_RX_CST_AMT |
| eligibility | ELIG | Weekly full (Sun) + daily changes (Mon–Sat) | 06:00 | Full / change | BENE_ID + BENE_ENROLLMT_REF_YR | none (record count only) |

## Columns appended to the source layout (all claim and pharmacy feeds)
Production feeds carry claim lifecycle fields that the CMS source does not. They are appended **after** the source columns:

| Column | Type | Values | Meaning |
|---|---|---|---|
| CLM_STATUS_CD | char(1) | O, A, V | Original, Adjustment, Void |
| CLM_VERSION_NUM | integer | 1, 2, … | Increments each time a claim is adjusted or voided |
| EXTRACT_TS | timestamp | ISO 8601 UTC | When the source system extracted the record |

A void (`V`) repeats the claim with amounts negated. The current state of a claim is its highest CLM_VERSION_NUM.

## claims_professional (CLM_PROF)
- **Layout:** `source_layouts/claims_professional.txt` (96 columns) + appended columns.
- **Contains:** all professional claim lines processed on the business date, including adjustments and voids of previously sent claims.
- **Feed-specific row rules:** PRF_PHYSN_NPI 10 digits; HCPCS_CD present; CLM_FROM_DT ≤ CLM_THRU_DT ≤ NCH_WKLY_PROC_DT.

## claims_inpatient (CLM_INP)
- **Layout:** `source_layouts/claims_inpatient.txt` (197 columns) + appended columns.
- **Feed-specific row rules:** CLM_ADMSN_DT ≤ NCH_BENE_DSCHRG_DT; CLM_DRG_CD present; ORG_NPI_NUM 10 digits.

## claims_outpatient (CLM_OUTP)
- **Layout:** `source_layouts/claims_outpatient.txt` (162 columns) + appended columns.
- **Feed-specific row rules:** REV_CNTR present; REV_CNTR_DT within CLM_FROM_DT–CLM_THRU_DT.

## pharmacy (RX_PDE)
- **Layout:** `source_layouts/pharmacy.txt` (36 columns) + appended columns.
- **Feed-specific row rules:** PROD_SRVC_ID is 11 digits (NDC); QTY_DSPNSD_NUM > 0; DAYS_SUPLY_NUM between 1 and 365.

## eligibility (ELIG)
- **Layout:** `source_layouts/eligibility.txt` (185 columns), identical across years.
- **Weekly full file (Sunday):** every member for the current and prior reference year. Replaces the previous full snapshot.
- **Daily change file (Mon–Sat):** only members whose record changed (new enrollment, termination, coverage change, death date, retroactive changes).
- **Feed-specific row rules:** BENE_BIRTH_DT not in the future; BENE_DEATH_DT ≥ BENE_BIRTH_DT when present.

## Open items for v1.0 (Sprint 2)
- [ ] Confirm date format in each file and record it in delivery-standards §3.
- [ ] Confirm PD_DT is populated for pharmacy; otherwise switch the driving date to SRVC_DT.
- [ ] Confirm business keys are unique in the source.
- [ ] Confirm NDC length and format in PROD_SRVC_ID.
- [ ] Decide whether the eligibility change file carries the full row or changed columns only (recommendation: full row).