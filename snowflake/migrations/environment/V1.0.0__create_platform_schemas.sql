-- Environment-level: platform-owned schemas. Deployed once per environment.
-- {{ database }} is supplied at deploy time (DEV_DB, TEST_DB or PROD_DB).
-- dbt creates and owns STAGING, INTERMEDIATE and MARTS itself.

USE ROLE SYSADMIN;
USE DATABASE {{ database }};

CREATE SCHEMA IF NOT EXISTS RAW WITH MANAGED ACCESS
  COMMENT = 'Source data as delivered: landing tables, stages, file formats, pipes';

CREATE SCHEMA IF NOT EXISTS AUDIT WITH MANAGED ACCESS
  COMMENT = 'Pipeline metadata: file load log, reconciliation, rejected rows, run history';

CREATE SCHEMA IF NOT EXISTS UTIL WITH MANAGED ACCESS
  COMMENT = 'Shared code: UDFs and stored procedures';