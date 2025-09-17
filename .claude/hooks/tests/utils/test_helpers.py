"""
Test helper functions and utilities for Claude hooks testing.

This module provides common utilities, mock creators, and helper functions
used across different test modules.
"""

import os
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from typing import Dict, Any, Optional, List
import uuid


class MockMCPClient:
    """Mock MCP client for testing hook interactions."""

    def __init__(self):
        self.responses = {}
        self.call_log = []
        self.is_authenticated = True

    def post(self, endpoint: str, **kwargs) -> Mock:
        """Mock POST request."""
        self.call_log.append(('POST', endpoint, kwargs))
        response = Mock()
        response.status_code = 200
        response.json.return_value = self.responses.get(endpoint, {
            'success': True,
            'data': {'result': 'mock_response'}
        })
        return response

    def get(self, endpoint: str, **kwargs) -> Mock:
        """Mock GET request."""
        self.call_log.append(('GET', endpoint, kwargs))
        response = Mock()
        response.status_code = 200
        response.json.return_value = self.responses.get(endpoint, {
            'success': True,
            'data': {'result': 'mock_response'}
        })
        return response

    def set_response(self, endpoint: str, response_data: Dict[str, Any]):
        """Set mock response for specific endpoint."""
        self.responses[endpoint] = response_data

    def get_calls(self, method: Optional[str] = None) -> List:
        """Get logged calls, optionally filtered by method."""
        if method:
            return [call for call in self.call_log if call[0] == method]
        return self.call_log

    def clear_log(self):
        """Clear call log."""
        self.call_log = []


class MockFileSystem:
    """Mock file system for testing file operations."""

    def __init__(self, temp_dir: Path):
        self.temp_dir = temp_dir
        self.files = {}
        self.directories = set()

    def create_file(self, path: str, content: str = ""):
        """Create a mock file with content."""
        full_path = self.temp_dir / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content)
        self.files[path] = content
        return full_path

    def create_directory(self, path: str):
        """Create a mock directory."""
        full_path = self.temp_dir / path
        full_path.mkdir(parents=True, exist_ok=True)
        self.directories.add(path)
        return full_path

    def create_json_file(self, path: str, data: Dict[str, Any]):
        """Create a JSON file with data."""
        content = json.dumps(data, indent=2)
        return self.create_file(path, content)

    def get_path(self, path: str) -> Path:
        """Get full path for relative path."""
        return self.temp_dir / path

    def file_exists(self, path: str) -> bool:
        """Check if file exists."""
        return (self.temp_dir / path).exists()


def create_mock_hook_context(
    user_id: str = "test_user",
    session_id: str = "test_session",
    tool_name: str = "test_tool",
    **kwargs
) -> Dict[str, Any]:
    """Create a mock hook context for testing."""
    context = {
        'user_id': user_id,
        'session_id': session_id,
        'tool_name': tool_name,
        'tool_params': kwargs.get('tool_params', {}),
        'working_directory': kwargs.get('working_directory', '/tmp/test'),
        'timestamp': kwargs.get('timestamp', '2025-09-16T16:00:00Z'),
        'message_id': kwargs.get('message_id', str(uuid.uuid4())),
        'conversation_id': kwargs.get('conversation_id', str(uuid.uuid4()))
    }
    context.update(kwargs)
    return context


def create_mock_task_data(
    task_id: str = None,
    title: str = "Test Task",
    status: str = "todo",
    **kwargs
) -> Dict[str, Any]:
    """Create mock task data for testing."""
    if task_id is None:
        task_id = str(uuid.uuid4())

    task_data = {
        'id': task_id,
        'title': title,
        'description': kwargs.get('description', 'Test task description'),
        'status': status,
        'priority': kwargs.get('priority', 'medium'),
        'assignees': kwargs.get('assignees', ['test-agent']),
        'created_at': kwargs.get('created_at', '2025-09-16T16:00:00Z'),
        'updated_at': kwargs.get('updated_at', '2025-09-16T16:00:00Z')
    }
    task_data.update(kwargs)
    return task_data


def create_mock_env_vars(**custom_vars) -> Dict[str, str]:
    """Create mock environment variables for testing."""
    env_vars = {
        'AI_DATA': '/tmp/test_ai_data',
        'AI_DOCS': '/tmp/test_ai_docs',
        'FASTMCP_TEST_MODE': '1',
        'MCP_SERVER_URL': 'http://localhost:8000',
        'USER_ID': 'test_user_123',
        'HOME': '/tmp/test_home',
        'PYTHONPATH': '/tmp/test_hooks'
    }
    env_vars.update(custom_vars)
    return env_vars


def patch_mcp_client():
    """Decorator to patch MCP client in tests."""
    def decorator(test_func):
        def wrapper(*args, **kwargs):
            mock_client = MockMCPClient()
            with patch('utils.mcp_client.MCPClient', return_value=mock_client):
                return test_func(*args, mock_client=mock_client, **kwargs)
        return wrapper
    return decorator


def patch_file_operations():
    """Decorator to patch file operations in tests."""
    def decorator(test_func):
        def wrapper(*args, **kwargs):
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                mock_fs = MockFileSystem(temp_path)

                with patch('os.getcwd', return_value=str(temp_path)), \
                     patch('pathlib.Path.home', return_value=temp_path):
                    return test_func(*args, mock_fs=mock_fs, **kwargs)
        return wrapper
    return decorator


def assert_mcp_call_made(mock_client: MockMCPClient, method: str, endpoint: str):
    """Assert that a specific MCP call was made."""
    calls = mock_client.get_calls(method)
    endpoints = [call[1] for call in calls]
    assert endpoint in endpoints, f"Expected call to {method} {endpoint}, but got: {endpoints}"


def assert_file_created(mock_fs: MockFileSystem, file_path: str):
    """Assert that a file was created."""
    assert mock_fs.file_exists(file_path), f"Expected file {file_path} to be created"


def assert_file_contains(file_path: Path, expected_content: str):
    """Assert that a file contains expected content."""
    assert file_path.exists(), f"File {file_path} does not exist"
    content = file_path.read_text()
    assert expected_content in content, f"Expected '{expected_content}' in file content: {content[:200]}..."


class TestDataGenerator:
    """Generate various types of test data."""

    @staticmethod
    def generate_hook_execution_data(count: int = 5) -> List[Dict[str, Any]]:
        """Generate multiple hook execution contexts."""
        return [
            create_mock_hook_context(
                user_id=f"user_{i}",
                session_id=f"session_{i}",
                tool_name=f"tool_{i % 3}"
            )
            for i in range(count)
        ]

    @staticmethod
    def generate_task_hierarchy(parent_count: int = 2, subtask_count: int = 3) -> Dict[str, Any]:
        """Generate a hierarchy of tasks and subtasks."""
        tasks = {}

        for i in range(parent_count):
            parent_id = str(uuid.uuid4())
            parent_task = create_mock_task_data(
                task_id=parent_id,
                title=f"Parent Task {i+1}",
                status="in_progress"
            )

            subtasks = []
            for j in range(subtask_count):
                subtask = create_mock_task_data(
                    title=f"Subtask {j+1} of Parent {i+1}",
                    status="todo"
                )
                subtasks.append(subtask)

            parent_task['subtasks'] = subtasks
            tasks[parent_id] = parent_task

        return tasks


# Error simulation utilities
class SimulatedError:
    """Simulate various types of errors for testing."""

    @staticmethod
    def network_error():
        """Simulate network connectivity error."""
        from requests.exceptions import ConnectionError
        raise ConnectionError("Simulated network error")

    @staticmethod
    def authentication_error():
        """Simulate authentication failure."""
        response = Mock()
        response.status_code = 401
        response.json.return_value = {"error": "Authentication failed"}
        return response

    @staticmethod
    def server_error():
        """Simulate server error."""
        response = Mock()
        response.status_code = 500
        response.json.return_value = {"error": "Internal server error"}
        return response

    @staticmethod
    def file_permission_error():
        """Simulate file permission error."""
        raise PermissionError("Simulated permission denied")


# Validation utilities
def validate_hook_response(response: Dict[str, Any]) -> bool:
    """Validate standard hook response format."""
    required_fields = ['success', 'message']
    return all(field in response for field in required_fields)


def validate_mcp_request(request_data: Dict[str, Any]) -> bool:
    """Validate MCP request format."""
    required_fields = ['action']
    return all(field in request_data for field in required_fields)


# Logging utilities for tests
def capture_log_output():
    """Context manager to capture log output during tests."""
    import logging
    from io import StringIO

    log_capture = StringIO()
    handler = logging.StreamHandler(log_capture)
    logger = logging.getLogger()
    logger.addHandler(handler)

    try:
        yield log_capture
    finally:
        logger.removeHandler(handler)