#!/usr/bin/env python3
"""
MCP Post-Action Hints - Provides reminders AFTER MCP operations are completed.

This module generates contextual reminders based on what was just done,
helping AI agents remember next steps and best practices.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any

class MCPPostActionHints:
    """Generate post-action reminders for MCP operations."""
    
    def __init__(self):
        """Initialize the post-action hint system."""
        self.task_tracking_file = Path.cwd() / '.claude' / 'hooks' / 'data' / 'task_tracking.json'
        self.task_tracking_file.parent.mkdir(parents=True, exist_ok=True)
        self.load_task_tracking()
    
    def load_task_tracking(self):
        """Load task tracking data."""
        if self.task_tracking_file.exists():
            try:
                with open(self.task_tracking_file, 'r') as f:
                    self.task_tracking = json.load(f)
            except:
                self.task_tracking = {}
        else:
            self.task_tracking = {}
    
    def save_task_tracking(self):
        """Save task tracking data."""
        with open(self.task_tracking_file, 'w') as f:
            json.dump(self.task_tracking, f, indent=2)
    
    def generate_hints(self, tool_name: str, tool_input: Dict[str, Any], result: Any = None) -> Optional[str]:
        """
        Generate post-action hints based on what was just done.
        
        Args:
            tool_name: The MCP tool that was just used
            tool_input: Parameters that were passed to the tool
            result: The result returned by the tool (if available)
            
        Returns:
            Optional[str]: Formatted reminder message or None
        """
        hints = []
        
        # Extract action from tool_input
        action = tool_input.get('action', 'default')
        
        # Check if operation was successful or failed
        is_success = True
        error_message = None
        if result and isinstance(result, dict):
            is_success = result.get('success', True)
            if not is_success:
                error_message = result.get('error', {}).get('message', 'Unknown error')
                # Don't provide hints for failed operations
                return None
        
        # Only generate hints for successful operations
        if tool_name == "mcp__agenthub_http__manage_task":
            hints.extend(self._task_post_hints(action, tool_input, result))
        elif tool_name == "mcp__agenthub_http__manage_subtask":
            hints.extend(self._subtask_post_hints(action, tool_input, result))
        elif tool_name == "mcp__agenthub_http__manage_context":
            hints.extend(self._context_post_hints(action, tool_input, result))
        elif tool_name == "mcp__agenthub_http__manage_project":
            hints.extend(self._project_post_hints(action, tool_input, result))
        elif tool_name == "mcp__agenthub_http__manage_git_branch":
            hints.extend(self._branch_post_hints(action, tool_input, result))
        elif tool_name == "mcp__agenthub_http__call_agent":
            hints.extend(self._agent_post_hints(tool_input, result))
        
        # Format and return hints if any
        if hints:
            return self._format_hints(hints, tool_name, action)
        
        return None
    
    def _task_post_hints(self, action: str, tool_input: Dict, result: Any) -> list:
        """Generate post-action hints for task operations."""
        hints = []
        
        if action == "create":
            # Track the created task
            if result and isinstance(result, dict):
                task_id = result.get('task', {}).get('id')
                if task_id:
                    self.task_tracking[task_id] = {
                        'created_at': datetime.now().isoformat(),
                        'title': tool_input.get('title'),
                        'has_been_delegated': False,
                        'has_been_updated': False
                    }
                    self.save_task_tracking()
            
            # Reminders after task creation
            if not tool_input.get('details'):
                hints.append("⚠️ MISSING DETAILS: Consider updating task with full requirements")
            
            if not tool_input.get('assignees'):
                hints.append("🚨 NO ASSIGNEES: Add assignees before delegating")
            else:
                hints.append("✅ NEXT STEP: Delegate to agent using Task tool with task_id only")
            
            # Check if task seems complex
            title = tool_input.get('title', '').lower()
            if any(word in title for word in ['implement', 'build', 'create', 'system']):
                hints.append("💡 SUGGESTION: Create subtasks for better tracking")
        
        elif action == "update":
            task_id = tool_input.get('task_id')
            if task_id and task_id in self.task_tracking:
                self.task_tracking[task_id]['has_been_updated'] = True
                self.task_tracking[task_id]['last_update'] = datetime.now().isoformat()
                self.save_task_tracking()
            
            # Reminders after update
            if not tool_input.get('progress_notes') and not tool_input.get('details'):
                hints.append("📝 TIP: Next update should include progress_notes")
            
            if tool_input.get('status') == 'blocked':
                hints.append("🚨 BLOCKED: Consider creating debug task or asking for help")
            
            hints.append("⏰ REMINDER: Continue updating every 25% progress")
        
        elif action == "complete":
            task_id = tool_input.get('task_id')
            if task_id and task_id in self.task_tracking:
                if not self.task_tracking[task_id].get('has_been_updated'):
                    hints.append("⚠️ PATTERN: Task completed without any progress updates")
            
            # Reminders after completion
            if not tool_input.get('completion_summary'):
                hints.append("📝 MISSING: Completion summary should be added for documentation")
            
            if not tool_input.get('testing_notes'):
                hints.append("🧪 MISSING: Testing notes help future debugging")
            
            hints.append("💾 NEXT: Update context with learnings from this task")
            hints.append("🎯 CONTINUE: Use 'next' action to find next task to work on")
        
        elif action == "get" or action == "list":
            hints.append("📋 REVIEW: Check task status and plan next actions")
        
        elif action == "next":
            hints.append("🎯 TASK SELECTED: Remember to update status when starting work")
        
        return hints
    
    def _subtask_post_hints(self, action: str, tool_input: Dict, result: Any) -> list:
        """Generate post-action hints for subtask operations."""
        hints = []
        
        if action == "create":
            if not tool_input.get('assignees'):
                hints.append("💡 INFO: Subtask inherited parent's assignees")
            hints.append("📊 TIP: Use progress_percentage in updates for auto status")
        
        elif action == "update":
            progress = tool_input.get('progress_percentage')
            if progress is not None:
                if progress < 100:
                    hints.append(f"📈 PROGRESS: {progress}% complete - keep updating")
                else:
                    hints.append("✅ 100% COMPLETE: Remember to formally complete subtask")
        
        elif action == "complete":
            if tool_input.get('insights_found'):
                hints.append("💡 GREAT: Insights documented for future reference")
            hints.append("🔄 CHECK: Review if parent task needs updating")
        
        return hints
    
    def _context_post_hints(self, action: str, tool_input: Dict, result: Any) -> list:
        """Generate post-action hints for context operations."""
        hints = []
        
        if action == "update":
            level = tool_input.get('level')
            if level == 'task':
                hints.append("📌 UPDATED: Task context preserved for future reference")
            elif level == 'branch':
                hints.append("🌿 BRANCH CONTEXT: All tasks in branch affected")
            elif level == 'project':
                hints.append("🏗️ PROJECT CONTEXT: Shared across all branches")
            
            if tool_input.get('propagate_changes'):
                hints.append("📡 PROPAGATED: Changes cascaded to child contexts")
        
        elif action == "add_insight":
            hints.append("💡 INSIGHT ADDED: Knowledge preserved for team")
            hints.append("🔄 CONSIDER: Share important insights at higher context levels")
        
        return hints
    
    def _project_post_hints(self, action: str, tool_input: Dict, result: Any) -> list:
        """Generate post-action hints for project operations."""
        hints = []
        
        if action == "create":
            hints.append("🏗️ PROJECT CREATED: Next, create git branches for features")
            hints.append("📋 SETUP: Create initial tasks for project setup")
        
        elif action == "project_health_check":
            hints.append("🏥 HEALTH CHECKED: Address any issues before continuing")
            hints.append("📊 METRICS: Use health data to prioritize work")
        
        return hints
    
    def _branch_post_hints(self, action: str, tool_input: Dict, result: Any) -> list:
        """Generate post-action hints for git branch operations."""
        hints = []
        
        if action == "create":
            hints.append("🌿 BRANCH CREATED: Create tasks for this branch's work")
            hints.append("🤖 ASSIGN: Consider assigning specialized agents")
        
        elif action == "assign_agent":
            hints.append("✅ AGENT ASSIGNED: Agent can now work on branch tasks")
        
        return hints
    
    def _agent_post_hints(self, tool_input: Dict, result: Any) -> list:
        """Generate post-action hints for agent operations."""
        hints = []
        
        agent_name = tool_input.get('name_agent')
        if agent_name == 'master-orchestrator-agent':
            hints.append("🎯 ORCHESTRATOR LOADED: You can now coordinate all work")
            hints.append("📋 START: List existing tasks or create new ones")
        else:
            hints.append(f"🤖 {agent_name.upper()} LOADED: Follow agent's specialized workflow")
        
        hints.append("⚠️ REMEMBER: This was a one-time load - don't call again this session")
        
        return hints
    
    def _format_hints(self, hints: list, tool_name: str, action: str) -> str:
        """Format hints into a system reminder."""
        # Create appropriate header
        headers = {
            ('manage_task', 'create'): "📋 TASK CREATED - NEXT STEPS",
            ('manage_task', 'update'): "📊 TASK UPDATED - REMINDERS",
            ('manage_task', 'complete'): "✅ TASK COMPLETED - FOLLOW-UP",
            ('manage_task', 'next'): "🎯 NEXT TASK - GETTING STARTED",
            ('manage_subtask', 'create'): "📌 SUBTASK CREATED - TIPS",
            ('manage_subtask', 'complete'): "✔️ SUBTASK COMPLETED - NEXT",
            ('manage_context', 'update'): "🔄 CONTEXT UPDATED - INFO",
            ('manage_project', 'create'): "🏗️ PROJECT CREATED - SETUP",
            ('manage_git_branch', 'create'): "🌿 BRANCH CREATED - NEXT",
            ('call_agent', 'default'): "🤖 AGENT LOADED - READY"
        }
        
        # Extract base tool name
        base_tool = tool_name.split('__')[-1]
        header = headers.get((base_tool, action), f"💡 {action.upper()} COMPLETE - REMINDERS")
        
        # Build formatted message
        message = f"<system-reminder>\n{header}:\n"
        for hint in hints[:5]:  # Limit to 5 hints
            message += f"{hint}\n"
        message += "</system-reminder>"
        
        return message


def generate_post_action_hints(tool_name: str, tool_input: Dict, result: Any = None) -> Optional[str]:
    """
    Main entry point for post-action hint generation.
    
    Args:
        tool_name: Name of the MCP tool that was executed
        tool_input: Parameters that were passed to the tool
        result: Result returned by the tool (if available)
        
    Returns:
        Optional[str]: Formatted reminder message or None
    """
    if not tool_name.startswith('mcp__agenthub_http'):
        return None
    
    hint_generator = MCPPostActionHints()
    return hint_generator.generate_hints(tool_name, tool_input, result)


if __name__ == "__main__":
    # Test cases
    test_cases = [
        {
            "tool_name": "mcp__agenthub_http__manage_task",
            "tool_input": {
                "action": "create",
                "title": "Implement authentication",
                "assignees": "@coding-agent"
            },
            "result": {"task": {"id": "task_123"}}
        },
        {
            "tool_name": "mcp__agenthub_http__manage_task",
            "tool_input": {
                "action": "complete",
                "task_id": "task_123",
                "completion_summary": "Done"
            }
        },
        {
            "tool_name": "mcp__agenthub_http__call_agent",
            "tool_input": {
                "name_agent": "master-orchestrator-agent"
            }
        }
    ]
    
    for test in test_cases:
        print(f"\nTesting: {test['tool_name']} - {test['tool_input'].get('action', 'default')}")
        print("-" * 60)
        hint = generate_post_action_hints(
            test['tool_name'], 
            test['tool_input'], 
            test.get('result')
        )
        if hint:
            print(hint)