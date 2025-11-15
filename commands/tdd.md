---
description: Complete TDD workflow - delegate to task-planning-agent
---

# TDD

**Purpose**: Implement feature using Test-Driven Development

**Delegate**: task-planning-agent via Task Tool

## Phases

| Phase | Action | Rule |
|-------|--------|------|
| 1 | Write Tests First | NO mock implementations, NO code yet |
| 2 | Verify Fail | Run tests, confirm failure |
| 3 | Commit Tests | Test files only |
| 4 | Implement Code | Minimal code to pass ALL tests |
| 5 | Verify | No overfitting, edge cases |
| 6 | Commit Implementation | Implementation only, no test changes |
| 7 | Documentation | Update/create docs (delegate to agent) |
| 8 | CHANGELOG | Update CHANGELOG.md (delegate to agent) |
| 9 | Complete MCP | Mark task complete, update context |

## TDD-Quick (Smaller Features)
1. Describe feature → Write ONLY tests
2. Run tests → Confirm fail
3. Write minimal code to pass
4. Iterate → All pass
5. Commit

**Feature Details**: $ARGUMENTS