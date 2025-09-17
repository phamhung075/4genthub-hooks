# Claude Hooks System Test Suite

This directory contains comprehensive unit and integration tests for the Claude hooks system. The test suite ensures all hook functionality is properly tested and working.

## Test Structure

```
tests/
├── conftest.py              # Shared test configuration and fixtures
├── pytest.ini              # Pytest configuration
├── requirements-test.txt    # Testing dependencies
├── run_tests.py            # Test runner script
├── README.md               # This documentation
├── unit/                   # Unit tests for individual components
├── integration/            # Integration tests for component interactions
├── fixtures/               # Test fixtures and sample data
└── utils/                  # Test utilities and helpers
```

## Quick Start

### 1. Install Dependencies

```bash
# Install testing dependencies
pip install -r requirements-test.txt

# Or install from main project (includes test deps)
cd ../../../agenthub_main
pip install -e ".[dev]"
```

### 2. Run Tests

```bash
# Quick test run (unit tests only)
python run_tests.py --quick

# Run all tests with coverage
python run_tests.py --coverage

# Run specific test categories
python run_tests.py --unit
python run_tests.py --integration

# Verbose output
python run_tests.py --verbose

# Parallel execution
python run_tests.py --parallel
```

### 3. Check Dependencies

```bash
python run_tests.py --check-deps
```

## Test Categories

### Unit Tests (`tests/unit/`)
- Test individual hook components in isolation
- Mock external dependencies (MCP server, file system)
- Fast execution (< 0.1s per test)
- No external dependencies required

### Integration Tests (`tests/integration/`)
- Test component interactions
- May require local MCP server or mock services
- Test realistic workflows and data flows

## Test Markers

The test suite uses pytest markers to categorize tests:

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.slow` - Tests taking > 1 second
- `@pytest.mark.fast` - Tests completing in < 0.1 seconds
- `@pytest.mark.hooks` - Hook system specific tests
- `@pytest.mark.mcp` - MCP integration tests
- `@pytest.mark.filesystem` - File system operation tests
- `@pytest.mark.network` - Tests requiring network access
- `@pytest.mark.auth` - Authentication/authorization tests

## Running Specific Tests

```bash
# Run only fast unit tests
pytest -m "unit and fast"

# Run MCP integration tests
pytest -m "mcp and integration"

# Run all except slow tests
pytest -m "not slow"

# Run specific test file
pytest unit/test_session_start.py

# Run specific test function
pytest unit/test_session_start.py::test_hook_initialization
```

## Coverage Requirements

The test suite enforces minimum code coverage requirements:

- **Overall Coverage**: 80% minimum
- **Critical Paths**: 90% minimum
- **New Code**: 95% minimum

Coverage reports are generated in multiple formats:

- **Terminal**: Immediate feedback during test runs
- **HTML**: Detailed coverage report (`htmlcov/index.html`)
- **XML**: For CI/CD integration (`coverage.xml`)

## Writing Tests

### Test File Naming
- Unit tests: `test_<module_name>.py`
- Integration tests: `test_integration_<feature>.py`
- Place in appropriate directory (`unit/` or `integration/`)

### Test Function Naming
- Use descriptive names: `test_hook_handles_missing_token_gracefully`
- Follow pattern: `test_<component>_<action>_<expected_outcome>`

### Using Fixtures
```python
def test_hook_with_mcp_client(mock_mcp_client, sample_hook_context):
    # Test uses fixtures from conftest.py
    pass

def test_file_operations(mock_file_system):
    # Test uses mock file system
    pass
```

### Mock Guidelines
- Mock external dependencies (MCP server, file system, network)
- Use realistic test data from `fixtures/sample_data.py`
- Test both success and failure scenarios
- Verify mock interactions when needed

### Test Example
```python
import pytest
from unittest.mock import patch, Mock
from utils.test_helpers import create_mock_hook_context

@pytest.mark.unit
@pytest.mark.hooks
def test_session_start_hook_initializes_correctly(mock_env_vars, mock_mcp_client):
    """Test that session_start hook initializes with proper configuration."""
    from session_start import main

    context = create_mock_hook_context(
        user_id="test_user",
        session_id="test_session"
    )

    with patch('utils.mcp_client.MCPClient', return_value=mock_mcp_client):
        result = main(context)

    assert result['success'] is True
    assert 'session_id' in result
    mock_mcp_client.post.assert_called_once()
```

## Debugging Tests

### Failed Test Investigation
```bash
# Run with detailed output
pytest --tb=long -v

# Run single failing test with debugging
pytest -s --tb=long unit/test_session_start.py::test_failing_function

# Use pdb for interactive debugging
pytest --pdb unit/test_session_start.py::test_failing_function
```

### Logging During Tests
```python
import logging

def test_with_logging(caplog):
    with caplog.at_level(logging.DEBUG):
        # Your test code here
        pass

    assert "Expected log message" in caplog.text
```

## Performance Guidelines

### Test Speed
- Unit tests should complete in < 0.1 seconds
- Integration tests should complete in < 1 second
- Mark slow tests with `@pytest.mark.slow`

### Resource Usage
- Clean up test artifacts (temp files, mock objects)
- Use fixtures for expensive setup operations
- Prefer mocking over real external services

## CI/CD Integration

### GitHub Actions Example
```yaml
- name: Run Hook Tests
  run: |
    cd .claude/hooks/tests
    python run_tests.py --coverage --parallel

- name: Upload Coverage
  uses: codecov/codecov-action@v3
  with:
    file: .claude/hooks/tests/coverage.xml
```

### Local Pre-commit
```bash
# Run before committing changes
cd .claude/hooks/tests
python run_tests.py --quick --lint
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Ensure hooks directory is in Python path
   export PYTHONPATH="${PYTHONPATH}:/path/to/.claude/hooks"
   ```

2. **Missing Dependencies**
   ```bash
   # Install test dependencies
   pip install -r requirements-test.txt
   ```

3. **Permission Errors**
   ```bash
   # Make test runner executable
   chmod +x run_tests.py
   ```

4. **Coverage Too Low**
   ```bash
   # Generate detailed coverage report
   python run_tests.py --coverage
   # Open htmlcov/index.html to see uncovered lines
   ```

### Test Data Issues
- Verify sample data in `fixtures/sample_data.py`
- Check mock configurations in `conftest.py`
- Ensure test helpers are imported correctly

### Environment Issues
- Check environment variables in test configuration
- Verify mock environments match expected values
- Test with both development and testing configurations

## Contributing

When adding new hook functionality:

1. **Write tests first** (TDD approach)
2. **Ensure 80%+ coverage** for new code
3. **Add appropriate markers** for test categorization
4. **Update fixtures** if adding new data types
5. **Document complex test scenarios**

### Test Review Checklist
- [ ] Tests cover both success and failure cases
- [ ] External dependencies are properly mocked
- [ ] Test names are descriptive and clear
- [ ] Appropriate markers are applied
- [ ] Test data is realistic and representative
- [ ] Performance requirements are met
- [ ] Documentation is updated if needed

## Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [Python unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
- [Testing Best Practices](https://docs.python-guide.org/writing/tests/)

---

For questions or issues with the test suite, please check the existing test implementations and documentation, or create an issue in the project repository.