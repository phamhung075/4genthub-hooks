# Continue Unit Test Fix - Command File

## Objective
Continue fixing and creating unit tests for the agenthub project backend, focusing on domain, application, and infrastructure layers.

## Current Focus
- Fix failing unit tests in the backend
- Create missing unit tests for uncovered code
- Ensure all tests follow DDD patterns
- Update TEST-CHANGELOG.md with changes

## Test Categories
- Unit tests: `agenthub_main/src/tests/unit/`
- Integration tests: `agenthub_main/src/tests/integration/`
- E2E tests: `agenthub_main/src/tests/e2e/`
- Performance tests: `agenthub_main/src/tests/performance/`

## Priority Areas
1. Domain layer entities and value objects
2. Application layer services and use cases
3. Infrastructure layer repositories
4. MCP interface controllers

## Test Execution Commands
```bash
# Run all unit tests
cd agenthub_main
python -m pytest src/tests/unit/ -v

# Run specific test file
python -m pytest src/tests/unit/domain/test_entities.py -v

# Run with coverage
python -m pytest src/tests/unit/ --cov=src --cov-report=html
```

## Rules
1. Write tests in correct location (`agenthub_main/src/tests/`)
2. Follow existing test patterns and conventions
3. Use mocks for external dependencies
4. Ensure tests are isolated and repeatable
5. Update TEST-CHANGELOG.md for all test changes
6. Follow DDD patterns in test structure

## Current Issues to Fix
- Check for failing tests in CI/CD pipeline
- Identify untested critical paths
- Fix test isolation issues
- Update deprecated test assertions
- Add missing test fixtures

## Success Criteria
- All unit tests pass
- Code coverage > 80%
- Tests follow DDD patterns
- TEST-CHANGELOG.md updated
- No test warnings or deprecations