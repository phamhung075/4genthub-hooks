---
description: Deep TDD analysis - existing tests/code/docs, root cause fixes
---

# TDD Analyze Fix

**Purpose**: Comprehensive analysis → remediation of tests/code/docs

**Delegate**: Different agents per task

## Phases

| Phase | Action | Rule |
|-------|--------|------|
| 1 | Deep Test Analysis | Read ALL tests, analyze quality/gaps, NO modifications yet |
| 2 | Code Context Analysis | Read code/docs/dependencies, map complete system context |
| 3 | System-Wide Impact | Identify obsolete components, compatibility issues, inconsistencies |
| 4 | Architecture/DB Verify | Call architecture/database agents, verify correctness |
| 5 | Strategic Planning | Think best strategy (test vs code vs architecture), prioritize |
| 6 | Compatibility | Identify incompatible/obsolete code, plan replacements |
| 7 | Task Creation & Handoff | Call task-planning agent with complete context |

## Phase 7: Task Context Package (Per Task)
- Analysis findings + root cause
- Code/test/doc relationship mapping
- Architecture/DB assessment results
- Compatibility issues + obsolescence
- Strategic approach + priority rationale
- Dependencies + prerequisites
- Success criteria + validation
- Risk assessment + mitigation

## Task Categories
Obsolete code removal | Architecture updates | DB schema changes | Test modernization | Documentation updates | Integration validation

**Quick Analyze** (tdd-quick-analyze): Smaller code sections, focused fixes

**Analysis Focus**: $ARGUMENTS
