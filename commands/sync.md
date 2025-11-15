---
description: Sync project docs, architecture, context layers (Global→Project→Branch→Task)
---

# Project Synchronization Protocol

**Purpose**: Sync documentation, architecture, context layers with git state

**Entry**: master-orchestrator-agent or documentation-agent

## Key Requirements
- Docs: `ai_docs/` with subfolders
- PRD: `ai_docs/architecture-design/PRD.md`
- Architecture: `ai_docs/architecture-design/Architecture_Technique.md`
- Context Hierarchy: Global → Project → Branch → Task (inheritance downward)
- Git Integration: Project/branch names match actual git
- No Duplicates: Check existing before creating
- Clean Updates: Update existing, don't create new versions

## Decision Tree
```
Start → Check Git? → Yes → Phase 1 Docs → Yes → Phase 2 Project/Branch → Yes
  → Phase 3 Context Layers → Yes → Phase 4 Verification → All Synced? → Complete
```

**Error Flow**: Stop → Document Issues → Fix Plan → Apply Updates → Verify → Return to Failed Phase

## Phase Summary

| Phase | Check | Error Action |
|-------|-------|--------------|
| 1 | Docs Updated | Stop → Create todo → Fix → Retry |
| 2 | Names Match Git | Stop → Create todo → Fix → Retry |
| 3 | Contexts Updated | Stop → Create todo → Fix → Retry |
| 4 | All Synced | If fail → Return to failed phase |

## Phase 1: Documentation Sync
| Doc | Action |
|-----|--------|
| PRD.md | UPDATE if exists (preserve structure), else GENERATE → Save to ai_docs/architecture-design/ |
| Architecture_Technique.md | UPDATE if exists (reflect actual impl), else GENERATE (DDD patterns) → Save |

## Phase 2: Project/Branch Sync
```python
# Get git info
project_name = git_repo_name
branch_name = current_git_branch

# Project: list → if not_found: create, if name_mismatch: update
# Branch: list → if not_found: create, if name_mismatch: update
```

## Phase 3: Context Layer Sync

| Level | Contains | Fields |
|-------|----------|--------|
| Global | User preferences, standards | standards, preferences, guidelines, sync_history |
| Project | Tech stack, workflow | technology_stack, team_preferences, project_workflow, local_standards |
| Branch | Dev focus, features | data, branch_info, branch_workflow, feature_flags, discovered_patterns |
| Task | Task-specific | (inherited from branch) |

## Phase 4: Verification
- [ ] PRD.md exists & current
- [ ] Architecture_Technique.md reflects actual
- [ ] Project name matches git
- [ ] Branch name matches git
- [ ] All contexts have data
- [ ] Inheritance working

## Success Criteria
All phases complete ✓

**Sync Instructions**: $ARGUMENTS
