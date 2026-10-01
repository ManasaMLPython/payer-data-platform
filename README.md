# Payer Data Platform

Production-style healthcare payer analytics platform built on CMS Synthetic Medicare claims.

## Architecture
_Diagram and overview — added in PAYER-8._

## Environments
DEV / TEST / PROD — see docs/adr/ADR-001.

## Repository layout
| Folder | Purpose |
|---|---|
| snowflake/migrations | schemachange scripts for all Snowflake objects |
| dbt | dbt project (staging, intermediate, marts) |
| airflow | Airflow DAGs and config |
| simulator | Source-system simulator that produces daily file drops |
| scripts | Helper scripts (uploads, utilities) |
| docs | ADRs, delivery contracts, runbooks, postmortems |
| .github/workflows | CI/CD pipelines |

## Getting started
_Setup steps — added as the project grows._