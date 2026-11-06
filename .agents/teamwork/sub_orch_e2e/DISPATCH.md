# Task Assignment: E2E Testing Orchestrator

## Objective
Lead the E2E Testing Track for Gift-Christmas. Design and implement a comprehensive, opaque-box, multi-tier test suite verifying all features F1-F8 defined in `PROJECT.md`. When complete, publish `TEST_INFRA.md` and `TEST_READY.md`.

## Context & Inputs
- Original Request: `e:\GitHub\Gift-Christmas\.agents\teamwork\ORIGINAL_REQUEST.md`
- Project Master Plan: `e:\GitHub\Gift-Christmas\.agents\teamwork\PROJECT.md`
- Working Directory: `e:\GitHub\Gift-Christmas\.agents\teamwork\sub_orch_e2e\`
- Parent ID: `a3ecd048-76ad-4b80-b218-217734502789`

## Test Methodology & Requirements
Follow Dual Track: E2E Testing Track principles:
1. **Opaque-box & Requirement-driven**: Derive test cases from `ORIGINAL_REQUEST.md` and `PROJECT.md § Feature Inventory` (F1 to F8).
2. **Test Infrastructure**:
   - Write test suite in `e:\GitHub\Gift-Christmas\tests\verify_e2e.py` (or similar executable script using Python 3.12 / headless Chrome).
   - Create `TEST_INFRA.md` at `e:\GitHub\Gift-Christmas\.agents\teamwork\TEST_INFRA.md`.
3. **4-Tier Test Coverage**:
   - Tier 1: Feature Coverage (>=5 per feature for F1-F8).
   - Tier 2: Boundary & Corner Cases (empty/long messages, viewport limits, resize).
   - Tier 3: Cross-Feature Combinations (typewriter + audio + responsive + scroll).
   - Tier 4: Real-World Application Scenarios (Desktop, Mobile portrait, Mobile landscape full flow).
4. **Publish Signal**:
   - Once test suite is implemented and ready to test `index.html`, write `TEST_READY.md` at `e:\GitHub\Gift-Christmas\.agents\teamwork\TEST_READY.md`.

## Output Requirements
- Orchestrate via subagents (Explorer -> Worker / Test Writer -> Reviewer -> Challenger -> Auditor) or execute sub-milestones.
- Write your progress to `e:\GitHub\Gift-Christmas\.agents\teamwork\sub_orch_e2e\progress.md`.
- Deliver `handoff.md` and report completion back to parent orchestrator.
