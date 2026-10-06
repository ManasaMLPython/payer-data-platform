-- Account-level: one database per environment.
-- Time Travel retention differs by environment: PROD keeps 7 days of history for recovery,
-- DEV/TEST keep 1 day to save storage.

USE ROLE SYSADMIN;

CREATE DATABASE IF NOT EXISTS DEV_DB
  DATA_RETENTION_TIME_IN_DAYS = 1
  COMMENT = 'Payer data platform - DEV environment';

CREATE DATABASE IF NOT EXISTS TEST_DB
  DATA_RETENTION_TIME_IN_DAYS = 1
  COMMENT = 'Payer data platform - TEST environment';

CREATE DATABASE IF NOT EXISTS PROD_DB
  DATA_RETENTION_TIME_IN_DAYS = 7
  COMMENT = 'Payer data platform - PROD environment';