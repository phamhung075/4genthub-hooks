---
description: Continue fixing/creating unit tests following DDD patterns
---

# Continue Unit Test

**Purpose**: Fix failing + create missing unit tests (DDD patterns)

## Architecture
**ORM Models**: `agenthub_main/src/fastmcp/task_management/domain/entities/*.py`
**Tests**: `agenthub_main/src/tests/`
**Rule**: ORM entity definitions = SOURCE OF TRUTH

## Test Categories
| Path | Type |
|------|------|
| `src/tests/unit/` | Unit tests |
| `src/tests/integration/` | Integration tests |
| `src/tests/e2e/` | E2E tests |
| `src/tests/performance/` | Performance tests |

## Priority
1. Domain layer entities/value objects
2. Application layer services/use cases
3. Infrastructure layer repositories
4. MCP interface controllers

## Commands
```bash
# All unit tests
cd agenthub_main && python -m pytest src/tests/unit/ -v

# Specific file
python -m pytest src/tests/unit/domain/test_entities.py -v

# With coverage
python -m pytest src/tests/unit/ --cov=src --cov-report=html
```

## Rules
1. Tests in `agenthub_main/src/tests/`
2. Follow existing patterns
3. Mock external dependencies
4. Isolated & repeatable
5. Update TEST-CHANGELOG.md
6. Follow DDD patterns

**Focus Area**: $ARGUMENTS
