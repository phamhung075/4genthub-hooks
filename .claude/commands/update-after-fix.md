# Post-Fix Update Checklist
#Summary of change: 
$ARGUMENTS
This document provides a systematic checklist to follow after implementing any bug fix or feature change in actual task.

## 1. Update Documentation

### 1.1 Update CHANGELOG.md
- [ ] Add entry in appropriate version section
- [ ] Follow [Keep a Changelog](https://keepachangelog.com/) format
- [ ] Include:
  - **Added** - for new features
  - **Changed** - for changes in existing functionality
  - **Deprecated** - for soon-to-be removed features
  - **Removed** - for now removed features
  - **Fixed** - for any bug fixes
  - **Security** - in case of vulnerabilities

### 1.2 Update CLAUDE.local.md
- [ ] Add entry to the CHANGELOG section with:
  - Date (YYYY-MM-DD format)
  - Description of change/fix
  - Impact assessment
  - Files modified
  - Test coverage added

### 1.3 Update Related Documentation
- [ ] Update API documentation if MCP tools changed
- [ ] Update troubleshooting guides if fixing known issues
- [ ] Update architecture docs if system changes made

## 2. Test Impact Analysis

### 2.1 Identify Affected Components
- [ ] Review all files modified by the change
- [ ] Identify dependent modules and components
- [ ] Check for integration points that might be affected
- [ ] Review related MCP tools and their usage

### 2.2 Find Related Tests
```bash
# Search for existing tests related to the change
find . -name "test_*.py" -exec grep -l "keyword_from_change" {} \;
rg "test.*function_name" --type py
```

### 2.3 Update/Create Tests
- [ ] Update existing unit tests for modified functions
- [ ] Add new unit tests for new functionality
- [ ] Update integration tests if system behavior changed
- [ ] Add regression tests to prevent the fixed bug from recurring

## 3. Validation Testing

### 3.1 Run Test Suite
```bash

# Run specific test category
pytest tests/unit/
% pytest tests/integration/

```

### 3.2 Validate Fix
- [ ] Verify the original issue is resolved
- [ ] Test edge cases and boundary conditions
- [ ] Ensure no regressions introduced
- [ ] Validate error handling improvements

### 3.3 Performance Testing (if applicable)
- [ ] Run performance benchmarks
- [ ] Check memory usage patterns
- [ ] Validate response times within acceptable limits

### 3.4 Add issue know content `ai_docs/issues/` if this is a fix probleme

% ## 4. Integration Verification

% ### 4.1 MCP Tool Testing
- [ ] Test affected MCP tools individually
- [ ] Verify tool parameter validation
- [ ] Check error responses and handling
- [ ] Test with realistic data scenarios

### 4.2 System Integration
- [ ] Test Docker container functionality
- [ ] Verify database connectivity and operations
- [ ] Check API endpoints if modified
- [ ] Validate frontend integration if applicable

## 5. Code Quality Checks

### 5.1 Linting and Formatting
```bash
# Run linting
flake8 src/
black --check src/
isort --check-only src/

# Auto-format if needed
black src/
isort src/
```

### 5.2 Type Checking
```bash
mypy src/
```

## 6. Final Review

### 6.1 Code Review Checklist
- [ ] Code follows project conventions
- [ ] All functions have proper docstrings
- [ ] Error handling is comprehensive
- [ ] Logging is appropriate and informative
- [ ] No debugging code left in production

### 6.2 Documentation Review
- [ ] All documentation updates are accurate
- [ ] Examples reflect current functionality
- [ ] API documentation matches implementation
- [ ] User-facing documentation updated if needed

## 7. Deployment Preparation

### 7.1 Version Management
- [ ] Update version numbers if applicable
- [ ] Tag release if this is a version release
- [ ] Update Docker image version if needed

### 7.2 Deployment Notes
- [ ] Document any migration steps required
- [ ] Note any configuration changes needed
- [ ] Identify any backward compatibility concerns

## Example Workflow

```bash
# 1. After implementing fix, update changelog
vim CHANGELOG.md
vim CLAUDE.local.md

# 2. Find and update related tests
rg "function_name" --type py tests/
vim tests/test_related_functionality.py

# 3. Run comprehensive test suite
pytest --cov=src tests/ -v

# 4. Validate MCP tools if affected
python -c "from fastmcp.mcp_tools import tool_name; print('Tool loads successfully')"

# 5. Run quality checks
black src/ && isort src/ && flake8 src/ && mypy src/

# 6. Final validation
echo "All checks passed - ready for commit"
```

## Notes

- Always follow this checklist systematically to ensure quality and reliability
- Document any deviations from this process and the rationale
- Consider the impact scope when determining which steps are necessary
- When in doubt, err on the side of more comprehensive testing and documentation