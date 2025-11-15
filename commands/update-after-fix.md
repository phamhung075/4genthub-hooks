---
description: Post-fix checklist - docs, tests, validation, quality checks
---

# Post-Fix Update Checklist

**Summary**: $ARGUMENTS

## 1. Update Documentation

| File | Format | Include |
|------|--------|---------|
| CHANGELOG.md | [Keep a Changelog](https://keepachangelog.com/) | Added/Changed/Deprecated/Removed/Fixed/Security |
| CLAUDE.local.md | Date (YYYY-MM-DD) | Description, impact, files, test coverage |
| Related Docs | API/troubleshooting/architecture | If MCP tools/issues/system changed |

## 2. Test Impact Analysis

| Step | Action |
|------|--------|
| Identify | Review modified files, dependent modules, integration points, MCP tools |
| Find Tests | `find . -name "test_*.py" -exec grep -l "keyword" {} \;` |
| Update/Create | Update existing unit tests, add new tests, update integration, add regression |

## 3. Validation Testing

```bash
# Run tests
pytest tests/unit/
pytest tests/integration/

# Validate fix + edge cases + no regressions
```

**If applicable**: Performance benchmarks, memory usage, response times

**Add issue doc**: `ai_docs/issues/` if this is a fix

## 4. Code Quality

```bash
# Lint & format
flake8 src/ && black src/ && isort src/ && mypy src/
```

## 5. Final Review
- [ ] Code follows conventions
- [ ] Proper docstrings
- [ ] Comprehensive error handling
- [ ] Appropriate logging
- [ ] No debugging code

**Change Summary**: $ARGUMENTS
