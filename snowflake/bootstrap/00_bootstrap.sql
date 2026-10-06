-- One-time bootstrap: creates the home for account-level schemachange history.
-- Run once per Snowflake account, before any schemachange deployment:
--   snow sql -f snowflake/bootstrap/00_bootstrap.sql
-- Safe to re-run (IF NOT EXISTS).

USE ROLE SYSADMIN;

CREATE DATABASE IF NOT EXISTS PLATFORM_DB
  COMMENT = 'Platform administration: schemachange history for account-level migrations';