"""
Sample data and fixtures for Claude hooks testing.

This module contains realistic sample data that mirrors actual hook system usage.
"""

import json
from typing import Dict, Any, List

# Sample MCP authentication tokens
SAMPLE_MCP_TOKENS = {
    "valid_token": {
        "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.test_payload.signature",
        "expires_at": "2025-12-31T23:59:59Z",
        "user_id": "user_123",
        "permissions": ["read", "write", "admin"]
    },
    "expired_token": {
        "token": "expired_token_example",
        "expires_at": "2024-01-01T00:00:00Z",
        "user_id": "user_123",
        "permissions": ["read"]
    }
}

# Sample environment configurations
SAMPLE_ENV_CONFIGS = {
    "development": {
        "AI_DATA": "/tmp/dev_ai_data",
        "AI_DOCS": "/tmp/dev_ai_docs",
        "MCP_SERVER_URL": "http://localhost:8000",
        "FASTMCP_TEST_MODE": "0",
        "LOG_LEVEL": "DEBUG"
    },
    "testing": {
        "AI_DATA": "/tmp/test_ai_data",
        "AI_DOCS": "/tmp/test_ai_docs",
        "MCP_SERVER_URL": "http://localhost:8000",
        "FASTMCP_TEST_MODE": "1",
        "LOG_LEVEL": "WARNING"
    },
    "production": {
        "AI_DATA": "/data/ai_data",
        "AI_DOCS": "/data/ai_docs",
        "MCP_SERVER_URL": "https://api.example.com",
        "FASTMCP_TEST_MODE": "0",
        "LOG_LEVEL": "ERROR"
    }
}

# Sample hook execution contexts
SAMPLE_HOOK_CONTEXTS = {
    "session_start": {
        "user_id": "user_123",
        "session_id": "session_456",
        "timestamp": "2025-09-16T16:00:00Z",
        "project_path": "/home/user/project",
        "claude_version": "claude-3-opus-20240229"
    },
    "pre_tool_use": {
        "user_id": "user_123",
        "session_id": "session_456",
        "tool_name": "Edit",
        "tool_params": {
            "file_path": "/home/user/project/src/main.py",
            "old_string": "def old_function():",
            "new_string": "def new_function():"
        },
        "timestamp": "2025-09-16T16:01:00Z"
    },
    "post_tool_use": {
        "user_id": "user_123",
        "session_id": "session_456",
        "tool_name": "Edit",
        "tool_result": {
            "success": True,
            "message": "File edited successfully"
        },
        "timestamp": "2025-09-16T16:01:30Z"
    }
}

# Sample MCP task data
SAMPLE_TASK_DATA = {
    "simple_task": {
        "id": "task_123",
        "title": "Fix authentication bug",
        "description": "Resolve issue with JWT token validation",
        "status": "todo",
        "priority": "high",
        "assignees": ["debugger-agent"],
        "created_at": "2025-09-16T16:00:00Z",
        "updated_at": "2025-09-16T16:00:00Z"
    },
    "complex_task": {
        "id": "task_456",
        "title": "Implement user dashboard",
        "description": "Create comprehensive user dashboard with analytics",
        "status": "in_progress",
        "priority": "medium",
        "assignees": ["coding-agent", "ui-specialist-agent"],
        "details": "Multi-component dashboard with real-time data",
        "estimated_effort": "1 week",
        "subtasks": [
            {
                "id": "subtask_1",
                "title": "Design dashboard layout",
                "status": "completed",
                "assignees": ["ui-specialist-agent"]
            },
            {
                "id": "subtask_2",
                "title": "Implement data fetching",
                "status": "in_progress",
                "assignees": ["coding-agent"]
            },
            {
                "id": "subtask_3",
                "title": "Add analytics widgets",
                "status": "todo",
                "assignees": ["coding-agent"]
            }
        ],
        "created_at": "2025-09-15T10:00:00Z",
        "updated_at": "2025-09-16T14:30:00Z"
    }
}

# Sample agent state data
SAMPLE_AGENT_STATES = {
    "master_orchestrator": {
        "agent_id": "master-orchestrator-agent",
        "status": "active",
        "current_task": "task_456",
        "session_id": "session_456",
        "capabilities": ["task_coordination", "agent_delegation"],
        "load_time": "2025-09-16T16:00:00Z"
    },
    "coding_agent": {
        "agent_id": "coding-agent",
        "status": "busy",
        "current_task": "subtask_2",
        "session_id": "session_456",
        "capabilities": ["code_implementation", "file_editing"],
        "load_time": "2025-09-16T16:01:00Z"
    }
}

# Sample context hierarchy data
SAMPLE_CONTEXT_HIERARCHY = {
    "global_context": {
        "level": "global",
        "user_id": "user_123",
        "preferences": {
            "coding_style": "python_pep8",
            "testing_framework": "pytest",
            "documentation_format": "markdown"
        },
        "active_projects": ["project_1", "project_2"]
    },
    "project_context": {
        "level": "project",
        "project_id": "project_1",
        "name": "AI Agent System",
        "tech_stack": ["python", "fastapi", "postgresql"],
        "coding_standards": "pep8",
        "testing_requirements": "80% coverage"
    },
    "branch_context": {
        "level": "branch",
        "git_branch_id": "branch_456",
        "branch_name": "feature/authentication",
        "description": "Implement JWT authentication system",
        "assigned_agents": ["security-auditor-agent", "coding-agent"]
    },
    "task_context": {
        "level": "task",
        "task_id": "task_123",
        "current_focus": "JWT token validation",
        "files_involved": [
            "/src/auth/jwt_validator.py",
            "/tests/test_auth.py"
        ],
        "blockers": [],
        "progress_notes": "Implementing token expiry validation"
    }
}

# Sample file system protection data
SAMPLE_FILE_PROTECTION = {
    "allowed_root_files": [
        "README.md",
        "CHANGELOG.md",
        "TEST-CHANGELOG.md",
        "CLAUDE.md",
        "CLAUDE.local.md"
    ],
    "valid_test_paths": [
        "src/tests/",
        "agenthub_main/src/tests/",
        ".claude/hooks/tests/",
        "tests/"
    ],
    "protected_patterns": [
        ".env*",
        "*.key",
        "*.pem",
        "secrets.*"
    ]
}

# Sample documentation index data
SAMPLE_DOCS_INDEX = {
    "version": "1.0",
    "generated_at": "2025-09-16T16:00:00Z",
    "total_files": 25,
    "directories": {
        "api-integration": {"files": 3, "updated": "2025-09-15T10:00:00Z"},
        "authentication": {"files": 5, "updated": "2025-09-16T14:00:00Z"},
        "testing-qa": {"files": 4, "updated": "2025-09-16T16:00:00Z"}
    },
    "files": [
        {
            "path": "api-integration/mcp-endpoints.md",
            "size": 2048,
            "hash": "abc123",
            "updated": "2025-09-15T10:00:00Z"
        },
        {
            "path": "authentication/jwt-setup.md",
            "size": 1024,
            "hash": "def456",
            "updated": "2025-09-16T14:00:00Z"
        }
    ]
}

# Sample hint matrix data
SAMPLE_HINT_MATRIX = {
    "tool_hints": {
        "Edit": {
            "success": "File edited successfully",
            "tips": ["Use precise line numbers", "Test changes before committing"],
            "common_errors": ["File not found", "Permission denied"]
        },
        "Write": {
            "success": "File created successfully",
            "tips": ["Check directory exists", "Use appropriate file extension"],
            "common_errors": ["Directory not found", "File already exists"]
        }
    },
    "context_hints": {
        "task_creation": {
            "description": "Creating new MCP task",
            "best_practices": ["Include detailed context", "Assign appropriate agents"],
            "examples": ["task_id: abc123", "assignees: coding-agent"]
        }
    }
}

# Sample session tracking data
SAMPLE_SESSION_DATA = {
    "active_session": {
        "session_id": "session_456",
        "user_id": "user_123",
        "start_time": "2025-09-16T16:00:00Z",
        "last_activity": "2025-09-16T16:15:00Z",
        "active_agents": ["master-orchestrator-agent"],
        "current_project": "project_1",
        "task_stack": ["task_456", "task_123"]
    },
    "completed_session": {
        "session_id": "session_123",
        "user_id": "user_123",
        "start_time": "2025-09-15T14:00:00Z",
        "end_time": "2025-09-15T16:30:00Z",
        "duration": "2h 30m",
        "tasks_completed": 3,
        "agents_used": ["coding-agent", "test-orchestrator-agent"]
    }
}

# Sample error scenarios for testing
SAMPLE_ERROR_SCENARIOS = {
    "network_failure": {
        "error_type": "ConnectionError",
        "message": "Failed to connect to MCP server",
        "retry_count": 3,
        "timestamp": "2025-09-16T16:00:00Z"
    },
    "authentication_failure": {
        "error_type": "AuthenticationError",
        "message": "Invalid or expired token",
        "status_code": 401,
        "timestamp": "2025-09-16T16:01:00Z"
    },
    "file_permission_error": {
        "error_type": "PermissionError",
        "message": "Permission denied accessing /protected/file.txt",
        "file_path": "/protected/file.txt",
        "timestamp": "2025-09-16T16:02:00Z"
    }
}


def get_sample_data(category: str, item: str = None) -> Any:
    """Get sample data by category and optional item name."""
    categories = {
        "tokens": SAMPLE_MCP_TOKENS,
        "env": SAMPLE_ENV_CONFIGS,
        "contexts": SAMPLE_HOOK_CONTEXTS,
        "tasks": SAMPLE_TASK_DATA,
        "agents": SAMPLE_AGENT_STATES,
        "hierarchy": SAMPLE_CONTEXT_HIERARCHY,
        "protection": SAMPLE_FILE_PROTECTION,
        "docs": SAMPLE_DOCS_INDEX,
        "hints": SAMPLE_HINT_MATRIX,
        "sessions": SAMPLE_SESSION_DATA,
        "errors": SAMPLE_ERROR_SCENARIOS
    }

    if category not in categories:
        raise ValueError(f"Unknown category: {category}")

    if item is None:
        return categories[category]
    else:
        if item not in categories[category]:
            raise ValueError(f"Unknown item '{item}' in category '{category}'")
        return categories[category][item]


def create_sample_json_file(file_path: str, category: str, item: str = None):
    """Create a JSON file with sample data."""
    data = get_sample_data(category, item)
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)
    return file_path