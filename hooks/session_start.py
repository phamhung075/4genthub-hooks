#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# ///

"""
Refactored Session start hook with factory pattern and clean architecture.

This hook runs when a Claude session starts and provides:
1. Session context loading and injection
2. Git status and branch information
3. MCP task status and recommendations
4. Development environment context
5. Agent role detection
6. Recent issues and project context

Refactored with:
- Factory pattern for component creation
- Single Responsibility Principle
- Dependency injection
- Clean error handling
- Centralized configuration
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any

import psutil
import yaml

# Add hooks directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Load .env file to make environment variables available throughout the module
from dotenv import load_dotenv

# Import robust project root finder that works with submodules
from utils.env_loader import get_project_root

# Find and load .env from project root (works with submodules)
project_root = get_project_root()
env_file = project_root / ".env"
if env_file.exists():
    load_dotenv(env_file)


# ============================================================================
# Mode Detection for Token Optimization
# ============================================================================

# Check for CLAUDE_CONTEXT_MODE environment variable
# - 'compact' (default): Loads minimal context, saves ~9,000 tokens (60%)
# - 'full': Loads complete verbose context (original behavior)
CONTEXT_MODE = os.getenv("CLAUDE_CONTEXT_MODE", "compact").lower()
USE_COMPACT_MODE = CONTEXT_MODE == "compact"


# ============================================================================
# Abstract Base Classes
# ============================================================================


class ContextProvider(ABC):
    """Base context provider interface."""

    @abstractmethod
    def get_context(self, input_data: dict) -> dict[str, Any] | None:
        """Get context information."""
        pass


class SessionProcessor(ABC):
    """Base session processor interface."""

    @abstractmethod
    def process(self, input_data: dict) -> str | None:
        """Process session start data."""
        pass


class Logger(ABC):
    """Abstract logger interface."""

    @abstractmethod
    def log(self, level: str, message: str, data: dict | None = None):
        """Log a message with optional data."""
        pass


# ============================================================================
# Configuration Management
# ============================================================================


class ConfigurationLoader:
    """Loads and manages YAML configuration files."""

    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self._cache = {}

    def load_config(self, config_name: str) -> dict | None:
        """Load a YAML configuration file."""
        if config_name in self._cache:
            return self._cache[config_name]

        config_path = self.config_dir / f"{config_name}.yaml"
        if not config_path.exists():
            return None

        try:
            with open(config_path) as f:
                config = yaml.safe_load(f)
                self._cache[config_name] = config
                return config
        except Exception:
            return None

    def get_agent_message(self, agent_name: str) -> dict | None:
        """Get initialization message for a specific agent."""
        config = self.load_config("session_start_messages")
        if not config:
            return None

        agent_messages = config.get("agent_messages", {})

        # Check for specific agent
        if agent_name in agent_messages:
            return agent_messages[agent_name]

        # Return default message
        default = agent_messages.get("default_agent", {})
        if default:
            # Replace placeholders
            return {
                "initialization_message": default.get(
                    "initialization_message", ""
                ).replace("{agent_name}", agent_name),
                "role_description": default.get("role_description", "").replace(
                    "{AGENT_NAME}", agent_name.upper().replace("-", " ")
                ),
            }

        return None


# ============================================================================
# Component Implementations
# ============================================================================


class FileLogger(Logger):
    """File-based logger implementation."""

    def __init__(self, log_dir: Path, log_name: str):
        self.log_dir = log_dir
        self.log_name = log_name
        self.log_path = log_dir / log_name
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def log(self, level: str, message: str, data: dict | None = None):
        """Log to JSON file with session tracking."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message,
            "data": data,
        }

        # Load existing log
        log_data = []
        if self.log_path.exists():
            try:
                with open(self.log_path) as f:
                    log_data = json.load(f)
            except:
                log_data = []

        # Append and save
        log_data.append(entry)

        # Keep only last 100 entries
        if len(log_data) > 100:
            log_data = log_data[-100:]

        with open(self.log_path, "w") as f:
            json.dump(log_data, f, indent=2)


class GitContextProvider(ContextProvider):
    """Provides git repository context."""

    def get_context(self, input_data: dict) -> dict[str, Any] | None:
        """Get git status and branch information."""
        try:
            # Get current branch
            branch_result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            current_branch = (
                branch_result.stdout.strip()
                if branch_result.returncode == 0
                else "unknown"
            )

            # Get uncommitted changes
            status_result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            changes = []
            if status_result.returncode == 0 and status_result.stdout.strip():
                changes = status_result.stdout.strip().split("\n")

            # Get recent commits
            log_result = subprocess.run(
                ["git", "log", "--oneline", "-5"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            recent_commits = []
            if log_result.returncode == 0:
                recent_commits = log_result.stdout.strip().split("\n")

            return {
                "current_branch": current_branch,
                "uncommitted_changes": len(changes),
                "changes": changes[:10],  # First 10 changes
                "recent_commits": recent_commits,
                "is_clean": len(changes) == 0,
            }

        except Exception as e:
            return {"error": str(e), "current_branch": "unknown", "is_clean": True}


class MCPContextProvider(ContextProvider):
    """Provides MCP task and project context with automatic project/branch retrieval."""

    def _get_mcp_url_from_config(self) -> str:
        """Get MCP server URL directly from .mcp.json configuration."""
        try:
            # Look for .mcp.json in project root (works with submodules)
            project_root = get_project_root()
            mcp_json_path = project_root / ".mcp.json"

            # Try parent directories if not found
            if not mcp_json_path.exists():
                for _ in range(3):
                    project_root = project_root.parent
                    mcp_json_path = project_root / ".mcp.json"
                    if mcp_json_path.exists():
                        break

            if mcp_json_path.exists():
                with open(mcp_json_path) as f:
                    mcp_config = json.load(f)

                # Extract URL from agenthub_http configuration exactly as shown
                agenthub_config = mcp_config.get("mcpServers", {}).get(
                    "agenthub_http", {}
                )
                configured_url = agenthub_config.get("url", "")
                if configured_url:
                    return configured_url
        except Exception:
            pass

        # Fallback to default
        return "https://api.4genthub.com"

    def get_context(self, input_data: dict) -> dict[str, Any] | None:
        """Get MCP tasks and project context with project/branch IDs."""
        # Load .env for debug logging
        DEBUG_ENABLED = os.getenv("APP_LOG_LEVEL", "").upper() == "DEBUG"
        logger = None
        if DEBUG_ENABLED:
            import logging

            from utils.env_loader import get_ai_data_path

            log_dir = get_ai_data_path()
            debug_log = log_dir / "claude-hooks" / "session_start_mcp_context_debug.log"
            # Ensure subdirectory exists
            debug_log.parent.mkdir(parents=True, exist_ok=True)
            logger = logging.getLogger("session_start.mcp_context")
            logger.setLevel(logging.DEBUG)
            if not logger.handlers:
                handler = logging.FileHandler(debug_log)
                handler.setLevel(logging.DEBUG)
                formatter = logging.Formatter(
                    "%(asctime)s - %(levelname)s - %(message)s"
                )
                handler.setFormatter(formatter)
                logger.addHandler(handler)

        try:
            # ALWAYS log to file
            import logging

            from utils.env_loader import get_ai_data_path

            debug_log = get_ai_data_path() / "session_start_main.log"
            debug_log.parent.mkdir(parents=True, exist_ok=True)

            main_logger = logging.getLogger("session_start_main")
            main_logger.setLevel(logging.DEBUG)
            if not main_logger.handlers:
                handler = logging.FileHandler(debug_log)
                handler.setLevel(logging.DEBUG)
                formatter = logging.Formatter("%(asctime)s - %(message)s")
                handler.setFormatter(formatter)
                main_logger.addHandler(handler)

            main_logger.debug("=" * 80)
            main_logger.debug("MCPContextProvider.get_context() CALLED")

            if logger:
                logger.debug("=" * 80)
                logger.debug("MCPContextProvider.get_context() CALLED")

            # Get MCP server URL directly from .mcp.json
            mcp_server_url = self._get_mcp_url_from_config()
            main_logger.debug(f"MCP URL from config: {mcp_server_url}")

            # TokenManager always reads fresh token from .mcp.json (no cache)
            from utils.mcp_client import MCPHTTPClient

            client = MCPHTTPClient()

            # Ensure client is authenticated
            main_logger.debug("Attempting authentication...")
            auth_result = client.authenticate()
            main_logger.debug(f"Authentication result: {auth_result}")

            # DEBUG: Check if Authorization header is actually set
            auth_header = client.session.headers.get("Authorization", "NOT SET")
            main_logger.debug(
                f"Authorization header: {auth_header[:50] if auth_header != 'NOT SET' else 'NOT SET'}"
            )

            if not auth_result:
                main_logger.debug("✗ MCP authentication FAILED - returning error")
                if logger:
                    logger.debug("MCP authentication failed")
                return {"error": "MCP authentication failed"}

            context = {}

            # Add MCP server URL to context (from .mcp.json)
            context["mcp_server_url"] = mcp_server_url
            main_logger.debug("✓ Added MCP URL to context")

            # Get project and branch information with IDs
            main_logger.debug("Calling _get_project_info...")
            project_info = self._get_project_info(client)
            main_logger.debug(f"_get_project_info returned: {project_info}")

            if project_info:
                context["project_info"] = project_info
                main_logger.debug("✓ Added project_info to context")
            else:
                main_logger.debug("✗ NO project_info returned - skipping branch_info")

            main_logger.debug("Calling _get_branch_info...")
            branch_info = self._get_branch_info(client, project_info)
            main_logger.debug(f"_get_branch_info returned: {branch_info}")

            if branch_info:
                context["branch_info"] = branch_info
                main_logger.debug("✓ Added branch_info to context")
            else:
                main_logger.debug("✗ NO branch_info returned")

            # DEBUG: After branch_info
            if logger:
                logger.debug(f"branch_info result: {branch_info}")
                logger.debug(
                    f"Has git_branch_id: {branch_info.get('git_branch_id') if branch_info else 'branch_info is None'}"
                )

            # Get pending tasks
            pending_tasks = self._query_pending_tasks(client)
            if pending_tasks:
                context["pending_tasks"] = pending_tasks[:5]  # First 5 tasks

            # Get active tasks (in_progress status)
            if branch_info and branch_info.get("git_branch_id"):
                if logger:
                    logger.debug(
                        f"Calling _query_active_tasks with git_branch_id: {branch_info['git_branch_id']}"
                    )

                active_tasks = self._query_active_tasks(
                    client, branch_info["git_branch_id"]
                )

                if logger:
                    logger.debug(f"_query_active_tasks returned: {type(active_tasks)}")
                    logger.debug(f"active_tasks value: {active_tasks}")

                if active_tasks:
                    context["active_tasks"] = active_tasks
                    if logger:
                        logger.debug(
                            f"✅ Added {len(active_tasks)} active tasks to context"
                        )
                else:
                    if logger:
                        logger.debug("❌ No active tasks returned (None or empty list)")
            else:
                if logger:
                    logger.debug(
                        f"❌ NOT calling _query_active_tasks - branch_info={branch_info}"
                    )

            # Get next recommended task
            if branch_info and branch_info.get("git_branch_id"):
                next_task = self._query_next_task(client, branch_info["git_branch_id"])
                if next_task:
                    context["next_task"] = next_task

            if logger:
                logger.debug(f"Final context keys: {list(context.keys())}")
                logger.debug("=" * 80)

            return context if context else None

        except Exception as e:
            if logger:
                logger.debug(f"Exception in get_context: {e}")
                logger.exception("Full traceback:")
            return {"error": str(e)}

    def _get_project_info(self, client) -> dict | None:
        """Get project information from MCP by matching git repository name."""
        # DEBUG: Log at method entry
        import logging

        from utils.env_loader import get_ai_data_path

        debug_log = get_ai_data_path() / "session_start_project_info.log"
        debug_log.parent.mkdir(parents=True, exist_ok=True)

        logger = logging.getLogger("project_info_method")
        logger.setLevel(logging.DEBUG)
        if not logger.handlers:
            handler = logging.FileHandler(debug_log)
            handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter("%(asctime)s - %(message)s")
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        logger.debug("=" * 80)
        logger.debug("_get_project_info() CALLED")

        try:
            # Get project name from git remote or folder name
            logger.debug("Calling _get_project_name()...")
            project_name = self._get_project_name()
            logger.debug(f"_get_project_name() returned: '{project_name}'")

            if not project_name:
                logger.debug("✗ NO PROJECT NAME - returning None")
                return None

            # Call MCP to list all projects
            mcp_request = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {"name": "manage_project", "arguments": {"action": "list"}},
                "id": 1,
            }

            logger.debug(f"Sending API request to: {client.base_url}/mcp")

            response = client.session.post(
                f"{client.base_url}/mcp", json=mcp_request, timeout=client.timeout
            )

            logger.debug(f"Response status: {response.status_code}")
            if response.status_code != 200:
                logger.debug(f"✗ API ERROR: {response.text[:200]}")

            if response.status_code == 200:
                result = response.json()
                if "result" in result and not result["result"].get("isError"):
                    # The actual data is in result.content[0].text as a JSON string
                    content = result["result"].get("content", [])
                    if content and len(content) > 0:
                        content_text = content[0].get("text", "")
                        try:
                            # DEBUG: Log project API response
                            import logging

                            from utils.env_loader import get_ai_data_path

                            debug_log = (
                                get_ai_data_path() / "session_start_project_info.log"
                            )
                            debug_log.parent.mkdir(parents=True, exist_ok=True)

                            logger = logging.getLogger("project_info")
                            logger.setLevel(logging.DEBUG)
                            if not logger.handlers:
                                handler = logging.FileHandler(debug_log)
                                handler.setLevel(logging.DEBUG)
                                formatter = logging.Formatter(
                                    "%(asctime)s - %(message)s"
                                )
                                handler.setFormatter(formatter)
                                logger.addHandler(handler)

                            # Parse the JSON string in the text field
                            parsed_content = json.loads(content_text)

                            logger.debug("=" * 80)
                            logger.debug("PROJECT INFO PARSING")
                            logger.debug(f"parsed_content type: {type(parsed_content)}")
                            logger.debug(
                                f"parsed_content keys: {parsed_content.keys() if isinstance(parsed_content, dict) else 'N/A'}"
                            )

                            projects_data = parsed_content.get("data", {}).get(
                                "projects", []
                            )
                            logger.debug(f"projects_data type: {type(projects_data)}")
                            logger.debug(f"projects_data value: {projects_data}")
                            logger.debug(f"project_name looking for: '{project_name}'")

                            # Handle both single object and array
                            matching_projects = []

                            if isinstance(projects_data, dict):
                                # Single project returned as object
                                if (
                                    projects_data.get("name", "").lower()
                                    == project_name.lower()
                                ):
                                    matching_projects.append(projects_data)
                            elif isinstance(projects_data, list):
                                # Multiple projects returned as array
                                for project in projects_data:
                                    if (
                                        project.get("name", "").lower()
                                        == project_name.lower()
                                    ):
                                        matching_projects.append(project)

                            # If multiple projects with same name, select the NEWEST one (highest created_at)
                            if matching_projects:
                                # Sort by created_at descending (newest first)
                                matching_projects.sort(
                                    key=lambda p: p.get("created_at", ""), reverse=True
                                )
                                newest_project = matching_projects[0]
                                logger.debug(
                                    f"✓ FOUND PROJECT: {newest_project.get('name')} ({newest_project.get('id')})"
                                )
                                return {
                                    "project_name": newest_project.get("name"),
                                    "project_id": newest_project.get("id"),
                                    "found": True,
                                }

                            # Project not found
                            logger.debug(
                                f"✗ NO PROJECT FOUND matching '{project_name}'"
                            )
                            logger.debug(f"  Checked {len(matching_projects)} projects")
                            return {
                                "project_name": project_name,
                                "project_id": None,
                                "found": False,
                            }
                        except json.JSONDecodeError:
                            pass  # Fall through to error case

        except Exception as e:
            return {
                "error": str(e),
                "project_name": project_name
                if "project_name" in locals()
                else "unknown",
            }

        return None

    def _get_branch_info(self, client, project_info: dict | None) -> dict | None:
        """Get branch information from MCP by matching current git branch."""
        try:
            if not project_info or not project_info.get("project_id"):
                return None

            # Get current branch name from main repository, not submodule
            # If we found the main repository during project detection, use it
            current_dir = get_project_root()
            search_dir = current_dir
            git_path = None

            # Search for .git to determine repository location
            for _ in range(3):
                potential_git = search_dir / ".git"
                if potential_git.exists():
                    git_path = potential_git
                    break
                search_dir = search_dir.parent
                if search_dir == search_dir.parent:
                    break

            # If in a submodule, get branch from main repository
            if git_path and git_path.is_file():
                # Look for main repository
                project_root = current_dir
                for _ in range(5):
                    parent_dir = project_root.parent
                    parent_git = parent_dir / ".git"
                    if parent_git.is_dir():
                        project_root = parent_dir
                        break
                    elif parent_dir == project_root:
                        break
                    else:
                        project_root = parent_dir

                # Get branch from main repository
                branch_result = subprocess.run(
                    [
                        "git",
                        "-C",
                        str(project_root),
                        "rev-parse",
                        "--abbrev-ref",
                        "HEAD",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
            else:
                # Normal git repository
                branch_result = subprocess.run(
                    ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )

            current_branch = (
                branch_result.stdout.strip() if branch_result.returncode == 0 else None
            )

            if not current_branch or current_branch == "HEAD":
                return None

            # Call MCP to list branches for the project
            mcp_request = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "manage_git_branch",
                    "arguments": {
                        "action": "list",
                        "project_id": project_info["project_id"],
                    },
                },
                "id": 2,
            }

            # DEBUG: Log API call
            import logging

            from utils.env_loader import get_ai_data_path

            debug_log = get_ai_data_path() / "session_start_branch_match.log"
            debug_log.parent.mkdir(parents=True, exist_ok=True)

            logger = logging.getLogger("branch_match")
            logger.setLevel(logging.DEBUG)
            if not logger.handlers:
                handler = logging.FileHandler(debug_log)
                handler.setLevel(logging.DEBUG)
                formatter = logging.Formatter("%(asctime)s - %(message)s")
                handler.setFormatter(formatter)
                logger.addHandler(handler)

            logger.debug("=" * 80)
            logger.debug("API CALL TO GET BRANCHES")
            logger.debug(f"URL: {client.base_url}/mcp")
            logger.debug(f"Project ID: {project_info['project_id']}")

            response = client.session.post(
                f"{client.base_url}/mcp", json=mcp_request, timeout=client.timeout
            )

            logger.debug(f"Response status: {response.status_code}")
            if response.status_code != 200:
                logger.debug(f"✗ API ERROR - Status {response.status_code}")
                logger.debug(f"Response: {response.text}")

            if response.status_code == 200:
                result = response.json()
                if "result" in result and not result["result"].get("isError"):
                    # The actual data is in result.content[0].text as a JSON string
                    content = result["result"].get("content", [])
                    if content and len(content) > 0:
                        content_text = content[0].get("text", "")
                        try:
                            # Parse the JSON string in the text field
                            parsed_content = json.loads(content_text)
                            # Note: API returns 'git_branchs' (typo) not 'git_branches'
                            branches_data = parsed_content.get("data", {}).get(
                                "git_branchs", []
                            )

                            # Handle both single branch (dict) and multiple branches (list)
                            # API sometimes returns single branch as dict instead of list
                            if isinstance(branches_data, dict):
                                # Single branch returned as dict - wrap in list
                                branches = [branches_data]
                            elif isinstance(branches_data, list):
                                # Multiple branches returned as list
                                branches = branches_data
                            else:
                                # Invalid type - neither dict nor list
                                return {
                                    "branch_name": current_branch,
                                    "git_branch_id": None,
                                    "found": False,
                                    "error": f"Invalid branches data type from API: {type(branches_data).__name__}",
                                }

                            # Find matching branch by git_branch_name first, then name
                            # Handle version branches where dots are normalized to hyphens (e.g., 0.0.6-agents-base → 0-0-6-agents-base)

                            # DEBUG: Log branch matching attempt
                            import logging

                            from utils.env_loader import get_ai_data_path

                            debug_log = (
                                get_ai_data_path() / "session_start_branch_match.log"
                            )
                            debug_log.parent.mkdir(parents=True, exist_ok=True)

                            logger = logging.getLogger("branch_match")
                            logger.setLevel(logging.DEBUG)
                            if not logger.handlers:
                                handler = logging.FileHandler(debug_log)
                                handler.setLevel(logging.DEBUG)
                                formatter = logging.Formatter(
                                    "%(asctime)s - %(message)s"
                                )
                                handler.setFormatter(formatter)
                                logger.addHandler(handler)

                            logger.debug("=" * 80)
                            logger.debug("BRANCH MATCHING START")
                            logger.debug(f"Current git branch: '{current_branch}'")
                            logger.debug(
                                f"Normalized: '{current_branch.replace('.', '-')}'"
                            )
                            logger.debug(f"Total branches from API: {len(branches)}")

                            for branch in branches:
                                # Defensive type check: ensure branch is a dict before calling .get()
                                if not isinstance(branch, dict):
                                    logger.debug(
                                        f"Skipping invalid branch (not dict): {type(branch)}"
                                    )
                                    continue  # Skip invalid entries

                                branch_git_name = branch.get("git_branch_name", "")
                                branch_name = branch.get("name", "")

                                logger.debug(
                                    f"Checking branch: git_branch_name='{branch_git_name}', name='{branch_name}'"
                                )

                                # Normalize git branch name for comparison (dots → hyphens)
                                normalized_current = current_branch.replace(".", "-")

                                # Try multiple matching strategies:
                                # 1. Exact match on git_branch_name
                                # 2. Exact match on name
                                # 3. Normalized match (for version branches)
                                match1 = branch_git_name == current_branch
                                match2 = branch_name == current_branch
                                match3 = branch_git_name == normalized_current
                                match4 = branch_name == normalized_current

                                logger.debug(
                                    f"  Match git_branch_name==current: {match1}"
                                )
                                logger.debug(f"  Match name==current: {match2}")
                                logger.debug(
                                    f"  Match git_branch_name==normalized: {match3}"
                                )
                                logger.debug(f"  Match name==normalized: {match4}")

                                if match1 or match2 or match3 or match4:
                                    logger.debug(
                                        f"✓ MATCH FOUND! Returning git_branch_id={branch.get('id')}"
                                    )
                                    return {
                                        "branch_name": current_branch,
                                        "git_branch_id": branch.get("id"),
                                        "found": True,
                                    }

                            # Branch not found
                            logger.debug(
                                f"✗ NO MATCH FOUND after checking {len(branches)} branches"
                            )
                            return {
                                "branch_name": current_branch,
                                "git_branch_id": None,
                                "found": False,
                            }
                        except json.JSONDecodeError:
                            pass  # Fall through to error case

        except Exception as e:
            current_branch = "unknown"
            try:
                branch_result = subprocess.run(
                    ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if branch_result.returncode == 0:
                    current_branch = branch_result.stdout.strip()
            except:
                pass
            return {"error": str(e), "branch_name": current_branch}

        return None

    def _get_project_name(self) -> str | None:
        """Get project name from git remote URL or folder name, checking parent repo if in submodule."""
        try:
            # First, check if we're in a git submodule by looking for .git file vs directory
            # Start from project root and check parent directories for .git
            current_dir = get_project_root()

            # Look for .git in current directory or parent directories (submodule might be in parent)
            search_dir = current_dir
            git_path = None

            # Search up to 3 levels to find .git
            for _ in range(3):
                potential_git = search_dir / ".git"
                if potential_git.exists():
                    git_path = potential_git
                    break
                search_dir = search_dir.parent
                if search_dir == search_dir.parent:  # Reached root
                    break

            # If .git is a file (submodule), navigate to parent repository
            if git_path and git_path.is_file():
                # We're in a submodule, try to find the main repository
                # Look for the project root by going up directories
                project_root = current_dir
                max_levels = 5  # Prevent infinite loop

                for _ in range(max_levels):
                    parent_dir = project_root.parent
                    parent_git = parent_dir / ".git"

                    # If parent has a .git directory (not file), it's the main repo
                    if parent_git.is_dir():
                        project_root = parent_dir
                        break
                    elif parent_dir == project_root:  # Reached filesystem root
                        break
                    else:
                        project_root = parent_dir

                # Try to get remote URL from the main repository
                remote_result = subprocess.run(
                    ["git", "-C", str(project_root), "remote", "get-url", "origin"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )

                if remote_result.returncode == 0:
                    remote_url = remote_result.stdout.strip()
                    project_name = self._extract_project_name_from_url(remote_url)
                    if project_name:
                        return project_name

                # Fallback to main repository directory name
                return project_root.name

            else:
                # Normal git repository, use current approach
                remote_result = subprocess.run(
                    ["git", "remote", "get-url", "origin"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )

                if remote_result.returncode == 0:
                    remote_url = remote_result.stdout.strip()
                    project_name = self._extract_project_name_from_url(remote_url)
                    if project_name:
                        return project_name

                # Fallback to current directory name
                return current_dir.name

        except Exception:
            # Final fallback to current directory name
            try:
                return Path.cwd().name
            except:
                return None

    def _extract_project_name_from_url(self, remote_url: str) -> str | None:
        """Extract project name from git remote URL."""
        if not remote_url:
            return None

        # Handle various URL formats
        if remote_url.endswith(".git"):
            remote_url = remote_url[:-4]

        # Extract last part of path
        if "/" in remote_url:
            project_name = remote_url.split("/")[-1]
        else:
            project_name = remote_url

        return project_name if project_name else None

    def _query_pending_tasks(self, client) -> list[dict] | None:
        """Query pending tasks from MCP."""
        try:
            mcp_request = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "manage_task",
                    "arguments": {
                        "action": "list",
                        "status": "todo,in_progress",
                        "limit": 5,
                    },
                },
                "id": 3,
            }

            response = client.session.post(
                f"{client.base_url}/mcp", json=mcp_request, timeout=client.timeout
            )

            if response.status_code == 200:
                result = response.json()
                if "result" in result and not result["result"].get("isError"):
                    # The actual data is in result.content[0].text as a JSON string
                    content = result["result"].get("content", [])
                    if content and len(content) > 0:
                        content_text = content[0].get("text", "")
                        try:
                            # Parse the JSON string in the text field
                            parsed_content = json.loads(content_text)
                            return parsed_content.get("data", {}).get("tasks", [])
                        except json.JSONDecodeError:
                            pass  # Fall through to return None

        except Exception:
            pass
        return None

    def _query_active_tasks(self, client, git_branch_id: str) -> list[dict] | None:
        """Query active tasks (todo and in_progress status) from MCP for the current branch."""
        # Only enable debug logging if APP_LOG_LEVEL=DEBUG in environment
        DEBUG_ENABLED = os.getenv("APP_LOG_LEVEL", "").upper() == "DEBUG"

        # Define debug log path FIRST (before conditional) so it's always in scope
        from utils.env_loader import get_ai_data_path

        log_dir = get_ai_data_path()
        debug_log = log_dir / "claude-hooks" / "session_start_active_tasks_debug.log"

        # Set up debug logger only if debug is enabled
        logger = None
        if DEBUG_ENABLED:
            import logging

            # Ensure subdirectory exists
            debug_log.parent.mkdir(parents=True, exist_ok=True)
            logger = logging.getLogger("session_start.active_tasks")
            logger.setLevel(logging.DEBUG)

            # Create file handler if not exists (debug_log already defined above)
            if not logger.handlers:
                handler = logging.FileHandler(debug_log)
                handler.setLevel(logging.DEBUG)
                formatter = logging.Formatter(
                    "%(asctime)s - %(levelname)s - %(message)s"
                )
                handler.setFormatter(formatter)
                logger.addHandler(handler)

        try:
            # DEBUG POINT 1: Method Entry
            if logger:
                logger.debug(
                    f"_query_active_tasks called with git_branch_id: {git_branch_id}"
                )
                logger.debug(
                    "Starting active tasks query for todo and in_progress statuses"
                )
                logger.debug(f"Debug log location: {debug_log}")

            # Query all tasks for the branch (without status filter)
            # Then filter on the client side for todo and in_progress
            mcp_request = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "manage_task",
                    "arguments": {
                        "action": "list",
                        "git_branch_id": git_branch_id,
                        "limit": 50,  # Increased to ensure we get all active tasks
                    },
                },
                "id": 5,
            }

            response = client.session.post(
                f"{client.base_url}/mcp", json=mcp_request, timeout=client.timeout
            )

            # DEBUG POINT 2: After API Request
            if logger:
                logger.debug(f"Response status code: {response.status_code}")
                logger.debug(f"Response headers: {dict(response.headers)}")
                logger.debug(f"Raw response body: {response.text}")

            if response.status_code == 200:
                result = response.json()

                # DEBUG POINT 3: After JSON Parse
                if logger:
                    logger.debug(f"Parsed result structure: {type(result)}")
                    logger.debug(f"Has 'result' key: {'result' in result}")
                if "result" in result and logger:
                    logger.debug(
                        f"Has error in result: {result['result'].get('isError', False)}"
                    )
                    logger.debug(f"Full result object: {json.dumps(result, indent=2)}")

                if "result" in result and not result["result"].get("isError"):
                    # The actual data is in result.content[0].text as a JSON string
                    content = result["result"].get("content", [])

                    # DEBUG POINT 4: After Content Extraction
                    if logger:
                        logger.debug(f"Content array length: {len(content)}")
                    if content and len(content) > 0:
                        if logger:
                            logger.debug(f"First content item type: {type(content[0])}")
                        content_text = content[0].get("text", "")
                        if logger:
                            logger.debug(
                                f"Raw content text (before JSON parse): {content_text}"
                            )

                        try:
                            # Parse the JSON string in the text field
                            parsed_content = json.loads(content_text)

                            # DEBUG POINT 5: After Task Parsing
                            if logger:
                                logger.debug(
                                    f"parsed_content structure: {type(parsed_content)}"
                                )
                                logger.debug(
                                    f"data object keys: {parsed_content.get('data', {}).keys() if isinstance(parsed_content.get('data'), dict) else 'N/A'}"
                                )
                            tasks = parsed_content.get("data", {}).get("tasks", [])
                            if logger:
                                logger.debug(f"tasks value type: {type(tasks)}")
                                logger.debug(
                                    f"tasks value content: {json.dumps(tasks, indent=2) if tasks else 'Empty or None'}"
                                )

                            # Handle both single task (dict) and multiple tasks (list)
                            if isinstance(tasks, dict):
                                tasks = [tasks]  # Wrap single task in list
                            elif not isinstance(tasks, list):
                                tasks = []  # Fallback to empty list for invalid types

                            # DEBUG POINT 6: After Type Normalization
                            if logger:
                                logger.debug(f"Final tasks list length: {len(tasks)}")
                                logger.debug(
                                    f"Final tasks list content: {json.dumps(tasks, indent=2)}"
                                )
                                if tasks:
                                    for idx, task in enumerate(tasks):
                                        logger.debug(
                                            f"Task {idx} structure: {json.dumps(task, indent=2)}"
                                        )

                            # Filter tasks to only show "todo" and "in_progress" statuses
                            # Exclude completed, cancelled, and other statuses
                            active_statuses = ["todo", "in_progress"]
                            filtered_tasks = []
                            for task in tasks:
                                task_status = task.get("status", "").lower()
                                if task_status in active_statuses:
                                    filtered_tasks.append(task)

                            result_to_return = (
                                filtered_tasks if filtered_tasks else None
                            )

                            # DEBUG POINT 7: Method Exit
                            if logger:
                                logger.debug(f"Total tasks before filter: {len(tasks)}")
                                logger.debug(
                                    f"Tasks after filtering for todo/in_progress: {len(filtered_tasks) if filtered_tasks else 0}"
                                )
                                logger.debug(
                                    f"What is being returned: {result_to_return}"
                                )
                                logger.debug(
                                    f"Return value type: {type(result_to_return)}"
                                )
                                if result_to_return:
                                    logger.debug(
                                        f"Return value length: {len(result_to_return)}"
                                    )

                            return result_to_return
                        except json.JSONDecodeError as json_err:
                            if logger:
                                logger.debug(f"JSON decode error: {json_err}")
                                logger.debug(
                                    f"Failed to parse content_text: {content_text}"
                                )
                            pass  # Fall through to return None
                    else:
                        if logger:
                            logger.debug("Content array is empty or None")
                else:
                    if logger:
                        logger.debug(
                            "Result check failed - no 'result' key or has error"
                        )
            else:
                if logger:
                    logger.debug(
                        f"Response status code is not 200: {response.status_code}"
                    )

        except Exception as e:
            if logger:
                logger.debug(f"Exception in _query_active_tasks: {e}")
                logger.exception("Full traceback:")

        # DEBUG: Final return None
        if logger:
            logger.debug("Returning None from _query_active_tasks")
        return None

    def _query_next_task(self, client, git_branch_id: str) -> dict | None:
        """Query next recommended task."""
        try:
            mcp_request = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "manage_task",
                    "arguments": {
                        "action": "next",
                        "git_branch_id": git_branch_id,
                        "include_context": True,
                    },
                },
                "id": 4,
            }

            response = client.session.post(
                f"{client.base_url}/mcp", json=mcp_request, timeout=client.timeout
            )

            if response.status_code == 200:
                result = response.json()
                if "result" in result and not result["result"].get("isError"):
                    # The actual data is in result.content[0].text as a JSON string
                    content = result["result"].get("content", [])
                    if content and len(content) > 0:
                        content_text = content[0].get("text", "")
                        try:
                            # Parse the JSON string in the text field
                            parsed_content = json.loads(content_text)
                            return parsed_content.get("data", {}).get("task")
                        except json.JSONDecodeError:
                            pass  # Fall through to return None

        except Exception:
            pass
        return None


class DevelopmentContextProvider(ContextProvider):
    """Provides development environment context with multi-project architecture detection."""

    def get_context(self, input_data: dict) -> dict[str, Any] | None:
        """Get comprehensive development environment context."""
        try:
            context = {}
            project_root = get_project_root()

            # Detect frontend project
            frontend_info = self._detect_frontend(project_root)
            if frontend_info:
                context["frontend"] = frontend_info

            # Detect backend project
            backend_info = self._detect_backend(project_root)
            if backend_info:
                context["backend"] = backend_info

            # Detect hook system
            hook_info = self._detect_hook_system(project_root)
            if hook_info:
                context["hooks"] = hook_info

            # Detect infrastructure
            infra_info = self._detect_infrastructure(project_root)
            if infra_info:
                context["infrastructure"] = infra_info

            # Legacy fields for backward compatibility
            context["working_directory"] = str(project_root)
            context["python_version"] = sys.version.split()[0]
            context["platform"] = sys.platform
            context["virtual_env"] = os.environ.get("VIRTUAL_ENV") is not None

            return context if context else None

        except Exception as e:
            return {"error": str(e)}

    def _detect_frontend(self, project_root: Path) -> dict[str, Any] | None:
        """Detect frontend project (React/TypeScript/Vite)."""
        try:
            frontend_dir = project_root / "agenthub-frontend"
            if not frontend_dir.exists():
                return None

            info = {"detected": True, "path": "agenthub-frontend/"}

            # Parse package.json for versions
            package_json = frontend_dir / "package.json"
            if package_json.exists():
                with open(package_json) as f:
                    data = json.load(f)
                    deps = data.get("dependencies", {})
                    dev_deps = data.get("devDependencies", {})

                    # Extract framework versions
                    if "react" in deps:
                        react_version = deps["react"].replace("^", "").replace("~", "")
                        info["react_version"] = react_version.split(".")[0] + ".x"

                    if "typescript" in deps or "typescript" in dev_deps:
                        ts_version = (
                            (deps.get("typescript") or dev_deps.get("typescript", ""))
                            .replace("^", "")
                            .replace("~", "")
                        )
                        info["typescript_version"] = (
                            ts_version.split(".")[0] + ".x"
                            if ts_version
                            else "detected"
                        )

                    if "vite" in dev_deps:
                        vite_version = (
                            dev_deps["vite"].replace("^", "").replace("~", "")
                        )
                        info["vite_version"] = vite_version.split(".")[0] + ".x"

                    # Check for UI frameworks
                    ui_frameworks = []
                    if "tailwindcss" in deps or "tailwindcss" in dev_deps:
                        ui_frameworks.append("Tailwind CSS")
                    if any("radix" in dep for dep in deps.keys()):
                        ui_frameworks.append("shadcn/ui")
                    if ui_frameworks:
                        info["ui_frameworks"] = ui_frameworks

            # Check for key files
            key_files = []
            for file in ["package.json", "vite.config.ts", "tsconfig.json"]:
                if (frontend_dir / file).exists():
                    key_files.append(file)
            if key_files:
                info["key_files"] = key_files

            info["port"] = 3800

            return info

        except Exception:
            return None

    def _detect_backend(self, project_root: Path) -> dict[str, Any] | None:
        """Detect backend project (Python/FastMCP/DDD)."""
        try:
            backend_dir = project_root / "agenthub_main"
            if not backend_dir.exists():
                return None

            info = {"detected": True, "path": "agenthub_main/"}

            # Parse pyproject.toml for dependencies
            pyproject = backend_dir / "pyproject.toml"
            if pyproject.exists():
                try:
                    import toml

                    data = toml.load(str(pyproject))
                    deps = data.get("project", {}).get("dependencies", [])

                    # Extract framework versions
                    frameworks = []
                    for dep in deps:
                        if "mcp" in dep.lower() and "mcp>=" in dep:
                            frameworks.append("FastMCP")
                        elif "fastapi" in dep.lower():
                            frameworks.append("FastAPI")

                    if frameworks:
                        info["frameworks"] = frameworks

                    # Check for SQLAlchemy
                    if any("sqlalchemy" in dep.lower() for dep in deps):
                        info["orm"] = "SQLAlchemy"

                except ImportError:
                    # Fallback if toml not available - parse manually
                    with open(pyproject) as f:
                        content = f.read()
                        if "mcp>=" in content:
                            info["frameworks"] = ["FastMCP", "FastAPI"]
                        if "sqlalchemy>=" in content:
                            info["orm"] = "SQLAlchemy"

            info["architecture"] = "DDD (Domain-Driven Design)"
            info["language"] = f"Python {sys.version.split()[0]}"

            # Check for key files
            key_files = []
            for file in ["pyproject.toml", "requirements.txt"]:
                if (backend_dir / file).exists():
                    key_files.append(file)
            if key_files:
                info["key_files"] = key_files

            info["port"] = 8000

            return info

        except Exception:
            return None

    def _detect_hook_system(self, project_root: Path) -> dict[str, Any] | None:
        """Detect Claude Code hook system."""
        try:
            hooks_dir = project_root / ".claude" / "hooks"
            if not hooks_dir.exists():
                return None

            info = {"detected": True, "path": ".claude/hooks/"}

            info["type"] = "Python-based enforcement"

            # Check for key hook files
            features = []
            key_files = []

            if (hooks_dir / "pre_tool_use.py").exists():
                features.append("File system protection")
                key_files.append("pre_tool_use.py")

            if (hooks_dir / "post_tool_use.py").exists():
                features.append("Documentation indexing")
                key_files.append("post_tool_use.py")

            if (hooks_dir / "utils" / "session_tracker.py").exists():
                features.append("2-hour tracking")

            if features:
                info["features"] = features
            if key_files:
                info["key_files"] = key_files

            return info

        except Exception:
            return None

    def _detect_infrastructure(self, project_root: Path) -> dict[str, Any] | None:
        """Detect infrastructure components."""
        try:
            info = {}

            # Check for Docker (multiple possible locations)
            docker_compose_files = [
                project_root / "docker-compose.yml",
                project_root / "docker-system" / "docker" / "docker-compose.yml",
                project_root / "docker-system" / "docker" / "docker-compose.dev.yml",
            ]

            docker_found = False
            docker_compose_content = ""

            for compose_file in docker_compose_files:
                if compose_file.exists():
                    docker_found = True
                    try:
                        with open(compose_file) as f:
                            docker_compose_content += f.read()
                    except:
                        pass

            if docker_found or (project_root / "docker-system").exists():
                info["container"] = "Docker + docker-compose"

            # Check for database configuration
            databases = []
            if docker_compose_content:
                if "postgres" in docker_compose_content.lower():
                    databases.append("PostgreSQL (Docker)")

            # Check for SQLite database
            if (project_root / "data").exists() or (
                project_root / "agenthub_main" / "data"
            ).exists():
                databases.append("SQLite (dev)")

            if databases:
                info["database"] = " / ".join(databases)

            # Check for authentication (in docker-compose or env files)
            if docker_compose_content and "keycloak" in docker_compose_content.lower():
                info["auth"] = "Keycloak"

            # Check for configuration files
            config_files = []
            if (project_root / ".env").exists():
                config_files.append(".env")
            if (project_root / "docker-system" / "docker-menu.sh").exists():
                config_files.append("docker-system/docker-menu.sh")

            if config_files:
                info["config"] = ", ".join(config_files)

            return info if info else None

        except Exception:
            return None


class IssueContextProvider(ContextProvider):
    """Provides recent issues and problem context."""

    def get_context(self, input_data: dict) -> dict[str, Any] | None:
        """Get recent issues from logs."""
        try:
            from utils.env_loader import get_ai_data_path

            log_dir = get_ai_data_path()
            error_files = ["pre_tool_use_errors.log", "post_tool_use_errors.log"]

            recent_issues = []
            for error_file in error_files:
                error_path = log_dir / error_file
                if error_path.exists():
                    try:
                        with open(error_path) as f:
                            lines = f.readlines()[-5:]  # Last 5 errors
                            recent_issues.extend(
                                [line.strip() for line in lines if line.strip()]
                            )
                    except:
                        pass

            return {"recent_issues": recent_issues[-10:]} if recent_issues else None

        except Exception:
            return None


class AgentMessageProvider(ContextProvider):
    """Provides agent-specific initialization messages."""

    def __init__(self, config_loader: ConfigurationLoader):
        self.config_loader = config_loader

    def get_context(self, input_data: dict) -> dict[str, Any] | None:
        """Get agent initialization messages based on session type."""
        try:
            # Detect session type
            session_type = self._detect_session_type()

            # Determine which agent to use
            agent_name = None

            # CHECK FOR CCLAUDE_AGENT ENVIRONMENT VARIABLE FIRST (highest priority)
            cclaude_agent = os.getenv("CCLAUDE_AGENT")
            if cclaude_agent:
                agent_name = cclaude_agent
            elif session_type == "principal":
                # Principal session defaults to master-orchestrator-agent (unless CCLAUDE_AGENT is set)
                agent_name = "master-orchestrator-agent"
            else:
                # Try to detect agent from context
                agent_name = self._detect_agent_from_context(input_data)

            if not agent_name:
                # Default to master-orchestrator for principal sessions
                if session_type == "principal":
                    agent_name = "master-orchestrator-agent"
                else:
                    return None

            # Get agent message from config
            agent_message = self.config_loader.get_agent_message(agent_name)
            if agent_message:
                return {
                    "agent_name": agent_name,
                    "session_type": session_type,
                    "initialization_message": agent_message.get(
                        "initialization_message", ""
                    ),
                    "role_description": agent_message.get("role_description", ""),
                }

            return None

        except Exception:
            return None

    def _detect_session_type(self) -> str:
        """Detect the type of session."""
        if "CLAUDE_SUBAGENT" in os.environ:
            return "sub-agent"
        return "principal"

    def _detect_agent_from_context(self, input_data: dict) -> str | None:
        """Detect agent type from input context."""
        try:
            conversation = input_data.get("conversation_history", [])

            for message in reversed(conversation[-10:]):
                content = message.get("content", "")
                if "mcp__agenthub_http__call_agent" in content:
                    import re

                    # Check for agent name in various patterns
                    match = re.search(r'"name_agent":\s*"([^"]+)"', content)
                    if match:
                        return match.group(1)

                    match = re.search(r'call_agent\(["\']([^"\']+)["\']', content)
                    if match:
                        return match.group(1)

                    match = re.search(
                        r"name_agent.*?([a-z-]+agent)", content, re.IGNORECASE
                    )
                    if match:
                        return match.group(1).lower()

            # Check for task_id pattern suggesting sub-agent
            for message in reversed(conversation[-5:]):
                content = message.get("content", "")
                if "task_id:" in content.lower():
                    # This is likely a sub-agent session, but we don't know which one
                    return None

        except:
            pass

        return None


class SessionStartProcessor(SessionProcessor):
    """Main session start processor."""

    def __init__(self, logger: Logger):
        self.logger = logger

    def process(self, input_data: dict) -> str | None:
        """Process session start and generate context output."""
        try:
            # Log session start
            self.logger.log("info", "Session started", input_data)

            # Get or generate session ID
            session_id = self._get_session_id(input_data)

            # Detect session type
            session_type = self._detect_session_type()
            agent_type = self._detect_agent_from_context(input_data)

            output_parts = []

            # Add session info with session ID
            if session_type or agent_type:
                session_info = []
                if session_type:
                    session_info.append(f"Session Type: {session_type}")
                if agent_type:
                    session_info.append(f"Detected Agent: {agent_type}")

                # Format session header with ID
                session_header = f"🚀 Session {session_id} Context:"
                output_parts.append(session_header + "\n" + "\n".join(session_info))

            return "\n\n".join(output_parts) if output_parts else None

        except Exception as e:
            self.logger.log("error", f"Session processing failed: {e}")
            return None

    def _detect_session_type(self) -> str | None:
        """Detect the type of session (principal vs sub-agent)."""
        try:
            # Check if this is a sub-agent session by looking for specific patterns
            if "CLAUDE_SUBAGENT" in os.environ:
                return "sub-agent"

            # Default to principal session
            return "principal"
        except:
            return None

    def _detect_agent_from_context(self, input_data: dict) -> str | None:
        """Detect agent type from input context."""
        try:
            # Check conversation history for agent loading patterns
            conversation = input_data.get("conversation_history", [])

            for message in reversed(conversation[-10:]):  # Last 10 messages
                content = message.get("content", "")
                if "mcp__agenthub_http__call_agent" in content:
                    # Extract agent name
                    import re

                    match = re.search(r'"name_agent":\s*"([^"]+)"', content)
                    if match:
                        return match.group(1)

                    # Alternative pattern
                    match = re.search(r'call_agent\(["\']([^"\']+)["\']', content)
                    if match:
                        return match.group(1)

            return None
        except:
            return None

    def _get_session_id(self, input_data: dict) -> str:
        """Get session ID from input data or generate a new one."""
        try:
            # Try to get session ID from input data first
            session_id = input_data.get("session_id")
            if session_id:
                # Return the complete session ID
                return session_id

            # Generate a new session ID if not provided
            timestamp = datetime.now().isoformat()
            full_session_id = hashlib.md5(timestamp.encode()).hexdigest()
            # Return complete session ID
            return full_session_id
        except Exception:
            # Fallback to a simple timestamp-based ID
            return datetime.now().strftime("%H%M%S")


class ContextFormatterProcessor(SessionProcessor):
    """Formats and presents context information."""

    def __init__(self, context_providers: list[ContextProvider], logger: Logger):
        self.context_providers = context_providers
        self.logger = logger

    def process(self, input_data: dict) -> str | None:
        """Format all context information."""
        try:
            context_data = {}

            # Gather context from all providers
            for provider in self.context_providers:
                try:
                    provider_name = provider.__class__.__name__.replace(
                        "Provider", ""
                    ).lower()
                    provider_context = provider.get_context(input_data)
                    if provider_context:
                        context_data[provider_name] = provider_context
                except Exception as e:
                    self.logger.log(
                        "error",
                        f"Context provider {provider.__class__.__name__} failed: {e}",
                    )

            return self._format_context(context_data) if context_data else None

        except Exception as e:
            self.logger.log("error", f"Context formatting failed: {e}")
            return None

    def _format_context(self, context_data: dict) -> str:
        """Format context data into readable output based on mode."""
        # Use compact or full formatter based on mode
        if USE_COMPACT_MODE:
            from providers.simple_formatter import SimpleFormatter

            return SimpleFormatter.format(self._normalize_context_data(context_data))
        else:
            # Original verbose formatting
            return self._format_context_verbose(context_data)

    def _normalize_context_data(self, context_data: dict) -> dict:
        """Normalize context data keys for formatter compatibility."""
        normalized = {}

        # Agent messages (always include)
        if "agentmessage" in context_data:
            normalized["agent_role"] = context_data["agentmessage"]

        # Git context (lazy or full)
        if "lazygitcontext" in context_data:
            normalized["git"] = context_data["lazygitcontext"]
        elif "gitcontext" in context_data:
            git_data = context_data["gitcontext"]
            normalized["git"] = {
                "branch": git_data.get("current_branch"),
                "changes": git_data.get("changes", []),
                "recent_commits": git_data.get("recent_commits", []),
                "mode": "full",
            }

        # MCP context (conditional or full)
        if "conditionalmcp" in context_data:
            normalized["mcp"] = context_data["conditionalmcp"]
        elif "mcpcontext" in context_data:
            normalized["mcp"] = {**context_data["mcpcontext"], "mode": "full"}

        # Environment context (compact or full)
        if "compactenvironment" in context_data:
            normalized["environment"] = context_data["compactenvironment"]
        elif "developmentcontext" in context_data:
            normalized["environment"] = context_data["developmentcontext"]

        # Issues context (always include if present)
        if "issuecontext" in context_data:
            normalized["issues"] = context_data["issuecontext"]

        # Session info (construct from available data)
        normalized["session"] = {
            "id": "current"  # Will be populated by hook system
        }

        return normalized

    def _format_context_verbose(self, context_data: dict) -> str:
        """Original verbose formatting logic."""
        output_parts = []

        # PRIORITY: Agent initialization messages (most important)
        if "agentmessage" in context_data:
            agent = context_data["agentmessage"]
            if agent.get("initialization_message"):
                # Add the initialization message as the FIRST thing
                output_parts.append(agent["initialization_message"])
            if agent.get("role_description"):
                output_parts.append(agent["role_description"])

        # Git context
        if "gitcontext" in context_data:
            git = context_data["gitcontext"]
            git_parts = [
                f"📁 Git Status: Branch '{git.get('current_branch', 'unknown')}'"
            ]

            if git.get("uncommitted_changes", 0) > 0:
                git_parts.append(f"⚠️  {git['uncommitted_changes']} uncommitted changes")
            else:
                git_parts.append("✅ Working directory clean")

            output_parts.append("\n".join(git_parts))

        # MCP context with project/branch IDs
        if "mcpcontext" in context_data:
            mcp = context_data["mcpcontext"]
            mcp_parts = []

            # Display MCP server URL first for verification
            if mcp.get("mcp_server_url"):
                mcp_parts.append(f"🌐 MCP Server: {mcp['mcp_server_url']}")

            # Project information with ID
            if mcp.get("project_info"):
                project = mcp["project_info"]
                if project.get("found"):
                    mcp_parts.append(
                        f"📁 Git project: Project '{project['project_name']}' : '{project['project_id']}'"
                    )
                else:
                    mcp_parts.append(
                        f"⚠️ Project '{project['project_name']}' not found in MCP - Master Orchestrator should create it"
                    )

            # Branch information with ID
            if mcp.get("branch_info"):
                branch = mcp["branch_info"]
                # Defensive type check: ensure branch is a dict before accessing with .get()
                if not isinstance(branch, dict):
                    mcp_parts.append(
                        "⚠️ Error fetching branch info: Invalid data type returned"
                    )
                elif branch.get("error"):
                    # Error occurred while fetching branch info
                    mcp_parts.append(f"⚠️ Error fetching branch info: {branch['error']}")
                elif branch.get("found"):
                    # Branch found in MCP
                    mcp_parts.append(
                        f"🌿 Git Branch: '{branch['branch_name']}' : '{branch['git_branch_id']}'"
                    )
                else:
                    # Branch exists in git but not in MCP (normal for new branches)
                    mcp_parts.append(
                        f"📝 Git Branch: '{branch['branch_name']}' (not yet registered in MCP)"
                    )

            # Active task information
            if mcp.get("active_tasks"):
                active_tasks = mcp["active_tasks"]
                if len(active_tasks) == 0:
                    mcp_parts.append("📋 No active tasks")
                elif len(active_tasks) == 1:
                    task = active_tasks[0]
                    task_title = task.get("title", "Unknown task")
                    task_id = task.get("id", "unknown-id")
                    mcp_parts.append(f"📋 Active Task: '{task_title}' : '{task_id}'")
                else:
                    mcp_parts.append(f"📋 Active Tasks ({len(active_tasks)}):")
                    for task in active_tasks:
                        task_title = task.get("title", "Unknown task")
                        task_id = task.get("id", "unknown-id")
                        mcp_parts.append(f"   • '{task_title}' : '{task_id}'")
            else:
                mcp_parts.append("📋 No active tasks")

            # Pending task information
            if mcp.get("pending_tasks"):
                task_count = len(mcp["pending_tasks"])
                mcp_parts.append(f"📝 {task_count} pending tasks")

            if mcp.get("next_task"):
                next_task = mcp["next_task"]
                task_title = next_task.get("title", "Unknown task")
                mcp_parts.append(f"   • Next: {task_title}")

            if mcp_parts:
                output_parts.append("\n".join(mcp_parts))

        # Development context - Multi-project architecture
        if "developmentcontext" in context_data:
            dev = context_data["developmentcontext"]
            dev_parts = []

            # Frontend section
            if dev.get("frontend"):
                frontend = dev["frontend"]
                frontend_parts = [f"📦 Frontend ({frontend['path']})"]

                # Build framework line
                framework_line = "   • Framework: "
                framework_parts = []
                if frontend.get("react_version"):
                    framework_parts.append(f"React {frontend['react_version']}")
                if frontend.get("typescript_version"):
                    framework_parts.append(
                        f"TypeScript {frontend['typescript_version']}"
                    )
                if framework_parts:
                    framework_line += " + ".join(framework_parts)
                    frontend_parts.append(framework_line)

                # Build tool
                if frontend.get("vite_version"):
                    frontend_parts.append(
                        f"   • Build: Vite {frontend['vite_version']}"
                    )

                # UI frameworks
                if frontend.get("ui_frameworks"):
                    ui = ", ".join(frontend["ui_frameworks"])
                    frontend_parts.append(f"   • UI: {ui}")

                # Key files
                if frontend.get("key_files"):
                    files = ", ".join(frontend["key_files"])
                    frontend_parts.append(f"   • Key files: {files}")

                # Port
                if frontend.get("port"):
                    frontend_parts.append(f"   • Port: {frontend['port']}")

                dev_parts.append("\n".join(frontend_parts))

            # Backend section
            if dev.get("backend"):
                backend = dev["backend"]
                backend_parts = [f"🐍 Backend ({backend['path']})"]

                # Frameworks
                if backend.get("frameworks"):
                    frameworks = " + ".join(backend["frameworks"])
                    backend_parts.append(f"   • Framework: {frameworks}")

                # Architecture
                if backend.get("architecture"):
                    backend_parts.append(
                        f"   • Architecture: {backend['architecture']}"
                    )

                # Language
                if backend.get("language"):
                    backend_parts.append(f"   • Language: {backend['language']}")

                # ORM
                if backend.get("orm"):
                    backend_parts.append(f"   • ORM: {backend['orm']}")

                # Key files
                if backend.get("key_files"):
                    files = ", ".join(backend["key_files"])
                    backend_parts.append(f"   • Key files: {files}")

                # Port
                if backend.get("port"):
                    backend_parts.append(f"   • Port: {backend['port']}")

                dev_parts.append("\n".join(backend_parts))

            # Hook system section
            if dev.get("hooks"):
                hooks = dev["hooks"]
                hook_parts = [f"🪝 Hook System ({hooks['path']})"]

                # Type
                if hooks.get("type"):
                    hook_parts.append(f"   • Type: {hooks['type']}")

                # Features
                if hooks.get("features"):
                    for feature in hooks["features"]:
                        if "File system" in feature:
                            hook_parts.append(f"   • Pre-tool: {feature}")
                        elif "Documentation" in feature:
                            hook_parts.append(f"   • Post-tool: {feature}")
                        elif "tracking" in feature:
                            hook_parts.append(f"   • Session: {feature}")

                # Key files
                if hooks.get("key_files"):
                    files = ", ".join(hooks["key_files"])
                    hook_parts.append(f"   • Key files: {files}")

                dev_parts.append("\n".join(hook_parts))

            # Infrastructure section
            if dev.get("infrastructure"):
                infra = dev["infrastructure"]
                infra_parts = ["🐳 Infrastructure:"]

                # Container
                if infra.get("container"):
                    infra_parts.append(f"   • Container: {infra['container']}")

                # Database
                if infra.get("database"):
                    infra_parts.append(f"   • Database: {infra['database']}")

                # Authentication
                if infra.get("auth"):
                    infra_parts.append(f"   • Auth: {infra['auth']}")

                # Config
                if infra.get("config"):
                    infra_parts.append(f"   • Config: {infra['config']}")

                dev_parts.append("\n".join(infra_parts))

            # Output all development sections
            if dev_parts:
                output_parts.append(
                    "🔧 Development Environment:\n\n" + "\n\n".join(dev_parts)
                )

        # Issues context
        if "issuecontext" in context_data:
            issues = context_data["issuecontext"]
            if issues.get("recent_issues"):
                issue_count = len(issues["recent_issues"])
                output_parts.append(f"⚠️  {issue_count} recent issues logged")

        return "\n\n".join(output_parts)


# ============================================================================
# Component Factory
# ============================================================================


class ComponentFactory:
    """Factory for creating session start components."""

    @staticmethod
    def create_logger(log_dir: Path, log_name: str = "session_start") -> Logger:
        """Create a logger instance."""
        return FileLogger(log_dir, log_name)

    @staticmethod
    def create_config_loader(config_dir: Path) -> ConfigurationLoader:
        """Create a configuration loader instance."""
        return ConfigurationLoader(config_dir)

    @staticmethod
    def create_context_providers(
        config_loader: ConfigurationLoader,
    ) -> list[ContextProvider]:
        """Create all context providers based on CONTEXT_MODE."""
        # Always include agent message provider (critical for agent roles)
        providers = [AgentMessageProvider(config_loader)]

        if USE_COMPACT_MODE:
            # Import compact providers
            from providers.compact_env import CompactEnvironmentProvider
            from providers.conditional_mcp import ConditionalMCPProvider
            from providers.lazy_git import LazyGitContextProvider

            providers.extend(
                [
                    LazyGitContextProvider(),  # Saves ~2,850 tokens
                    ConditionalMCPProvider(),  # Saves ~2,400 tokens
                    CompactEnvironmentProvider(),  # Saves ~1,900 tokens
                    IssueContextProvider(),  # Keep issues (low token cost)
                ]
            )
        else:
            # Use original verbose providers
            providers.extend(
                [
                    GitContextProvider(),
                    MCPContextProvider(),
                    DevelopmentContextProvider(),
                    IssueContextProvider(),
                ]
            )

        return providers

    @staticmethod
    def create_processors(
        context_providers: list[ContextProvider], logger: Logger
    ) -> list[SessionProcessor]:
        """Create all session processors."""
        return [
            SessionStartProcessor(logger),
            ContextFormatterProcessor(context_providers, logger),
        ]


# ============================================================================
# Claude Session Cleanup
# ============================================================================


class ClaudeSessionCleanup:
    """Manages cleanup of idle Claude sessions to prevent memory buildup."""

    def __init__(self, logger=None):
        """Initialize the cleanup manager."""
        self.logger = logger
        # Configuration from environment or defaults
        self.idle_threshold_hours = float(os.getenv("CLAUDE_IDLE_THRESHOLD_HOURS", "2"))
        self.cpu_threshold = float(os.getenv("CLAUDE_CPU_THRESHOLD", "0.5"))
        self.cleanup_enabled = (
            os.getenv("CLAUDE_AUTO_CLEANUP", "true").lower() == "true"
        )

    def find_claude_processes(self) -> list[dict[str, Any]]:
        """Find all Claude processes running on the system."""
        claude_processes = []
        current_pid = os.getpid()

        try:
            for proc in psutil.process_iter(
                ["pid", "name", "cmdline", "create_time", "cpu_percent"]
            ):
                try:
                    # Check if this is a Claude process
                    cmdline = proc.info.get("cmdline", [])
                    if cmdline and any("claude" in str(cmd).lower() for cmd in cmdline):
                        # Skip the current process
                        if proc.info["pid"] != current_pid:
                            claude_processes.append(
                                {
                                    "pid": proc.info["pid"],
                                    "cmdline": " ".join(cmdline),
                                    "create_time": proc.info["create_time"],
                                    "cpu_percent": proc.cpu_percent(interval=0.1),
                                    "age_hours": (
                                        time.time() - proc.info["create_time"]
                                    )
                                    / 3600,
                                }
                            )
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

        except Exception as e:
            if self.logger:
                self.logger.log("error", f"Error finding Claude processes: {e}")

        return claude_processes

    def is_process_idle(self, process: dict[str, Any]) -> bool:
        """Determine if a process is idle based on age and CPU usage."""
        # Process is idle if it's older than threshold AND has low CPU usage
        is_old = process["age_hours"] > self.idle_threshold_hours
        is_low_cpu = process["cpu_percent"] < self.cpu_threshold
        return is_old and is_low_cpu

    def cleanup_idle_sessions(self) -> dict[str, Any]:
        """Find and kill idle Claude sessions."""
        if not self.cleanup_enabled:
            return {"enabled": False, "message": "Auto-cleanup is disabled"}

        results = {"found": 0, "idle": 0, "killed": 0, "errors": [], "details": []}

        try:
            processes = self.find_claude_processes()
            results["found"] = len(processes)

            for proc_info in processes:
                if self.is_process_idle(proc_info):
                    results["idle"] += 1

                    # Attempt to kill the idle process
                    try:
                        process = psutil.Process(proc_info["pid"])
                        process.terminate()

                        # Give it a moment to terminate gracefully
                        time.sleep(0.5)

                        # Force kill if still running
                        if process.is_running():
                            process.kill()

                        results["killed"] += 1
                        results["details"].append(
                            {
                                "pid": proc_info["pid"],
                                "age_hours": round(proc_info["age_hours"], 2),
                                "cpu_percent": round(proc_info["cpu_percent"], 2),
                                "status": "killed",
                            }
                        )

                        if self.logger:
                            self.logger.log(
                                "info",
                                f"Killed idle Claude session (PID: {proc_info['pid']}, "
                                f"Age: {proc_info['age_hours']:.1f}h, CPU: {proc_info['cpu_percent']:.1f}%)",
                            )

                    except Exception as e:
                        results["errors"].append(
                            f"Failed to kill PID {proc_info['pid']}: {e}"
                        )
                        if self.logger:
                            self.logger.log(
                                "error", f"Failed to kill PID {proc_info['pid']}: {e}"
                            )
                else:
                    # Log active sessions
                    results["details"].append(
                        {
                            "pid": proc_info["pid"],
                            "age_hours": round(proc_info["age_hours"], 2),
                            "cpu_percent": round(proc_info["cpu_percent"], 2),
                            "status": "active",
                        }
                    )

        except Exception as e:
            results["errors"].append(f"Cleanup error: {e}")
            if self.logger:
                self.logger.log("error", f"Session cleanup failed: {e}")

        return results

    def format_cleanup_message(self, results: dict[str, Any]) -> str:
        """Format cleanup results for display."""
        if not results.get("enabled", True):
            return ""

        if results["killed"] > 0:
            msg = f"🧹 Cleaned up {results['killed']} idle Claude session(s)\n"
            for detail in results["details"]:
                if detail["status"] == "killed":
                    msg += f"   • Killed PID {detail['pid']} (idle for {detail['age_hours']:.1f}h)\n"
            return msg.rstrip()
        elif results["found"] > 0:
            active_count = results["found"] - results["idle"]
            if active_count > 1:
                return f"ℹ️  {active_count} active Claude session(s) running"

        return ""


# ============================================================================
# Main Hook Class
# ============================================================================


class SessionStartHook:
    """Main session start hook with clean architecture."""

    def __init__(self):
        """Initialize the hook with all components."""
        # Get paths
        from utils.env_loader import get_ai_data_path

        self.log_dir = get_ai_data_path() / "claude-hooks"
        self.config_dir = Path(__file__).parent / "config"

        # Create components using factory
        self.factory = ComponentFactory()
        self.logger = self.factory.create_logger(self.log_dir)
        self.config_loader = self.factory.create_config_loader(self.config_dir)

        # Initialize components with config loader
        self.context_providers: list[ContextProvider] = (
            self.factory.create_context_providers(self.config_loader)
        )
        self.processors: list[SessionProcessor] = self.factory.create_processors(
            self.context_providers, self.logger
        )

    def execute(self, input_data: dict[str, Any]) -> int:
        """Execute the session start hook."""
        # Log the execution
        self.logger.log("info", "Processing session start")

        # Run Claude session cleanup first
        try:
            cleanup_manager = ClaudeSessionCleanup(self.logger)
            cleanup_results = cleanup_manager.cleanup_idle_sessions()
            cleanup_message = cleanup_manager.format_cleanup_message(cleanup_results)
            if cleanup_message:
                print(f"\n{cleanup_message}\n")
                self.logger.log("info", f"Session cleanup: {cleanup_results}")
        except Exception as e:
            self.logger.log("error", f"Session cleanup failed: {e}")

        # Process through all processors
        output_parts = []
        for processor in self.processors:
            try:
                output = processor.process(input_data)
                if output and output.strip():
                    output_parts.append(output)
            except Exception as e:
                self.logger.log(
                    "error", f"Processor {processor.__class__.__name__} failed: {e}"
                )

        # Output combined results
        if output_parts:
            combined_output = "\n\n".join(output_parts)
            print(combined_output)
            sys.stdout.flush()

        self.logger.log("info", "Session start processing completed")
        return 0


# ============================================================================
# Backward Compatibility Functions (for test compatibility)
# ============================================================================


def log_session_start(input_data: dict) -> None:
    """Backward compatibility wrapper for log_session_start."""
    try:
        log_dir = get_ai_data_path()
        log_path = log_dir / "session_start.json"

        # Ensure directory exists
        log_dir.mkdir(parents=True, exist_ok=True)

        # Load existing data
        log_data = []
        if log_path.exists():
            try:
                with open(log_path) as f:
                    log_data = json.load(f)
            except:
                log_data = []

        # Append new data directly (for test compatibility)
        log_data.append(input_data)

        # Save updated data
        with open(log_path, "w") as f:
            json.dump(log_data, f, indent=2)

    except Exception:
        # Fail silently for compatibility
        pass


def get_git_status() -> tuple:
    """Backward compatibility wrapper for git status."""
    try:
        git_provider = GitContextProvider()
        context = git_provider.get_context({})
        if context and "error" not in context:
            branch = context.get("current_branch", None)
            changes = context.get("uncommitted_changes", None)
            # Map "unknown" to None for backward compatibility (indicates git command failure)
            if branch == "unknown":
                branch = None
                changes = None  # Also set changes to None when git commands fail
            return branch, changes
        else:
            return None, None
    except Exception:
        return None, None


def get_recent_issues() -> str | None:
    """Backward compatibility wrapper for recent issues."""
    try:
        # Check if gh CLI is available
        which_result = subprocess.run(
            ["which", "gh"], capture_output=True, text=True, timeout=5
        )

        if which_result.returncode != 0:
            return None

        # Get recent issues using gh CLI
        issues_result = subprocess.run(
            ["gh", "issue", "list", "--state=open", "--limit=10"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if issues_result.returncode == 0 and issues_result.stdout.strip():
            # Return the raw output, removing trailing newline for consistency
            return issues_result.stdout.rstrip("\n")
        else:
            return None

    except Exception:
        return None


def query_mcp_pending_tasks() -> list | None:
    """Backward compatibility wrapper for pending tasks."""
    try:
        # Direct server query without cache
        client = get_default_client()
        if client:
            server_tasks = client.query_pending_tasks(limit=5)
            if server_tasks:
                return server_tasks

        return []
    except Exception:
        return None


def query_mcp_next_task(branch_id: str | None = None) -> dict | None:
    """Backward compatibility wrapper for next task."""
    try:
        if not branch_id:
            return None

        # Direct server query without cache
        client = get_default_client()
        if client:
            next_task = client.get_next_recommended_task(branch_id)
            if next_task:
                return next_task

        return None
    except Exception:
        return None


def get_git_branch_context() -> dict | None:
    """Backward compatibility wrapper for git branch context."""
    try:
        # Get git context from subprocess calls
        # Get current branch
        branch_result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        current_branch = (
            branch_result.stdout.strip() if branch_result.returncode == 0 else "unknown"
        )

        # Get uncommitted changes count
        status_result = subprocess.run(
            ["git", "status", "--porcelain"], capture_output=True, text=True, timeout=5
        )
        changes = []
        if status_result.returncode == 0 and status_result.stdout.strip():
            changes = status_result.stdout.strip().split("\n")

        # Get recent commits
        log_result = subprocess.run(
            ["git", "log", "--oneline", "-5"], capture_output=True, text=True, timeout=5
        )
        recent_commits = []
        if log_result.returncode == 0 and log_result.stdout.strip():
            recent_commits = log_result.stdout.strip().split("\n")

        result = {
            "branch": current_branch,
            "uncommitted_changes": len(changes),
            "recent_commits": recent_commits,
            "git_branch_id": None,  # Test expects this to be None
        }

        return result

    except Exception:
        return None


def format_mcp_context(context_data: dict) -> str:
    """Backward compatibility wrapper for MCP context formatting."""
    try:
        if not context_data:
            return ""
        return json.dumps(context_data, indent=2)
    except Exception:
        return ""


def load_development_context(trigger: str = "startup") -> str:
    """Backward compatibility wrapper for development context.

    Args:
        trigger: Event trigger type (kept for backward compatibility)
    """
    # Note: trigger parameter is kept for backward compatibility but not used
    _ = trigger  # Mark as intentionally unused
    try:
        # Create a factory and get context
        factory = ComponentFactory()
        config_loader = factory.create_config_loader(Path(__file__).parent / "config")
        providers = factory.create_context_providers(config_loader)

        combined_context = {}
        for provider in providers:
            try:
                context = provider.get_context({})
                if context:
                    combined_context.update(context)
            except Exception:
                continue

        # Format as expected by tests
        git_status = "✅" if combined_context.get("git_info") else "❌"
        mcp_tasks = len(combined_context.get("pending_tasks", []))

        formatted_output = f"""🚀 INITIALIZATION REQUIRED
⚠️ **MCP Status:** Server unavailable or no active tasks
--- Context Generation Stats ---
MCP tasks loaded: {mcp_tasks}
Git context: {git_status}
"""
        return formatted_output
    except Exception:
        return "🚀 INITIALIZATION REQUIRED\n⚠️ **MCP Status:** Server unavailable or no active tasks\n--- Context Generation Stats ---\nMCP tasks loaded: 0\nGit context: ❌"


def get_ai_data_path() -> Path:
    """Backward compatibility wrapper for get_ai_data_path."""
    try:
        from utils.env_loader import get_ai_data_path as real_get_ai_data_path

        return real_get_ai_data_path()
    except Exception:
        # Fallback: Use absolute path relative to this file's location
        # .claude/hooks/session_start.py -> project_root is 2 levels up
        return Path(__file__).parent.parent.parent / "logs"


def get_default_client():
    """Backward compatibility wrapper for default client."""
    try:
        return None
    except Exception:
        return None


# ============================================================================
# Main Entry Point
# ============================================================================


def main():
    """Main entry point for the hook."""
    # CRITICAL: Print output IMMEDIATELY before any processing
    # This is required for Claude Code v2.0.29+ to display SessionStart output
    print("🚀 Session loaded", flush=True)

    parser = argparse.ArgumentParser(description="Session start hook")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--log-only", action="store_true", help="Only log, no output")
    args = parser.parse_args()

    try:
        # CRITICAL: Validate configuration files before any hook execution
        try:
            from utils.config_validator import validate_configuration

            if not validate_configuration():
                # Configuration validation failed, error already printed to stderr
                sys.exit(1)
        except ImportError:
            # If validator module not found, print basic error
            print("\n❌ ERROR: Configuration validator not found!", file=sys.stderr)
            print(
                "Please ensure .claude/hooks/utils/config_validator.py exists.",
                file=sys.stderr,
            )
            sys.exit(1)
        except Exception as e:
            # Any other validation error
            print(f"\n❌ ERROR: Configuration validation failed: {e}", file=sys.stderr)
            sys.exit(1)

        # Read JSON input from stdin
        input_data = {}
        if not sys.stdin.isatty():
            try:
                input_data = json.load(sys.stdin)
            except json.JSONDecodeError:
                input_data = {}

        # Create and execute hook
        hook = SessionStartHook()

        if args.log_only:
            hook.logger.log("info", "Session start logged only", input_data)
        else:
            exit_code = hook.execute(input_data)
            sys.exit(exit_code)

        sys.exit(0)

    except Exception as e:
        # Log error but exit cleanly
        try:
            from utils.env_loader import get_ai_data_path

            log_dir = get_ai_data_path()
            error_log = log_dir / "session_start_errors.log"
            with open(error_log, "a") as f:
                f.write(f"{datetime.now().isoformat()} - Fatal error: {e}\n")
        except:
            pass
        sys.exit(0)


if __name__ == "__main__":
    main()
