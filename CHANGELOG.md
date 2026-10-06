# Changelog
All notable changes to this project are documented here.

## [Unreleased]
- Repository structure, README skeleton (PAYER-2)
- Branch protection ruleset, PR template, CODEOWNERS (PAYER-3)
- Jira–GitHub integration (PAYER-4)
- AWS account hardening: IAM admin user with MFA, monthly budget alert (PAYER-5)
- DEV/TEST/PROD landing buckets via CloudFormation, us-east-2 (PAYER-6)
- AWS CLI setup and S3 upload helper with dry-run and PROD guard (PAYER-7)
- ADR-001 environment strategy, architecture diagram v1 (PAYER-8)
- Compression script for CMS samples; 5 feeds landed in DEV sample/ (PAYER-10)
- Source column layouts and feed mapping for 5 feeds (PAYER-11)
- Delivery standards and feed contracts v0.9 draft (PAYER-12)
- Source simulator design (PAYER-13)
- Snowflake account (Enterprise, AWS us-east-2), key-pair access and CLI connection runbook (PAYER-14)
- schemachange with account and environment layers; DEV/TEST/PROD databases; RAW/AUDIT/UTIL schemas in DEV (PAYER-15)
- RBAC: roles per environment, program users, privileges with future grants; deployed and tested in DEV (PAYER-16)