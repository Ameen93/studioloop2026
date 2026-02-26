# Changelog

## Unreleased

### Changed
- Stabilized Epic 5 class scheduling merge into `master` and re-verified backend coverage after merge conflict/regression fixes.

### Risks & Mitigations (Epic 5 Merge)
- **Risk:** Persistent test DB state caused false regression in private user creation (`duplicate key` on fixed email test data).
  - **Mitigation:** Updated `test_private.py` to generate a unique email per run (`uuid4`) so test outcomes remain deterministic across reused local DB state.
- **Risk:** Scheduling feature merge could silently impact unrelated auth/private routes.
  - **Mitigation:** Executed full backend test suite (`uv run pytest`) after stabilization and confirmed all tests pass.
