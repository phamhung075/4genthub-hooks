"""
DEPRECATED: Legacy messages configuration for Claude hooks.
This file is now a backwards compatibility wrapper.

USE utils.config_factory instead for all new code.
"""

from typing import Dict, Any
import warnings

# Import from new ConfigFactory for backwards compatibility
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'utils'))
from config_factory import get_error_message as _get_error_message, get_warning_message as _get_warning_message, get_info_message as _get_info_message

# Issue deprecation warning
warnings.warn(
    "config.messages is deprecated. Use utils.config_factory instead.",
    DeprecationWarning,
    stacklevel=2
)

# Legacy error messages for backwards compatibility
ERROR_MESSAGES = {
    # File system protection errors
    "claude_edit_disabled": {
        "message": "BLOCKED: Editing .claude files is disabled",
        "hint": "Set ENABLE_CLAUDE_EDIT=true in .env.claude to allow editing"
    },
    "env_file_subfolder": {
        "message": "BLOCKED: .env* files must be created in project root only",
        "hint": "Place environment files in the project root directory"
    },
    "env_file_access": {
        "message": "BLOCKED: Access to .env* files containing sensitive data is prohibited",
        "hint": "Use .env.sample for template files instead"
    },
    "root_file_creation": {
        "message": "BLOCKED: Creating files in project root is restricted",
        "hint": "Place files in appropriate subdirectories (e.g., ai_docs/, src/, tests/)"
    },
    "root_folder_creation": {
        "message": "BLOCKED: Creating folders in project root is not allowed",
        "hint": "All necessary project folders should already exist"
    },
    "unique_root_file": {
        "message": "BLOCKED: {file} can only exist in project root",
        "hint": "This file already exists in root. Edit the existing file instead of creating a duplicate"
    },
    "subfolder_ai_docs": {
        "message": "BLOCKED: 'ai_docs' folder can only exist in project root",
        "hint": "Use the existing ai_docs folder in the project root for documentation"
    },
    "docs_folder": {
        "message": "BLOCKED: Creating 'docs' folders is prohibited",
        "hint": "Use 'ai_docs' folder in project root for all documentation"
    },
    "md_not_in_ai_docs": {
        "message": "BLOCKED: ALL .md files must be in ai_docs folder",
        "hint": "Place documentation in ai_docs/{category}/*.md",
        "examples": ["ai_docs/api-integration/auth.md", "ai_docs/troubleshooting-guides/setup-issues.md"]
    },
    "invalid_ai_docs_folder": {
        "message": "BLOCKED: Invalid folder name in ai_docs",
        "hint": "Folder names in ai_docs must use kebab-case (lowercase-with-dashes)",
        "valid_examples": ["api-integration", "test-results", "setup-guides"],
        "invalid_examples": ["API_Integration", "Test Results", "SetupGuides"]
    },
    "test_wrong_location": {
        "message": "BLOCKED: Test files must be in designated test directories",
        "hint": "Place test files in approved test directories",
        "valid_paths": ["agenthub_main/src/tests", "agenthub-frontend/src/tests"]
    },
    "venv_wrong_location": {
        "message": "BLOCKED: Virtual environment must be in agenthub_main/.venv",
        "hint": "Create .venv only at: agenthub_main/.venv"
    },
    "logs_not_in_root": {
        "message": "BLOCKED: 'logs' folder can only exist in project root",
        "hint": "Use the logs folder in project root for all log files"
    },
    "sh_not_in_scripts": {
        "message": "BLOCKED: Shell scripts must be in scripts/ or docker-system/ folders",
        "hint": "Place .sh files in scripts/ or docker-system/ folders"
    },
    "dangerous_rm": {
        "message": "BLOCKED: Dangerous rm -rf command detected",
        "hint": "This command could delete critical system files. Use specific paths and verify before deletion"
    },
    "documentation_required": {
        "message": "BLOCKED: Documentation update required",
        "hint": "This {type} has existing documentation that must be updated before modification",
        "action": "Update documentation at: {doc_path}"
    }
}

# Warning messages
WARNING_MESSAGES = {
    "context_switch_failed": "Warning: Agent context switch failed: {error}",
    "documentation_needed": "📝 Documentation needed: Please {action} {doc_path} for file: {file_path}",
    "hint_display_error": "Warning: Failed to display hints: {error}",
    "context_injection_error": "Warning: Failed to inject context: {error}",
    "session_tracking_error": "Warning: Session tracking error: {error}"
}

# Info messages
INFO_MESSAGES = {
    "role_violation": "Tool '{tool}' is not available for agent '{agent}'",
    "available_tools": "Available tools: {tools}",
    "solution": "Solution: {solution}",
    "documentation_updated": "✅ Documentation successfully updated",
    "session_started": "Session {session_id} started",
    "context_injected": "Context injected for {tool}: {size} bytes"
}

# System prompts and instructions
SYSTEM_PROMPTS = {
    "documentation_reminder": """
The file you're modifying has existing documentation that should be kept in sync.
Please ensure the documentation accurately reflects your changes.
Documentation location: {doc_path}
""",
    "role_enforcement": """
You are currently operating as {agent_type}.
Your available tools are restricted to: {tools}
Please use only the tools appropriate for your role.
""",
    "context_injection": """
Relevant context has been loaded for your current operation.
Context type: {context_type}
Context size: {context_size} bytes
"""
}

# Backwards compatibility functions using ConfigFactory
def get_error_message(error_key: str, **kwargs) -> str:
    """
    DEPRECATED: Get a formatted error message. Use utils.config_factory instead.
    """
    return _get_error_message(error_key, **kwargs)

def get_warning_message(warning_key: str, **kwargs) -> str:
    """
    DEPRECATED: Get a formatted warning message. Use utils.config_factory instead.
    """
    return _get_warning_message(warning_key, **kwargs)

def get_info_message(info_key: str, **kwargs) -> str:
    """
    DEPRECATED: Get a formatted info message. Use utils.config_factory instead.
    """
    return _get_info_message(info_key, **kwargs)

def get_system_prompt(prompt_key: str, **kwargs) -> str:
    """
    DEPRECATED: Get a system prompt. Use utils.config_factory instead.
    """
    # For backwards compatibility, try to get from ConfigFactory
    try:
        from config_factory import get_config_factory
        factory = get_config_factory()
        return factory.format_message('info', prompt_key, **kwargs)
    except:
        # Fallback to legacy behavior
        if prompt_key not in SYSTEM_PROMPTS:
            return f"Unknown prompt: {prompt_key}"
        prompt = SYSTEM_PROMPTS[prompt_key]
        return prompt.format(**kwargs) if kwargs else prompt