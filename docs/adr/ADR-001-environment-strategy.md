# ADR-001: Environment strategy (DEV / TEST / PROD)

- **Status:** Accepted
- **Date:** 2026-10-02
- **Decider:** Manasa Bitla
- **Ticket:** PAYER-8

## Context
The platform must behave like a production healthcare payer data platform:
code changes are promoted through environments, PROD only changes through an
approved pipeline, and real production incidents can be handled without risk
to development work. Constraints: one person, one personal AWS account,
a Snowflake trial/pay-as-you-go account, and a monthly cost target under $10
for AWS. Data is synthetic (CMS Synthetic Medicare) but is treated as PHI.

## Decision
1. **Three environments:** DEV, TEST, PROD.
2. **AWS landing zone:** one AWS account, one S3 landing bucket per environment,
   created from a single CloudFormation template (`infra/aws/s3-landing-bucket.yaml`).
   Naming: `mb-payer-landing-<env>-<account id>`. Versioning, SSE-S3 encryption,
   public access blocked, HTTPS-only bucket policy, lifecycle rules.
   PROD stack has termination protection.
3. **Region:** `us-east-2` (Ohio) for all AWS resources. The Snowflake account
   will be created in AWS us-east-2 to avoid cross-region transfer cost and latency.
4. **Snowflake:** one account with separate databases `DEV_DB`, `TEST_DB`, `PROD_DB`,
   per-environment warehouses, roles and resource monitors. All objects are
   deployed by schemachange migrations; no manual changes in PROD.
5. **Data per environment:**
   - DEV: small sample extracts for building.
   - TEST: frozen regression dataset with known expected results.
   - PROD: daily file drops from the source simulator, including injected
     real-world issues.
6. **Code promotion:** `feature/*` → PR → `develop` (deploys to TEST) →
   release PR → `main` (deploys to PROD). `develop` and `main` are protected:
   pull request required, no force pushes, no deletion.

## Alternatives considered
- **Separate AWS account per environment.** Enterprise standard (strongest
  isolation, separate billing and IAM). Rejected here for cost and setup effort
  for a single developer; recommended for a real production deployment.
- **Separate Snowflake account per environment.** Rejected: database-level
  separation with RBAC gives enough isolation for this project at no extra cost.
- **Single environment with separate schemas.** Rejected: no realistic promotion
  path, and testing would risk production data.
- **us-east-1 (N. Virginia).** Originally intended. Resources were created in
  us-east-2; recreating them would add effort with no benefit, so us-east-2
  was standardized instead.

## Consequences
- **Positive:** realistic DEV → TEST → PROD promotion; every environment built
  from the same code; PROD protected by branch rules, termination protection,
  and an explicit `--confirm-prod` guard in upload tooling.
- **Negative:** a shared AWS account means a mistake can reach any environment.
  Mitigated by naming conventions, least-privilege IAM users for automation
  (planned), and PROD guards. A shared Snowflake account means environments
  share account-level limits; mitigated by per-environment warehouses and
  resource monitors.