#!/usr/bin/env python3
"""
Context Updater Module for Real-Time Hook Enhancement

This module implements context updates for the post-tool hook, providing
intelligent context change detection, MCP updates, and cache synchronization.

Task ID: de7621a4-df75-4d03-a967-8fb743b455f1 (Phase 2)
Architecture Reference: Real-Time Context Injection System
"""

import os
import json
import re
import time
import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass

# Import MCP client and cache manager
from .mcp_client import OptimizedMCPClient
from .cache_manager import SessionContextCache

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class ContextUpdateConfig:
    """Configuration for context update system."""
    enable_mcp_updates: bool = True
    enable_cache_invalidation: bool = True
    update_batch_size: int = 10
    update_timeout_ms: int = 1000
    audit_trail_enabled: bool = True


class OperationClassifier:
    """Classifies tool operations to determine context update requirements."""
    
    def __init__(self):
        self.operation_patterns = {
            'file_created': {
                'tools': ['Write'],
                'indicators': ['file_path'],
                'priority': 'medium'
            },
            'file_modified': {
                'tools': ['Edit', 'MultiEdit'],
                'indicators': ['file_path', 'old_string', 'new_string'],
                'priority': 'medium'
            },
            'file_deleted': {
                'tools': ['Bash'],
                'patterns': [r'rm\s+.*', r'del\s+.*'],
                'priority': 'high'
            },
            'task_created': {
                'tools': ['mcp__agenthub_http__manage_task'],
                'actions': ['create'],
                'priority': 'high'
            },
            'task_updated': {
                'tools': ['mcp__agenthub_http__manage_task'],
                'actions': ['update', 'complete'],
                'priority': 'high'
            },
            'subtask_updated': {
                'tools': ['mcp__agenthub_http__manage_subtask'],
                'actions': ['create', 'update', 'complete'],
                'priority': 'high'
            },
            'context_updated': {
                'tools': ['mcp__agenthub_http__manage_context'],
                'actions': ['update', 'add_insight', 'add_progress'],
                'priority': 'critical'
            },
            'git_operation': {
                'tools': ['Bash'],
                'patterns': [r'git\s+add.*', r'git\s+commit.*', r'git\s+push.*', r'git\s+branch.*'],
                'priority': 'medium'
            },
            'documentation_updated': {
                'tools': ['Write', 'Edit', 'MultiEdit'],
                'file_patterns': [r'.*\.md$', r'.*/ai_docs/.*'],
                'priority': 'low'
            }
        }
    
    def classify_operation(self, tool_name: str, tool_input: Dict[str, Any], tool_output: Optional[Dict] = None) -> Tuple[str, str, Dict]:
        """
        Classify tool operation to determine update requirements.
        
        Returns:
            (operation_type, priority, update_requirements)
        """
        # Check each operation pattern
        for operation_type, pattern in self.operation_patterns.items():
            if self._matches_pattern(tool_name, tool_input, tool_output, pattern):
                priority = pattern.get('priority', 'low')
                update_reqs = self._get_update_requirements(operation_type, tool_name, tool_input, tool_output)
                return operation_type, priority, update_reqs
        
        return 'unknown', 'none', {}
    
    def _matches_pattern(self, tool_name: str, tool_input: Dict, tool_output: Optional[Dict], pattern: Dict) -> bool:
        """Check if operation matches a specific pattern."""
        
        # Check tool name match
        if 'tools' in pattern:
            if tool_name not in pattern['tools']:
                return False
        
        # Check action match for MCP tools
        if 'actions' in pattern:
            action = tool_input.get('action', '')
            if action not in pattern['actions']:
                return False
        
        # Check regex patterns for bash commands
        if 'patterns' in pattern:
            command = tool_input.get('command', '')
            if not any(re.search(p, command) for p in pattern['patterns']):
                return False
        
        # Check file pattern matches
        if 'file_patterns' in pattern:
            file_path = tool_input.get('file_path', '')
            if not any(re.search(p, file_path) for p in pattern['file_patterns']):
                return False
        
        # Check required indicators
        if 'indicators' in pattern:
            if not all(indicator in tool_input for indicator in pattern['indicators']):
                return False
        
        return True
    
    def _get_update_requirements(self, operation_type: str, tool_name: str, tool_input: Dict, tool_output: Optional[Dict]) -> Dict:
        """Get specific update requirements for operation type."""
        
        base_requirements = {
            'operation_type': operation_type,
            'tool_name': tool_name,
            'timestamp': datetime.now().isoformat()
        }
        
        if operation_type in ['file_created', 'file_modified']:
            file_path = tool_input.get('file_path', '')
            base_requirements.update({
                'file_path': file_path,
                'file_extension': Path(file_path).suffix if file_path else '',
                'needs_documentation_check': file_path.endswith(('.py', '.js', '.ts', '.sh', '.sql'))
            })
        
        elif operation_type in ['task_created', 'task_updated']:
            base_requirements.update({
                'task_id': tool_input.get('task_id', ''),
                'git_branch_id': tool_input.get('git_branch_id', ''),
                'action': tool_input.get('action', ''),
                'needs_cache_invalidation': True
            })
        
        elif operation_type == 'subtask_updated':
            base_requirements.update({
                'task_id': tool_input.get('task_id', ''),
                'subtask_id': tool_input.get('subtask_id', ''),
                'action': tool_input.get('action', ''),
                'needs_parent_update': True
            })
        
        elif operation_type == 'context_updated':
            base_requirements.update({
                'context_id': tool_input.get('context_id', ''),
                'level': tool_input.get('level', ''),
                'action': tool_input.get('action', ''),
                'needs_hierarchy_sync': True
            })
        
        elif operation_type == 'git_operation':
            command = tool_input.get('command', '')
            base_requirements.update({
                'git_command': command,
                'needs_git_status_refresh': True,
                'affects_branch_context': 'branch' in command or 'checkout' in command
            })
        
        return base_requirements


class MCPContextUpdater:
    """Handles MCP context updates with async support and error handling."""
    
    def __init__(self, config: ContextUpdateConfig):
        self.config = config
        self.mcp_client = OptimizedMCPClient()
        self.cache = SessionContextCache()
    
    async def update_context(self, update_requirements: Dict) -> bool:
        """
        Update MCP context based on operation requirements.
        
        Returns True if update was successful, False otherwise.
        """
        operation_type = update_requirements.get('operation_type')
        
        try:
            if operation_type in ['file_created', 'file_modified']:
                return await self._handle_file_operation_update(update_requirements)
            elif operation_type in ['task_created', 'task_updated']:
                return await self._handle_task_update(update_requirements)
            elif operation_type == 'subtask_updated':
                return await self._handle_subtask_update(update_requirements)
            elif operation_type == 'context_updated':
                return await self._handle_context_update(update_requirements)
            elif operation_type == 'git_operation':
                return await self._handle_git_update(update_requirements)
            elif operation_type == 'documentation_updated':
                return await self._handle_documentation_update(update_requirements)
            else:
                logger.debug(f"No specific handler for operation type: {operation_type}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to update context for {operation_type}: {e}")
            return False
    
    async def _handle_file_operation_update(self, requirements: Dict) -> bool:
        """Handle context updates for file operations."""
        file_path = requirements.get('file_path', '')
        
        # Check if file has associated tasks
        related_tasks = await self._find_tasks_mentioning_file(file_path)
        
        if related_tasks:
            # Update task context with file modification info
            for task in related_tasks[:3]:  # Limit to 3 most relevant tasks
                task_id = task.get('id')
                if task_id:
                    await self._add_task_progress(task_id, f"Modified file: {file_path}")
        
        # Invalidate file-related cache entries
        if self.config.enable_cache_invalidation:
            self._invalidate_file_cache(file_path)
        
        return True
    
    async def _handle_task_update(self, requirements: Dict) -> bool:
        """Handle context updates for task operations."""
        task_id = requirements.get('task_id', '')
        action = requirements.get('action', '')
        
        if not task_id:
            return False
        
        # Invalidate task-related cache
        if self.config.enable_cache_invalidation:
            self._invalidate_task_cache(task_id)
        
        # If task was completed, update related contexts
        if action == 'complete':
            await self._handle_task_completion(task_id, requirements)
        
        return True
    
    async def _handle_subtask_update(self, requirements: Dict) -> bool:
        """Handle context updates for subtask operations."""
        task_id = requirements.get('task_id', '')
        subtask_id = requirements.get('subtask_id', '')
        
        if not task_id or not subtask_id:
            return False
        
        # Update parent task context if needed
        if requirements.get('needs_parent_update'):
            await self._update_parent_task_from_subtask(task_id, subtask_id)
        
        # Invalidate related cache
        if self.config.enable_cache_invalidation:
            self._invalidate_task_cache(task_id)
        
        return True
    
    async def _handle_context_update(self, requirements: Dict) -> bool:
        """Handle context updates for direct context operations."""
        context_id = requirements.get('context_id', '')
        level = requirements.get('level', '')
        
        if not context_id:
            return False
        
        # Synchronize hierarchy if needed
        if requirements.get('needs_hierarchy_sync'):
            await self._sync_context_hierarchy(context_id, level)
        
        # Invalidate context cache
        if self.config.enable_cache_invalidation:
            self._invalidate_context_cache(context_id, level)
        
        return True
    
    async def _handle_git_update(self, requirements: Dict) -> bool:
        """Handle context updates for git operations."""
        git_command = requirements.get('git_command', '')
        
        # Refresh git status cache if needed
        if requirements.get('needs_git_status_refresh'):
            self.cache.delete('git_status')
        
        # Update branch context if affected
        if requirements.get('affects_branch_context'):
            # This would typically update current branch information
            logger.info(f"Git operation affects branch context: {git_command}")
        
        return True
    
    async def _handle_documentation_update(self, requirements: Dict) -> bool:
        """Handle context updates for documentation changes."""
        file_path = requirements.get('file_path', '')
        
        # If documentation was updated, refresh documentation index
        if 'ai_docs' in file_path:
            logger.info(f"Documentation updated: {file_path}")
            # The post_tool_use.py hook already handles this via docs_indexer
        
        return True
    
    async def _handle_task_completion(self, task_id: str, requirements: Dict) -> bool:
        """Handle special processing when a task is completed."""
        try:
            # Get task details
            result = self.mcp_client.make_request("/mcp/manage_task", {
                "action": "get",
                "task_id": task_id
            })
            
            if result and result.get("success"):
                task = result.get("data", {}).get("task", {})
                
                # Add completion insight to context
                completion_insight = f"Task completed: {task.get('title', 'Unknown')} on {datetime.now().isoformat()}"
                
                git_branch_id = task.get('git_branch_id')
                if git_branch_id:
                    await self._add_branch_context_insight(git_branch_id, completion_insight)
                
                return True
            
        except Exception as e:
            logger.error(f"Failed to handle task completion for {task_id}: {e}")
        
        return False
    
    async def _find_tasks_mentioning_file(self, file_path: str) -> List[Dict]:
        """Find tasks that mention a specific file."""
        try:
            result = self.mcp_client.make_request("/mcp/manage_task", {
                "action": "search",
                "query": file_path,
                "limit": 5
            })
            
            if result and result.get("success"):
                return result.get("data", {}).get("tasks", [])
        except Exception as e:
            logger.warning(f"Failed to find tasks mentioning file {file_path}: {e}")
        
        return []
    
    async def _add_task_progress(self, task_id: str, progress_note: str) -> bool:
        """Add progress note to a task."""
        try:
            result = self.mcp_client.make_request("/mcp/manage_context", {
                "action": "add_progress",
                "level": "task",
                "context_id": task_id,
                "content": progress_note,
                "agent": "post_tool_hook"
            })
            
            return result and result.get("success", False)
        except Exception as e:
            logger.warning(f"Failed to add progress to task {task_id}: {e}")
            return False
    
    async def _add_branch_context_insight(self, git_branch_id: str, insight: str) -> bool:
        """Add insight to branch context."""
        try:
            result = self.mcp_client.make_request("/mcp/manage_context", {
                "action": "add_insight",
                "level": "branch",
                "context_id": git_branch_id,
                "content": insight,
                "category": "completion",
                "agent": "post_tool_hook"
            })
            
            return result and result.get("success", False)
        except Exception as e:
            logger.warning(f"Failed to add insight to branch {git_branch_id}: {e}")
            return False
    
    async def _update_parent_task_from_subtask(self, task_id: str, subtask_id: str) -> bool:
        """Update parent task based on subtask changes."""
        try:
            # This would typically recalculate parent task progress
            # based on subtask completion status
            logger.info(f"Updating parent task {task_id} from subtask {subtask_id}")
            
            # The MCP system should handle this automatically, but we can
            # trigger a context refresh here if needed
            
            return True
        except Exception as e:
            logger.error(f"Failed to update parent task {task_id} from subtask {subtask_id}: {e}")
            return False
    
    async def _sync_context_hierarchy(self, context_id: str, level: str) -> bool:
        """Synchronize context hierarchy after changes."""
        try:
            # This would trigger hierarchy synchronization in the MCP system
            logger.info(f"Syncing context hierarchy for {level}:{context_id}")
            
            # The context management system should handle this automatically
            # This is a placeholder for future hierarchy sync logic
            
            return True
        except Exception as e:
            logger.error(f"Failed to sync context hierarchy for {level}:{context_id}: {e}")
            return False
    
    def _invalidate_file_cache(self, file_path: str):
        """Invalidate cache entries related to a file."""
        cache_keys_to_invalidate = [
            f"file_context_{Path(file_path).name}",
            f"file_tasks_{file_path}",
            f"documentation_{file_path}"
        ]
        
        for key in cache_keys_to_invalidate:
            self.cache.delete(key)
    
    def _invalidate_task_cache(self, task_id: str):
        """Invalidate cache entries related to a task."""
        cache_keys_to_invalidate = [
            f"task_{task_id}",
            f"task_context_{task_id}",
            "pending_tasks",
            f"next_task_{task_id}"
        ]
        
        for key in cache_keys_to_invalidate:
            self.cache.delete(key)
    
    def _invalidate_context_cache(self, context_id: str, level: str):
        """Invalidate cache entries related to context."""
        cache_keys_to_invalidate = [
            f"context_{level}_{context_id}",
            f"hierarchy_{context_id}",
            f"{level}_context_{context_id}"
        ]
        
        for key in cache_keys_to_invalidate:
            self.cache.delete(key)


class ContextUpdater:
    """Main context updater for post-tool hooks."""
    
    def __init__(self, config: Optional[ContextUpdateConfig] = None):
        self.config = config or ContextUpdateConfig()
        self.classifier = OperationClassifier()
        self.mcp_updater = MCPContextUpdater(self.config)
        
    async def update_context(self, tool_name: str, tool_input: Dict[str, Any], tool_output: Optional[Dict] = None) -> bool:
        """
        Main entry point for context updates.
        
        Returns True if update was successful or not needed, False on error.
        """
        start_time = time.time()
        
        try:
            # Step 1: Classify operation (< 10ms)
            operation_type, priority, update_reqs = self.classifier.classify_operation(
                tool_name, tool_input, tool_output
            )
            
            if operation_type == 'unknown' or priority == 'none':
                logger.debug(f"No context update needed for {tool_name}")
                return True
            
            logger.info(f"Context update triggered for {tool_name} (type: {operation_type}, priority: {priority})")
            
            # Step 2: Update MCP context if enabled
            update_success = True
            if self.config.enable_mcp_updates:
                update_success = await self.mcp_updater.update_context(update_reqs)
            
            # Step 3: Create audit trail if enabled
            if self.config.audit_trail_enabled:
                self._create_audit_entry(tool_name, operation_type, update_success, update_reqs)
            
            execution_time = (time.time() - start_time) * 1000
            logger.info(f"Context update completed in {execution_time:.2f}ms")
            
            # Performance monitoring
            if execution_time > self.config.update_timeout_ms:
                logger.warning(
                    f"Context update exceeded timeout: {execution_time:.2f}ms > "
                    f"{self.config.update_timeout_ms}ms"
                )
            
            return update_success
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            logger.error(f"Context update failed after {execution_time:.2f}ms: {e}")
            return False
    
    def _create_audit_entry(self, tool_name: str, operation_type: str, success: bool, requirements: Dict):
        """Create audit trail entry for context updates."""
        try:
            from .env_loader import get_ai_data_path
            
            audit_entry = {
                'timestamp': datetime.now().isoformat(),
                'tool_name': tool_name,
                'operation_type': operation_type,
                'success': success,
                'requirements': {k: v for k, v in requirements.items() if k != 'tool_output'}  # Exclude large output
            }
            
            audit_log_path = get_ai_data_path() / 'context_updates_audit.json'
            
            # Read existing audit data
            if audit_log_path.exists():
                with open(audit_log_path, 'r') as f:
                    try:
                        audit_data = json.load(f)
                    except (json.JSONDecodeError, ValueError):
                        audit_data = []
            else:
                audit_data = []
            
            audit_data.append(audit_entry)
            
            # Keep only last 200 entries
            if len(audit_data) > 200:
                audit_data = audit_data[-200:]
            
            with open(audit_log_path, 'w') as f:
                json.dump(audit_data, f, indent=2)
                
        except Exception as e:
            logger.warning(f"Failed to create audit entry: {e}")


# Factory function for easy usage
def create_context_updater(config: Optional[ContextUpdateConfig] = None) -> ContextUpdater:
    """Create a context updater instance with optional configuration."""
    return ContextUpdater(config)


# Synchronous wrapper for use in existing hook infrastructure
def update_context_sync(tool_name: str, tool_input: Dict[str, Any], tool_output: Optional[Dict] = None) -> bool:
    """
    Synchronous wrapper for context updates.
    
    This function provides a synchronous interface for the existing hook system
    while internally using async operations for better performance.
    """
    updater = create_context_updater()
    
    # Run async operation in event loop
    try:
        # Check if we're already in an async event loop
        try:
            loop = asyncio.get_running_loop()
            # If already in an event loop, create a new one in a thread
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, updater.update_context(tool_name, tool_input, tool_output))
                return future.result(timeout=2.0)  # 2 second timeout
        except RuntimeError:
            # No event loop is running, create a new one
            return asyncio.run(updater.update_context(tool_name, tool_input, tool_output))
    except Exception as e:
        logger.error(f"Synchronous context update failed: {e}")
        return False


if __name__ == "__main__":
    # Test the context updater
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Context Updater")
    parser.add_argument('--tool', required=True, help='Tool name to test')
    parser.add_argument('--input', required=True, help='Tool input JSON')
    parser.add_argument('--output', help='Tool output JSON (optional)')
    
    args = parser.parse_args()
    
    try:
        tool_input = json.loads(args.input)
        tool_output = json.loads(args.output) if args.output else None
        
        success = update_context_sync(args.tool, tool_input, tool_output)
        
        if success:
            print("Context update completed successfully")
        else:
            print("Context update failed")
            exit(1)
            
    except Exception as e:
        print(f"Test failed: {e}")
        exit(1)