# Snowflake objects (schemachange)

Every Snowflake object is created by a versioned SQL file in this folder — never by hand.

## Layout
| Folder | Purpose | Change history table |
|---|---|---|
| `bootstrap/` | One-time setup, run by hand once per account | — |
| `migrations/account/` | Objects that exist once per account (databases, warehouses, roles, integrations) | `PLATFORM_DB.SCHEMACHANGE.CHANGE_HISTORY` |
| `migrations/environment/` | Objects inside each environment database (schemas, stages, tables, pipes, UDFs) | `<ENV>_DB.SCHEMACHANGE.CHANGE_HISTORY` |

## Rules
- File names: `V<major>.<minor>.<patch>__<description>.sql`. Never edit a file after it has run — add a new version.
- Environment migrations use `{{ database }}`; never hard-code DEV_DB/TEST_DB/PROD_DB.
- Objects are created as SYSADMIN (or SECURITYADMIN/USERADMIN for roles and users), not ACCOUNTADMIN.
- DEV may be deployed by hand. TEST and PROD are deployed only by the CI/CD pipeline.
- Always `--dry-run` first.

## Commands
```powershell
. $HOME\.snowflake\payer-env.ps1          # once per terminal session (see payer-env.template.ps1)

# Bootstrap (once per account)
snow sql -f snowflake/bootstrap/00_bootstrap.sql

# Account layer
schemachange deploy --root-folder snowflake/migrations/account `
  --change-history-table PLATFORM_DB.SCHEMACHANGE.CHANGE_HISTORY --create-change-history-table --dry-run

# Environment layer (DEV)
schemachange deploy --root-folder snowflake/migrations/environment `
  --change-history-table DEV_DB.SCHEMACHANGE.CHANGE_HISTORY --create-change-history-table `
  --vars '{\"database\": \"DEV_DB\"}' --dry-run
```
Windows PowerShell strips double quotes from native-command arguments — hence `\"` inside `--vars`.

## Deployed so far
| Layer | Version | Creates |
|---|---|---|
| account | 1.0.0 | DEV_DB, TEST_DB (retention 1 day), PROD_DB (retention 7 days) |
| environment | 1.0.0 | RAW, AUDIT, UTIL schemas (managed access) |