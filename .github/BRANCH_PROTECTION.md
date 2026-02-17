# Branch Protection Configuration

This document describes the recommended branch protection rules for the StudioLoop repository.

## Required GitHub Settings

Navigate to: **Settings > Branches > Add branch protection rule**

### Protected Branch: `master` (or `main`)

Configure the following settings:

#### Required Status Checks

Enable **Require status checks to pass before merging** and select:

- `Backend Lint`
- `Backend Type Check`
- `Backend Tests`
- `Frontend Lint`
- `Frontend Type Check`
- `Frontend Tests`

#### Additional Settings

- [ ] **Require a pull request before merging**
  - Require 1 approval (optional for solo development)
  - Dismiss stale pull request approvals when new commits are pushed

- [x] **Require status checks to pass before merging**
  - Require branches to be up to date before merging

- [ ] **Require conversation resolution before merging** (optional)

- [ ] **Require signed commits** (optional)

- [ ] **Include administrators** (recommended to enforce rules for everyone)

## CI Workflow Name

The CI workflow is named `CI` and contains these jobs:
- `backend-lint`
- `backend-typecheck`
- `backend-test`
- `frontend-lint`
- `frontend-typecheck`
- `frontend-test`

## Notes

- Deployment workflows are deferred to Epic 16
- This configuration ensures all lint, type-check, and test jobs pass before merging
- The CI runs on all PRs targeting master/main branches
