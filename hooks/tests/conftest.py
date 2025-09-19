"""
Pytest configuration and shared fixtures for Claude hooks tests.

This module provides common test fixtures, mock objects, and configuration
for testing the hooks system components.
"""

import os
import sys
import tempfile
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import json

# Add the hooks directory to Python path for imports
hooks_dir = Path(__file__).parent.parent
sys.path.insert(0, str(hooks_dir))


@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing."""
    with patch.dict(os.environ, {
        'AI_DATA': '/tmp/test_ai_data',
        'AI_DOCS': '/tmp/test_ai_docs',
        'FASTMCP_TEST_MODE': '1',
        'MCP_SERVER_URL': 'http://localhost:8000',
        'USER_ID': 'test_user_123',
        'HOME': '/tmp/test_home'
    }):
        yield


@pytest.fixture
def temp_directory():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def mock_mcp_token():
    """Mock MCP authentication token."""
    return {
        'token': 'test_token_123',
        'expires_at': '2025-12-31T23:59:59Z',
        'user_id': 'test_user_123'
    }


@pytest.fixture
def mock_mcp_client():
    """Mock MCP client for testing."""
    client = Mock()
    client.post.return_value.status_code = 200
    client.post.return_value.json.return_value = {
        'success': True,
        'data': {'result': 'test_response'}
    }
    client.get.return_value.status_code = 200
    client.get.return_value.json.return_value = {
        'success': True,
        'data': {'result': 'test_response'}
    }
    return client


@pytest.fixture
def mock_claude_message():
    """Mock Claude message structure for testing."""
    return {
        'type': 'text',
        'text': 'Test message content',
        'tool_calls': [],
        'assistant_id': 'claude-3-opus-20240229'
    }


@pytest.fixture
def mock_file_system(temp_directory):
    """Mock file system structure for testing."""
    # Create basic directory structure
    (temp_directory / 'ai_docs').mkdir()
    (temp_directory / 'logs').mkdir()
    (temp_directory / '.claude').mkdir()
    (temp_directory / '.claude' / 'hooks').mkdir()

    # Create mock config files
    (temp_directory / '.mcp.json').write_text(json.dumps({
        'token': 'test_token',
        'server_url': 'http://localhost:8000'
    }))

    (temp_directory / '.env').write_text('TEST_VAR=test_value\n')

    return temp_directory


@pytest.fixture
def mock_git_repo(temp_directory):
    """Mock git repository for testing."""
    git_dir = temp_directory / '.git'
    git_dir.mkdir()
    (git_dir / 'config').write_text('[core]\nrepositoryformatversion = 0\n')
    return temp_directory


@pytest.fixture
def sample_hook_context():
    """Sample hook context data for testing."""
    return {
        'user_id': 'test_user_123',
        'session_id': 'session_456',
        'tool_name': 'test_tool',
        'tool_params': {'param1': 'value1'},
        'working_directory': '/tmp/test_workspace',
        'timestamp': '2025-09-16T16:00:00Z'
    }


@pytest.fixture
def mock_session_data():
    """Mock session tracking data."""
    return {
        'session_id': 'test_session_123',
        'start_time': '2025-09-16T16:00:00Z',
        'user_id': 'test_user_123',
        'project_id': 'test_project_456',
        'active_tasks': [],
        'context_stack': []
    }


@pytest.fixture
def mock_task_data():
    """Mock task data for testing."""
    return {
        'id': 'task_123',
        'title': 'Test Task',
        'description': 'Test task description',
        'status': 'todo',
        'assignees': ['test-agent'],
        'created_at': '2025-09-16T16:00:00Z'
    }


@pytest.fixture(autouse=True)
def setup_test_logging():
    """Setup test-specific logging configuration."""
    import logging
    logging.getLogger().setLevel(logging.WARNING)  # Reduce log noise in tests


@pytest.fixture
def mock_requests():
    """Mock HTTP requests for testing external API calls."""
    with patch('requests.post') as mock_post, \
         patch('requests.get') as mock_get, \
         patch('httpx.post') as mock_httpx_post, \
         patch('httpx.get') as mock_httpx_get:

        # Setup default responses
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'success': True, 'data': {}}

        mock_post.return_value = mock_response
        mock_get.return_value = mock_response
        mock_httpx_post.return_value = mock_response
        mock_httpx_get.return_value = mock_response

        yield {
            'post': mock_post,
            'get': mock_get,
            'httpx_post': mock_httpx_post,
            'httpx_get': mock_httpx_get
        }


# Test markers for categorizing tests
pytestmark = [
    pytest.mark.unit,  # These are unit tests
    pytest.mark.hooks  # Custom marker for hooks tests
]