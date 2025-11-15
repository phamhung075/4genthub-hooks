---
description: Generate AI-optimized fix prompts per issue (comprehensive context)
---

# Prompt To Fix

**Purpose**: Generate comprehensive fix prompts for new chat sessions

## Prompt Template (Per Issue)

```markdown
# Fix Issue: [TITLE] (Issue #[NUMBER])

## Context & Background
**Problem**: [Clear description]
**Impact**: [User/system effects]
**Root Cause**: [Technical analysis]
**Priority**: [High/Medium/Low]

## Technical Specs
**System**: 4genthub Multi-Project AI Orchestration
**Architecture**: DDD (Domain → Application → Infrastructure → Interface)
**Database**: SQLite/PostgreSQL (hierarchical context)
**Framework**: FastMCP
**Testing**: TDD (unit/integration/e2e)

## Implementation

| Requirement | Details |
|-------------|---------|
| Objective | [Specific, measurable goal] |
| Files | [Paths with line numbers] |
| Components | [Domain/repos/controllers] |
| Dependencies | [Imports/libraries] |
| API Changes | [If MCP tools affected] |

**Solution**: [Step-by-step with technical details]

## Testing Strategy

| Test Type | Requirements |
|-----------|--------------|
| Unit | Functionality, error handling, edge cases, mocks/stubs |
| Integration | E2E workflow, DB interaction, MCP tools, cross-component |

## Verification Checklist
- [ ] Original issue resolved
- [ ] No regressions
- [ ] Error handling improved
- [ ] Performance acceptable
- [ ] DDD principles followed
- [ ] Proper logging
- [ ] Type hints/docstrings
- [ ] Tests passing (>95%)
- [ ] Documentation updated

## Deliverables
1. Modified files + descriptions
2. New files (if any)
3. Test files
4. Fix documentation: `ai_docs/fixes/[issue-name]-fix.md`
5. Changelog entry

## Validation
```bash
pytest --cov=src tests/ -v
black src/ && isort src/ && flake8 src/ && mypy src/
```

## Success Criteria
[Specific, measurable criteria]

## Risk & Rollback
**High Risk**: [Components]
**Mitigation**: [Strategies]
**Rollback**: [Steps]
```

## Agent Selection

| Issue Type | Agent |
|------------|-------|
| Bug fixes | debugger-agent |
| Features | coding-agent |
| Testing | test-orchestrator-agent |
| Security | security-auditor-agent |
| Docs | documentation-agent |

**Issue Details**: $ARGUMENTS
