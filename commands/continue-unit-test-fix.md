---
description: Continue unit test creation following DDD - check coverage, fix errors
---

# Continue Unit Test Fix

**Purpose**: Fix failing + create missing unit tests (DDD patterns)

## Step 0: Architecture Review
- Read `ai_docs/architecture-design/Architecture_Technique.md` (technical)
- Read `ai_docs/architecture-design/PRD.md` (product)
- Understand 4 layers: Domain → Application → Infrastructure → Interface

## Step 0b: Fix Errors FIRST
- Check `agenthub_main/backend.log` for errors
- Root cause analysis (not just symptoms)
- Fix at appropriate layer
- Test fix doesn't break other components

## Step 0c: Check Coverage
```bash
# Coverage report → identify untested code
pytest --cov=src --cov-report=html
```

## Test Organization (DDD)
| Layer | Path | Test |
|-------|------|------|
| Domain | `/tests/unit/.../domain/` | Entities without dependencies, business rules |
| Application | `/tests/unit/.../application/` | Facades with mocked services, DTOs |
| Infrastructure | `/tests/unit/.../infrastructure/` | Repositories with test DB, ORM mappings |
| Interface | `/tests/unit/.../interface/` | MCP controllers with mocked facades |

## Coverage Requirements
- Minimum 80% per file
- 100% for domain logic
- Critical paths full coverage
- Edge cases + error paths

**Test Plan**: $ARGUMENTS
