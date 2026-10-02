# Sprint 0 — Project & platform setup

**Dates:** Oct 1 – Oct 2, 2026 (planned Oct 1 – Oct 4)
**Goal:** Jira, GitHub, AWS foundations and ADR-001 in place — **Met**

## Delivered
| Ticket | Item |
|---|---|
| PAYER-1 | Jira project, board with 5-column workflow, 15 epics, 10 sprints, 81-ticket backlog via CSV import |
| PAYER-2 | GitHub repo, folder structure, README, .gitignore, .gitattributes, CHANGELOG |
| PAYER-3 | Branch ruleset on main/develop (PR required, no force push/delete), PR template, CODEOWNERS |
| PAYER-4 | GitHub for Atlassian: branches/commits/PRs linked to Jira tickets |
| PAYER-5 | Root MFA, IAM admin user with MFA, billing access for IAM, $10 monthly budget alert |
| PAYER-6 | DEV/TEST/PROD landing buckets from one CloudFormation template (us-east-2) |
| PAYER-7 | AWS CLI configured, upload helper with dry-run and PROD guard |
| PAYER-8 | ADR-001 environment strategy, architecture diagram v1 |

**Planned hours:** 14.0 · **Actual hours:** __

## What went well
- Infrastructure as code from the start (CloudFormation) instead of console clicks.
- Branch protection verified by deliberately attempting a direct push.
- Jira–GitHub traceability working through ticket keys in branches, commits and PR titles.

## What didn't go well
- `git init` first ran in the parent folder; caught by checking `git status` before committing.
- A commit landed on local `develop` before the feature branch existed; fixed by branching and resetting.
- AWS resources created in us-east-2 instead of the intended us-east-1; standardized on us-east-2 (ADR-001).
- Jira backfill of older commits was slow; verified the link with a new commit instead of waiting.

## Changes for next sprint
- Always create the branch before editing files.
- Check the AWS region and the terminal folder before running anything.
- Run `git status` before every `git add`.