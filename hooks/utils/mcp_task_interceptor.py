#!/usr/bin/env python3
"""
MCP Task Interceptor
Automatically tracks MCP task operations and agent state changes
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

# Import task tracker
from .task_tracker import track_task_from_mcp
# Import agent state manager
from .agent_state_manager import set_current_agent

logger = logging.getLogger(__name__)


class MCPTaskInterceptor:
    """Intercepts MCP task operations for automatic tracking."""

    def __init__(self):
        # Use correct path: .claude/data/task_tracking
        self.data_dir = Path(__file__).parent.parent.parent / "data" / "task_tracking"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.data_dir / "mcp_task_operations.json"

    def intercept_task_operation(self, tool_name: str, parameters: Dict[str, Any],
                                 session_id: str = None) -> bool:
        """
        Intercept MCP task operations and track them.

        Args:
            tool_name: Name of the tool being called
            parameters: Parameters passed to the tool
            session_id: Current session ID

        Returns:
            True if operation was tracked, False otherwise
        """
        # Check if this is a call_agent operation
        if tool_name == "mcp__agenthub_http__call_agent":
            return self._handle_call_agent(parameters, session_id)

        # Check if this is a task management operation
        if tool_name not in ["mcp__agenthub_http__manage_task", "manage_task"]:
            return False

        try:
            action = parameters.get('action', '')

            # Log the operation
            self._log_operation(tool_name, parameters, session_id)

            # Track based on action
            if action == "create":
                # Prepare task data for tracking
                task_data = {
                    'id': parameters.get('task_id') or self._generate_task_id(),
                    'title': parameters.get('title', 'Untitled Task'),
                    'status': parameters.get('status', 'pending'),
                    'assignees': parameters.get('assignees', []),
                    'details': parameters.get('details', ''),
                    'priority': parameters.get('priority', 0)
                }
                track_task_from_mcp("create", task_data, session_id)
                logger.info(f"Tracked new task: {task_data['title']}")
                return True

            elif action == "update":
                task_data = {
                    'id': parameters.get('task_id', ''),
                    'status': parameters.get('status'),
                    'title': parameters.get('title'),
                    'progress_percentage': parameters.get('progress_percentage')
                }
                track_task_from_mcp("update", task_data, session_id)
                logger.info(f"Updated task: {task_data['id']}")
                return True

            elif action == "complete":
                task_data = {
                    'id': parameters.get('task_id', '')
                }
                track_task_from_mcp("complete", task_data, session_id)
                logger.info(f"Completed task: {task_data['id']}")
                return True

            elif action == "delete" or action == "cancel":
                # Also remove from tracking
                task_data = {
                    'id': parameters.get('task_id', '')
                }
                track_task_from_mcp("complete", task_data, session_id)  # Use complete to remove
                logger.info(f"Removed task: {task_data['id']}")
                return True

        except Exception as e:
            logger.error(f"Error intercepting task operation: {e}")
            return False

        return False

    def _log_operation(self, tool_name: str, parameters: Dict[str, Any], session_id: str):
        """Log the operation for debugging and audit."""
        try:
            # Load existing log
            if self.log_file.exists():
                with open(self.log_file, 'r') as f:
                    log_data = json.load(f)
            else:
                log_data = []

            # Add new entry
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'tool_name': tool_name,
                'parameters': parameters,
                'session_id': session_id
            }
            log_data.append(log_entry)

            # Keep only last 500 entries
            if len(log_data) > 500:
                log_data = log_data[-500:]

            # Save log
            with open(self.log_file, 'w') as f:
                json.dump(log_data, f, indent=2, default=str)

        except Exception as e:
            logger.error(f"Error logging operation: {e}")

    def _generate_task_id(self) -> str:
        """Generate a unique task ID if not provided."""
        import uuid
        return str(uuid.uuid4())[:8]

    def _handle_call_agent(self, parameters: Dict[str, Any], session_id: str) -> bool:
        """
        Handle call_agent operation to update active agent.

        Args:
            parameters: Parameters passed to call_agent
            session_id: Current session ID

        Returns:
            True if agent state was updated, False otherwise
        """
        try:
            # Extract agent name from parameters
            agent_name = parameters.get('name_agent', '')
            if not agent_name:
                # Try alternative parameter names
                agent_name = parameters.get('agent_name', parameters.get('agent', ''))

            if agent_name and session_id:
                # Update the current agent state
                set_current_agent(session_id, agent_name)
                logger.info(f"Updated active agent to: {agent_name}")
                return True

        except Exception as e:
            logger.error(f"Error handling call_agent: {e}")

        return False

    def intercept_from_response(self, tool_name: str, response: Any,
                               original_params: Dict[str, Any], session_id: str = None) -> bool:
        """
        Intercept task operations from tool response.

        This is called after the tool execution completes to update tracking
        based on the actual response.
        """
        if tool_name not in ["mcp__agenthub_http__manage_task", "manage_task"]:
            return False

        try:
            # Parse response if it's a string
            if isinstance(response, str):
                try:
                    response = json.loads(response)
                except json.JSONDecodeError:
                    return False

            # Extract task data from response
            if isinstance(response, dict):
                task = response.get('task', response.get('data', {}))

                if task and isinstance(task, dict):
                    action = original_params.get('action', '')

                    # Update tracking with actual data from response
                    task_data = {
                        'id': task.get('id', ''),
                        'title': task.get('title', ''),
                        'status': task.get('status', ''),
                        'assignees': task.get('assignees', []),
                        'details': task.get('details', ''),
                        'priority': task.get('priority', 0)
                    }

                    if action == "create":
                        track_task_from_mcp("create", task_data, session_id)
                    elif action == "update":
                        track_task_from_mcp("update", task_data, session_id)
                    elif action == "complete":
                        track_task_from_mcp("complete", task_data, session_id)

                    return True

        except Exception as e:
            logger.error(f"Error intercepting response: {e}")

        return False


# Singleton instance
_interceptor_instance = None

def get_mcp_interceptor() -> MCPTaskInterceptor:
    """Get or create the MCP task interceptor instance."""
    global _interceptor_instance
    if _interceptor_instance is None:
        _interceptor_instance = MCPTaskInterceptor()
    return _interceptor_instance