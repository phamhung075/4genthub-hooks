│ # AI-Optimized Issue Fix Prompt Generator

## Purpose
Generate comprehensive, AI-friendly prompts for each issue that provide complete context, clear instructions, and systematic verification steps for implementation in a new chat session.

## Prompt Structure Template

For each issue, generate a prompt following this structured format:

### 🔍 ISSUE ANALYSIS PROMPT TEMPLATE

```markdown
# Fix Issue: [ISSUE_TITLE] (Issue #[NUMBER])

## 🎯 CONTEXT & BACKGROUND
**Problem**: [Clear description of the issue]
**Impact**: [How this affects users/system]
**Root Cause**: [Technical analysis of what's root causing the issue]
**Priority**: [High/Medium/Low based on impact]

## 📋 TECHNICAL SPECIFICATIONS
**System**: 4genthub Multi-Project AI Orchestration Platform
**Architecture**: Domain-Driven Design (DDD) with 4-tier context hierarchy
```
┌──────────────────────────────────────────────────────┐
│                  MCP Request Entry                   │
└────────────────────┬─────────────────────────────────┘
                     ↓
┌──────────────────────────────────────────────────────┐
│         INTERFACE LAYER (Controllers)                │
│  • Receive MCP requests                              │
│  • Validate input parameters                         │
│  • Format responses                                  │
└────────────────────┬─────────────────────────────────┘
                     ↓
┌──────────────────────────────────────────────────────┐
│      APPLICATION LAYER (Facades & Use Cases)         │
│  • Orchestrate business logic                        │
│  • Manage transactions                               │
│  • Coordinate between services                       │
└────────────────────┬─────────────────────────────────┘
                     ↓
┌──────────────────────────────────────────────────────┐
│         DOMAIN LAYER (Entities & Services)           │
│  • Business rules and logic                          │
│  • Domain entities and value objects                 │
│  • Repository interfaces (abstractions)              │
└────────────────────┬─────────────────────────────────┘
                     ↓
┌──────────────────────────────────────────────────────┐
│     INFRASTRUCTURE LAYER (Implementations)           │
│                                                      │
│  ┌─────────────────────────────────────────┐         │
│  │         Repository Factory               │        │
│  │  Decides which implementation to use     │        │
│  └──────────────┬──────────────────────────┘         │
│                 ↓                                    │
│  ┌──────────────────────────────────────────┐        │
│  │     Environment Detection                │        │
│  └──────┬───────────────────┬───────────────┘        │
│         ↓                   ↓                        │
│    TEST MODE           PRODUCTION MODE               │
│         ↓                   ↓                        │
│  ┌──────────────┐   ┌──────────────┐                 │
│  │   SQLite     │   │   Supabase   │                 │
│  │  Repository  │   │  Repository  │                 │
│  └──────────────┘   └───────┬──────┘                 │
│                             ↓                        │
│                    ┌─────────────────┐               │
│                    │ Cache Enabled?  │               │
│                    └────┬──────┬─────┘               │
│                        YES     NO                    │
│                         ↓       ↓                    │
│                  ┌─────────┐  ┌──────────┐           │
│                  │  Redis  │  │  Direct  │           │
│                  │  Cache  │  │ Database │           │
│                  └─────────┘  └──────────┘           │
└──────────────────────────────────────────────────────┘
```
**Database**: SQLite/PostgreSQL with hierarchical context support
**Framework**: FastMCP with MCP tools integration
**Testing**: TDD approach with unit/integration/e2e coverage

## 🔧 IMPLEMENTATION REQUIREMENTS

### Primary Objective
[Specific, measurable goal for the fix]

### Technical Details
- **Files to Modify**: [List specific files with line numbers if known]
- **Components Affected**: [Domain services, repositories, controllers, etc.]
- **Dependencies**: [Required imports, libraries, or system components]
- **API Changes**: [If MCP tools or endpoints are affected]

### Solution Approach
1. [Step 1 with technical details]
2. [Step 2 with implementation specifics]
3. [Step 3 with validation requirements]

## 🧪 TESTING STRATEGY

### Unit Tests Required
- [ ] Test for [specific functionality]
- [ ] Error handling validation
- [ ] Edge case coverage
- [ ] Mock/stub requirements

### Integration Tests Required
- [ ] End-to-end workflow testing
- [ ] Database interaction validation
- [ ] MCP tool integration testing
- [ ] Cross-component interaction

### Test Files to Create/Update
- `tests/[domain]/[component]/test_[specific_fix].py`
- `tests/integration/test_[integration_scenario].py`

## 🔍 VERIFICATION CHECKLIST

### 1. Implementation Verification
- [ ] Original issue symptoms resolved
- [ ] No regressions introduced
- [ ] Error handling improved
- [ ] Performance impact acceptable

### 2. Code Quality Standards
- [ ] Follows DDD principles
- [ ] Proper error handling
- [ ] Comprehensive logging
- [ ] Type hints and docstrings
- [ ] Clean, readable code

### 3. Testing Coverage
- [ ] Unit tests passing (>95% coverage)
- [ ] Integration tests passing
- [ ] Edge cases covered
- [ ] Error scenarios tested

### 4. Documentation Updates
- [ ] CHANGELOG.md updated
- [ ] CLAUDE.local.md updated
- [ ] API documentation (if tools changed)
- [ ] Architecture ai_docs (if system changed)
- [ ] Troubleshooting guides (if fixing known issues)

### 5. System Integration
- [ ] Docker container functionality
- [ ] Database connectivity
- [ ] MCP tools working correctly
- [ ] No circular import issues
- [ ] Async/sync compatibility

## 📝 EXPECTED DELIVERABLES

### Code Changes
1. **Modified Files**: [List with brief description of changes]
2. **New Files**: [If any new files need to be created]
3. **Test Files**: [Comprehensive test coverage]

### Documentation
1. **Fix Documentation**: Create `ai_docs/fixes/[issue-name]-fix.md`
2. **Changelog Entry**: Update with fix details
3. **API Updates**: If MCP tools are affected

## 🚀 POST-IMPLEMENTATION VALIDATION

### Automated Testing
```bash
# Run comprehensive test suite
pytest --cov=src tests/ -v

# Validate MCP tools if affected
python -c "from fastmcp.mcp_tools import [affected_tool]; print('Tool loads successfully')"

# Code quality checks
black src/ && isort src/ && flake8 src/ && mypy src/
```

### Manual Verification
1. **Reproduce Original Issue**: Verify it no longer occurs
2. **Test User Workflows**: Ensure normal operations work
3. **Performance Check**: Verify no significant slowdown
4. **Error Scenarios**: Test graceful error handling

### Integration Testing
- [ ] Docker container rebuild and test
- [ ] Database migrations (if applicable)
- [ ] MCP server restart and validation
- [ ] Frontend integration (if UI changes)

## 🎯 SUCCESS CRITERIA
[Define specific, measurable criteria that indicate the fix is complete and successful]

## ⚠️ RISK ASSESSMENT
**High Risk Areas**: [Components that could be affected]
**Mitigation Strategies**: [How to minimize risk]
**Rollback Plan**: [Steps to revert if issues arise]

## 🔗 RELATED ISSUES/DEPENDENCIES
[Link to related issues or dependencies that might be affected]

## 💡 IMPLEMENTATION NOTES
[Any additional context, gotchas, or important considerations for the developer]
```

## 🤖 AI AGENT INSTRUCTIONS

When generating issue fix prompts:

### 1. AGENT SELECTION
Use appropriate agent based on issue type:
- `debugger-agent`: For bug fixes and troubleshooting
- `coding-agent`: For feature implementation
- `test-orchestrator-agent`: For testing-related issues
- `security-auditor-agent`: For security fixes
- `documentation-agent`: For documentation issues

### 2. CONTEXT RESOLUTION
Always include:
```python
# Standard context resolution
mcp__agenthub_http__manage_context(
    action="resolve",
    level="task",
    context_id=task_id,
    include_inherited=True
)
```

### 3. SYSTEMATIC APPROACH
Follow the agenthub operation sequence:
1. Health check and agent switching
2. Context resolution
3. Task status updates
4. Implementation with progress tracking
5. Comprehensive testing
6. Documentation updates
7. Final verification

### 4. VALIDATION FRAMEWORK
Each prompt must include:
- Pre-implementation validation checklist
- Implementation verification steps
- Post-implementation testing protocol
- Documentation update requirements
- System integration checks

## 📋 USAGE INSTRUCTIONS

1. **Identify Issue**: Analyze the issue for technical requirements
2. **Select Template**: Use the appropriate prompt template above
3. **Customize Content**: Fill in issue-specific details
4. **Add Verification**: Include comprehensive post-fix validation
5. **Generate Prompt**: Create complete, self-contained prompt for new chat
6. **Include Context**: Add all necessary technical context and system information

## 🔄 POST-FIX VERIFICATION INTEGRATION

After implementing any fix, systematically follow the verification checklist from `update-after-fix.md`:

### Immediate Verification
1. **Test Suite**: Run all relevant tests
2. **Integration Check**: Verify system still works end-to-end
3. **Documentation**: Update all affected documentation
4. **Code Quality**: Run linting, formatting, and type checking

### Documentation Updates
1. **CHANGELOG.md**: Add fix entry with proper categorization
2. **CLAUDE.local.md**: Update project changelog with technical details
3. **Issue Documentation**: Create fix documentation in `ai_docs/issues/`
4. **API Reference**: Update if MCP tools were modified

### System Validation
1. **Docker Testing**: Rebuild and test containers
2. **Database Integration**: Verify database operations
3. **MCP Tools**: Test all affected MCP tools
4. **Performance**: Ensure no degradation

This comprehensive approach ensures every fix is thoroughly implemented, tested, and documented for long-term project health.