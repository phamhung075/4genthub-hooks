#!/usr/bin/env python3
"""
Conditional MCP Provider - Token-optimized MCP context.

Only loads full MCP context if MCP tools were recently used.
Otherwise provides availability check only.
Saves ~2,400 tokens (96% reduction from 2,500 to 100 tokens).

Full details available via /mcp_status slash command.
"""

import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


class ContextProvider(ABC):
    """Base context provider interface."""

    @abstractmethod
    def get_context(self, input_data: dict) -> dict[str, Any] | None:
        """Get context information."""
        pass


class ConditionalMCPProvider(ContextProvider):
    """Only loads MCP if explicitly needed."""

    def get_context(self, input_data: dict) -> dict[str, Any] | None:
        """Check MCP availability without loading full context."""

        # Check if MCP tools were used in recent conversation
        conversation = input_data.get("conversation_history", [])
        mcp_needed = any(
            "mcp__" in str(msg.get("content", ""))
            for msg in conversation[-5:]  # Check last 5 messages
        )

        if not mcp_needed:
            # Just verify connection availability
            try:
                from utils.mcp_client import MCPHTTPClient

                client = MCPHTTPClient()

                # Quick authentication check
                if client.authenticate():
                    return {
                        "status": "ready",
                        "details_available": True,
                        "mode": "compact",
                        "message": "💡 Use /mcp_status for details",
                    }
            except Exception:
                pass

            return {"status": "unavailable", "mode": "compact"}

        # Full MCP context only when tools were recently used
        return self._load_full_mcp_context(input_data)

    def _load_full_mcp_context(self, input_data: dict) -> dict[str, Any]:
        """Load complete MCP context when needed."""
        try:
            from utils.env_loader import get_project_root
            from utils.mcp_client import MCPHTTPClient

            client = MCPHTTPClient()

            if not client.authenticate():
                return {"status": "auth_failed", "mode": "full"}

            project_root = get_project_root()

            # Get project context
            try:
                import subprocess

                remote_result = subprocess.run(
                    ["git", "config", "--get", "remote.origin.url"],
                    capture_output=True,
                    text=True,
                    timeout=2,
                    cwd=project_root,
                )
                remote_url = (
                    remote_result.stdout.strip()
                    if remote_result.returncode == 0
                    else None
                )
            except:
                remote_url = None

            project_info = None
            if remote_url:
                projects = client.list_projects()
                if projects:
                    # Match by name or description
                    project_name = project_root.name
                    project_info = next(
                        (p for p in projects if p.get("name") == project_name), None
                    )

            # Get branch and task info if project found
            branch_info = None
            active_tasks = []

            if project_info:
                try:
                    branch_result = subprocess.run(
                        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                        capture_output=True,
                        text=True,
                        timeout=2,
                        cwd=project_root,
                    )
                    current_branch = (
                        branch_result.stdout.strip()
                        if branch_result.returncode == 0
                        else None
                    )

                    if current_branch:
                        branches = client.list_git_branches(project_info["id"])
                        branch_info = next(
                            (
                                b
                                for b in branches
                                if b.get("git_branch_name") == current_branch
                            ),
                            None,
                        )

                        if branch_info:
                            tasks = client.list_tasks(branch_info["id"])
                            active_tasks = [
                                t
                                for t in tasks
                                if t.get("status") in ["todo", "in_progress"]
                            ]
                except:
                    pass

            return {
                "status": "connected",
                "mode": "full",
                "project": project_info,
                "branch": branch_info,
                "active_tasks": active_tasks,
            }

        except Exception as e:
            return {"status": "error", "mode": "full", "error": str(e)}
