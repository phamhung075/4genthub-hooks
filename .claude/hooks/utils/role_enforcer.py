#!/usr/bin/env python3
"""
Role Enforcer for Tool Usage
Enforces role-based permissions for tool usage based on active agent
"""

import yaml
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import fnmatch
import sys

# Add parent directory to import messages
sys.path.insert(0, str(Path(__file__).parent.parent))
from .config_factory import get_info_message

# Import agent state manager
try:
    from .agent_state_manager import get_current_agent
except ImportError:
    get_current_agent = None


class RoleEnforcer:
    """Enforces role-based tool permissions."""

    def __init__(self, session_id: str = None):
        """Initialize role enforcer with session context."""
        self.session_id = session_id
        self.config_dir = Path(__file__).parent.parent / "config"
        self.role_config_file = self.config_dir / "__hint_message__active_role.yaml"

        # Load role configuration
        self.role_config = self._load_config(self.role_config_file)

        # Track violations
        self.violations = []

        # Cache current role
        self._current_role = None
        self._role_cache_time = None

    def _load_config(self, file_path: Path) -> Dict[str, Any]:
        """Load YAML configuration file."""
        if not file_path.exists():
            return {"enabled": False}

        try:
            with open(file_path, 'r') as f:
                return yaml.safe_load(f) or {"enabled": False}
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            return {"enabled": False}

    def check_tool_permission(self, tool_name: str, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Check if the current role is allowed to use this tool.

        Returns:
            Tuple of (allowed: bool, message: str)
        """
        if not self.role_config.get("enabled", False):
            return (True, "")  # Allow all if not enabled

        # Get current agent/role
        current_role = self._get_current_role()

        # Get role configuration
        role_def = self._get_role_definition(current_role)
        if not role_def:
            # Use default role if no specific role found
            role_def = self._get_default_role()

        # Check if tool is explicitly blocked
        blocked_tools = role_def.get("blocked_tools", [])
        if blocked_tools == "*":
            # All tools blocked except explicitly allowed
            allowed_tools = role_def.get("allowed_tools", [])
            if tool_name not in allowed_tools:
                return (False, self._get_violation_message(current_role, tool_name, "not_allowed"))
        elif tool_name in blocked_tools:
            return (False, self._get_violation_message(current_role, tool_name, "blocked"))

        # Check if tool is in allowed list (if defined)
        allowed_tools = role_def.get("allowed_tools", [])
        if allowed_tools and tool_name not in allowed_tools:
            return (False, self._get_violation_message(current_role, tool_name, "not_allowed"))

        # Check path restrictions for write operations
        if tool_name in ["Write", "Edit", "MultiEdit", "NotebookEdit"]:
            path_allowed, path_msg = self._check_path_restrictions(current_role, tool_name, parameters)
            if not path_allowed:
                return (False, path_msg)

        # Log successful permission check
        self._log_tool_usage(current_role, tool_name, True)

        return (True, "")

    def _get_current_role(self) -> str:
        """Get the current active agent/role."""
        # Cache role for 60 seconds to avoid repeated lookups
        if self._current_role and self._role_cache_time:
            if (datetime.now() - self._role_cache_time).seconds < 60:
                return self._current_role

        # Get current agent from state manager
        if get_current_agent:
            current_agent = get_current_agent(self.session_id)
            if current_agent:
                self._current_role = current_agent
                self._role_cache_time = datetime.now()
                return current_agent

        # Default to uninitialized if no agent loaded
        return "uninitialized"

    def _get_role_definition(self, role_name: str) -> Optional[Dict[str, Any]]:
        """Get role definition from configuration."""
        roles = self.role_config.get("roles", {})
        return roles.get(role_name)

    def _get_default_role(self) -> Dict[str, Any]:
        """Get default role configuration."""
        default = self.role_config.get("default_role", {})
        if default:
            return default

        # Fallback default
        return {
            "name": "uninitialized",
            "allowed_tools": ["mcp__agenthub_http__call_agent", "Read", "Grep", "Glob"],
            "blocked_tools": "*",
            "warning": "[NO ROLE] Must call mcp__agenthub_http__call_agent first!"
        }

    def _check_path_restrictions(self, role: str, tool_name: str, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """Check path restrictions for write operations."""
        role_def = self._get_role_definition(role)
        if not role_def:
            return (True, "")

        path_restrictions = role_def.get("path_restrictions", {})
        if not path_restrictions:
            return (True, "")

        # Get file path from parameters
        file_path = parameters.get("file_path", "")
        if not file_path:
            return (True, "")

        # Check write path restrictions
        write_paths = path_restrictions.get("write_paths", [])
        if write_paths:
            path_allowed = False
            for pattern in write_paths:
                if fnmatch.fnmatch(file_path, pattern):
                    path_allowed = True
                    break

            if not path_allowed:
                warnings = role_def.get("warnings", {})
                msg = warnings.get("wrong_path", f"[ROLE VIOLATION] {role} cannot write to {file_path}")
                return (False, msg)

        return (True, "")

    def _get_violation_message(self, role: str, tool_name: str, violation_type: str) -> str:
        """Get appropriate violation message."""
        role_def = self._get_role_definition(role)
        if not role_def:
            role_def = self._get_default_role()

        warnings = role_def.get("warnings", {})

        # Map tool names to warning types
        warning_map = {
            "Write": "write_attempt",
            "Edit": "edit_attempt",
            "MultiEdit": "edit_attempt",
            "Task": "delegation_attempt",
            "Bash": "execution_attempt"
        }

        warning_key = warning_map.get(tool_name, "modification_attempt")

        if warning_key in warnings:
            return warnings[warning_key]

        # Default messages using centralized config
        if violation_type == "blocked" or violation_type == "not_allowed":
            allowed_tools = role_def.get("allowed_tools", [])
            violation_msg = get_info_message("role_violation", tool=tool_name, agent=role)
            tools_msg = get_info_message("available_tools", tools=", ".join(allowed_tools))
            return f"{violation_msg}\n{tools_msg}"

        return get_info_message("role_violation", tool=tool_name, agent=role)

    def _log_tool_usage(self, role: str, tool_name: str, allowed: bool):
        """Log tool usage for analysis."""
        enforcement = self.role_config.get("enforcement", {})
        if not enforcement.get("log_violations", True):
            return

        if allowed and not enforcement.get("log_all", False):
            return  # Only log violations unless log_all is true

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "role": role,
            "tool": tool_name,
            "allowed": allowed,
            "session_id": self.session_id
        }

        # Track in memory
        if not allowed:
            self.violations.append(log_entry)

        # Write to log file if configured
        log_file = enforcement.get("log_file")
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            # Read existing log
            if log_path.exists():
                try:
                    with open(log_path, 'r') as f:
                        log_data = json.load(f)
                except:
                    log_data = []
            else:
                log_data = []

            # Append new entry
            log_data.append(log_entry)

            # Keep only last 1000 entries
            if len(log_data) > 1000:
                log_data = log_data[-1000:]

            # Write back
            try:
                with open(log_path, 'w') as f:
                    json.dump(log_data, f, indent=2)
            except:
                pass  # Don't fail on log write errors

    def get_role_info(self, role: str = None) -> Dict[str, Any]:
        """Get information about a role's permissions."""
        if not role:
            role = self._get_current_role()

        role_def = self._get_role_definition(role)
        if not role_def:
            role_def = self._get_default_role()

        return {
            "role": role,
            "description": role_def.get("description", ""),
            "allowed_tools": role_def.get("allowed_tools", []),
            "blocked_tools": role_def.get("blocked_tools", []),
            "path_restrictions": role_def.get("path_restrictions", {})
        }

    def suggest_delegation(self, tool_name: str) -> str:
        """Suggest which agent should handle this tool."""
        suggestions = {
            "Write": "coding-agent",
            "Edit": "coding-agent or debugger-agent",
            "MultiEdit": "coding-agent or debugger-agent",
            "Bash": "coding-agent or test-orchestrator-agent",
            "NotebookEdit": "coding-agent"
        }

        agent = suggestions.get(tool_name, "appropriate specialized agent")

        return f"Consider delegating to {agent} for this operation."


# Singleton instance
_enforcer_instance = None

def get_role_enforcer(session_id: str = None) -> RoleEnforcer:
    """Get or create role enforcer instance."""
    global _enforcer_instance
    if _enforcer_instance is None or (session_id and _enforcer_instance.session_id != session_id):
        _enforcer_instance = RoleEnforcer(session_id)
    return _enforcer_instance


def check_tool_permission(tool_name: str, parameters: Dict[str, Any],
                         session_id: str = None) -> Tuple[bool, str]:
    """Convenience function to check tool permission."""
    enforcer = get_role_enforcer(session_id)
    return enforcer.check_tool_permission(tool_name, parameters)