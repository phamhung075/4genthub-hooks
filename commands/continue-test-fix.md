---
description: Fix MCP test issues - DDD-compliant, restart backend, verify DB
---

# Continue Test Fix

**Purpose**: Fix code issues found during testing (DDD-compliant)

## Architecture
**Flow**: MCP Tool(mcp) → mcp_controllers → Facade → Use Case → Repository → ORM → DB
**Flow**: API(frontend) → api_controllers → Facade → Use Case → Repository → ORM → DB
**Rule**: NO legacy patterns, NO fallbacks, NO migration mechanisms

## Key Requirements

| Requirement | Value |
|-------------|-------|
| Logs | `logs/backend.log` (tail 200 lines each check) |
| Environment | Keycloak auth + PostgreSQL docker (local) |
| Auth | Keycloak = source of truth |
| Rebuild | `docker-menu.sh` option R after each fix |
| DB Schema | ORM model = source of truth → Update DB to match ORM |
| Code | Clean code only, NO backward compatibility |

## Test Flow (Decision Tree)

```
Start → Initialize test-orchestrator-agent
  → Project Management (2 create, ops, delete 1) → Pass?
  → Git Branch (2 create, ops, delete 1) → Pass?
  → Task Management Branch 1 (5 tasks, ops) → Pass?
  → Task Management Branch 2 (2 tasks, ops) → Pass?
  → Subtask (4 per task, ops, complete) → Pass?
  → Task Completion (1 task) → Pass?
  → Context (all 4 layers) → Pass?
  → Document issues → Create fix prompts → Update contexts
```

**Error Flow**: Stop → Document in MD → DDD fixes → Restart → Verify DB → Return to failed test

**Test Issues**: $ARGUMENTS
