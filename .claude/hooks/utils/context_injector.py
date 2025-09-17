#!/usr/bin/env python3
"""
Context Injection Module for Real-Time Hook Enhancement

This module implements the real-time context injection system for the pre-tool hook,
providing intelligent context detection, MCP queries, and performance optimization.

Task ID: de7621a4-df75-4d03-a967-8fb743b455f1 (Phase 2)
Architecture Reference: Real-Time Context Injection System
"""

import os
import json
import time
import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass

# Import MCP client and cache manager
try:
    from .mcp_client import OptimizedMCPClient
    from .cache_manager import SessionContextCache
except ImportError:
    # Fall back to absolute imports when run as script
    from mcp_client import OptimizedMCPClient
    from cache_manager import SessionContextCache

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class ContextInjectionConfig:
    """Configuration for context injection system."""
    performance_threshold_ms: int = 500
    cache_ttl_seconds: int = 900  # 15 minutes
    max_mcp_requests: int = 5
    enable_async_injection: bool = True
    fallback_strategy: str = "cache_then_skip"  # cache_then_skip, skip, error
    test_mode: bool = False  # Disable MCP requests in test environments

    def __post_init__(self):
        """Auto-detect test mode if not explicitly set."""
        # Store the original value to see if it was explicitly set
        explicitly_set = self.test_mode

        if not explicitly_set:
            # Detect test environment multiple ways
            import sys
            # Check for test-related modules
            test_modules = any(mod in sys.modules for mod in ['pytest', '_pytest', 'unittest'])
            # Check environment variables
            test_env = any(env in os.environ for env in ['PYTEST_CURRENT_TEST', 'TEST_MODE'])
            # Check command line arguments
            test_argv = any('test' in str(arg).lower() for arg in sys.argv)
            # Check if running from test directory
            test_cwd = 'test' in os.getcwd().lower()

            self.test_mode = test_modules or test_env or test_argv or test_cwd

            # Log detection for debugging
            logger.debug(f"Test mode detection: modules={test_modules}, env={test_env}, argv={test_argv}, cwd={test_cwd}, result={self.test_mode}")
        else:
            logger.debug(f"Test mode explicitly set to: {self.test_mode}")


class ContextRelevanceDetector:
    """Detects when tool calls require context injection."""
    
    def __init__(self):
        self.context_triggers = {
            # MCP task management operations
            'mcp__agenthub_http__manage_task': {
                'actions': ['get', 'update', 'complete', 'next', 'list', 'search'],
                'priority': 'high'
            },
            'mcp__agenthub_http__manage_subtask': {
                'actions': ['create', 'update', 'complete', 'list'],
                'priority': 'high'
            },
            'mcp__agenthub_http__manage_context': {
                'actions': ['get', 'update', 'resolve'],
                'priority': 'high'
            },
            
            # File operations on documented files
            'Write': {
                'file_extensions': ['.py', '.js', '.ts', '.md', '.sh', '.sql', '.jsx', '.tsx'],
                'priority': 'medium'
            },
            'Edit': {
                'file_extensions': ['.py', '.js', '.ts', '.md', '.sh', '.sql', '.jsx', '.tsx'],
                'priority': 'medium'
            },
            'MultiEdit': {
                'file_extensions': ['.py', '.js', '.ts', '.md', '.sh', '.sql', '.jsx', '.tsx'],
                'priority': 'medium'
            },
            
            # Analysis operations
            'Grep': {
                'patterns': ['todo', 'fixme', 'bug', 'error', 'test'],
                'priority': 'low'
            },
            'Glob': {
                'patterns': ['**/*.py', '**/*.js', '**/*.ts', '**/*.md'],
                'priority': 'low'
            },
            
            # Git operations
            'Bash': {
                'git_commands': ['git status', 'git commit', 'git branch', 'git diff', 'git log'],
                'priority': 'medium'
            }
        }
    
    def is_context_relevant(self, tool_name: str, tool_input: Dict[str, Any]) -> Tuple[bool, str, Dict]:
        """
        Determine if a tool call requires context injection.
        
        Returns:
            (is_relevant, priority, context_requirements)
        """
        if tool_name not in self.context_triggers:
            return False, 'none', {}
        
        trigger_config = self.context_triggers[tool_name]
        priority = trigger_config.get('priority', 'low')
        
        # Check MCP operations
        if 'actions' in trigger_config:
            action = tool_input.get('action', '')
            if action in trigger_config['actions']:
                context_reqs = self._get_mcp_context_requirements(tool_name, action, tool_input)
                return True, priority, context_reqs
        
        # Check file operations
        if 'file_extensions' in trigger_config:
            file_path = tool_input.get('file_path', '')
            if file_path and any(file_path.endswith(ext) for ext in trigger_config['file_extensions']):
                context_reqs = self._get_file_context_requirements(file_path, tool_input)
                return True, priority, context_reqs
        
        # Check bash git operations
        if tool_name == 'Bash' and 'git_commands' in trigger_config:
            command = tool_input.get('command', '')
            if any(git_cmd in command for git_cmd in trigger_config['git_commands']):
                context_reqs = self._get_git_context_requirements(command)
                return True, priority, context_reqs
        
        # Check grep/glob patterns
        if 'patterns' in trigger_config:
            pattern = tool_input.get('pattern', '') or tool_input.get('query', '')
            if pattern:
                # Use different matching logic for Glob vs Grep
                if tool_name == 'Glob':
                    # For Glob, check if the input pattern contains any of the file extensions
                    pattern_match = any(
                        ('.' + p.split('*.')[-1]) in pattern.lower()
                        for p in trigger_config['patterns'] if '*.' in p
                    )
                else:
                    # For Grep and other tools, use substring matching
                    pattern_match = any(p in pattern.lower() for p in trigger_config['patterns'])

                if pattern_match:
                    context_reqs = self._get_search_context_requirements(pattern, tool_input)
                    return True, priority, context_reqs
        
        return False, 'none', {}
    
    def _get_mcp_context_requirements(self, tool_name: str, action: str, tool_input: Dict) -> Dict:
        """Get context requirements for MCP operations."""
        requirements = {
            'type': 'mcp_operation',
            'tool_name': tool_name,
            'action': action
        }
        
        # Task-specific requirements
        if 'task' in tool_name:
            if task_id := tool_input.get('task_id'):
                requirements['task_id'] = task_id
            if git_branch_id := tool_input.get('git_branch_id'):
                requirements['git_branch_id'] = git_branch_id
        
        # Context-specific requirements  
        if 'context' in tool_name:
            if context_id := tool_input.get('context_id'):
                requirements['context_id'] = context_id
            if level := tool_input.get('level'):
                requirements['level'] = level
        
        return requirements
    
    def _get_file_context_requirements(self, file_path: str, tool_input: Dict) -> Dict:
        """Get context requirements for file operations."""
        return {
            'type': 'file_operation',
            'file_path': file_path,
            'file_extension': Path(file_path).suffix,
            'operation_type': 'write' if 'content' in tool_input else 'edit'
        }
    
    def _get_git_context_requirements(self, command: str) -> Dict:
        """Get context requirements for git operations."""
        return {
            'type': 'git_operation',
            'command': command,
            'needs_git_status': 'status' in command,
            'needs_branch_info': 'branch' in command
        }
    
    def _get_search_context_requirements(self, pattern: str, tool_input: Dict) -> Dict:
        """Get context requirements for search operations."""
        return {
            'type': 'search_operation',
            'pattern': pattern,
            'search_path': tool_input.get('path', '.'),
            'file_filter': tool_input.get('glob', '')
        }


class MCPContextQuery:
    """Handles MCP context queries with async support and caching."""
    
    def __init__(self, config: ContextInjectionConfig):
        self.config = config
        self.mcp_client = OptimizedMCPClient()
        self.cache = SessionContextCache()
    
    async def query_context(self, context_requirements: Dict) -> Optional[Dict]:
        """
        Query MCP for relevant context based on requirements.
        
        Performance target: < 400ms for MCP queries
        """
        query_type = context_requirements.get('type')
        
        # Create cache key from requirements
        cache_key = self._create_cache_key(context_requirements)
        
        # Check cache first (< 50ms)
        cached_context = self.cache.get(cache_key, self.config.cache_ttl_seconds)
        if cached_context:
            logger.debug(f"Cache hit for context query: {query_type}")
            return cached_context
        
        # Query MCP based on type
        start_time = time.time()
        
        try:
            if query_type == 'mcp_operation':
                context_data = await self._query_mcp_operation_context(context_requirements)
            elif query_type == 'file_operation':
                context_data = await self._query_file_context(context_requirements)
            elif query_type == 'git_operation':
                context_data = await self._query_git_context(context_requirements)
            elif query_type == 'search_operation':
                context_data = await self._query_search_context(context_requirements)
            else:
                logger.warning(f"Unknown context query type: {query_type}")
                return None
            
            # Cache the results
            if context_data:
                self.cache.set(cache_key, context_data, self.config.cache_ttl_seconds)
            
            query_time = (time.time() - start_time) * 1000
            logger.debug(f"MCP context query completed in {query_time:.2f}ms")
            
            return context_data
            
        except Exception as e:
            logger.error(f"MCP context query failed: {e}")
            return None
    
    async def _query_mcp_operation_context(self, requirements: Dict) -> Optional[Dict]:
        """Query context for MCP operations."""
        tool_name = requirements['tool_name']
        action = requirements['action']
        
        context_data = {'mcp_operation': {'tool': tool_name, 'action': action}}
        
        # For list/search actions, get recent tasks
        if action in ['list', 'search']:
            recent_tasks = await self._get_recent_tasks()
            if recent_tasks:
                context_data['recent_tasks'] = recent_tasks
        
        # Get task context if needed
        if 'task_id' in requirements:
            task_context = await self._get_task_context(requirements['task_id'])
            if task_context:
                context_data['task'] = task_context
            else:
                # If task_id was requested but couldn't be retrieved, fail the operation
                logger.warning(f"Failed to retrieve required task context for {requirements['task_id']}")
                return None
        
        # Get git branch context if needed
        if 'git_branch_id' in requirements:
            branch_context = await self._get_branch_context(requirements['git_branch_id'])
            if branch_context:
                context_data['git_branch'] = branch_context
        
        # Get project context for project operations
        if 'project' in tool_name.lower():
            project_context = await self._get_project_context()
            if project_context:
                context_data['project'] = project_context
        
        return context_data
    
    async def _query_file_context(self, requirements: Dict) -> Optional[Dict]:
        """Query context for file operations."""
        file_path = requirements['file_path']
        
        context_data = {
            'file_operation': {
                'path': file_path,
                'extension': requirements.get('file_extension', ''),
                'type': requirements.get('operation_type', 'unknown')
            }
        }
        
        # Check if file has documentation
        docs_path = self._get_documentation_path(file_path)
        if docs_path and docs_path.exists():
            context_data['documentation'] = {
                'exists': True,
                'path': str(docs_path),
                'last_modified': datetime.fromtimestamp(docs_path.stat().st_mtime).isoformat()
            }
        
        # Get related tasks if any
        related_tasks = await self._get_file_related_tasks(file_path)
        if related_tasks:
            context_data['related_tasks'] = related_tasks
        
        return context_data
    
    async def _query_git_context(self, requirements: Dict) -> Optional[Dict]:
        """Query context for git operations."""
        command = requirements['command']
        
        context_data = {'git_operation': {'command': command}}
        
        # Get current git status if needed
        if requirements.get('needs_git_status'):
            git_status = self.cache.get_git_status()
            if not git_status:
                # This would typically use a git command wrapper
                git_status = {'status': 'unknown', 'cached': False}
            context_data['git_status'] = git_status
        
        # Get branch information if needed
        if requirements.get('needs_branch_info'):
            branch_info = await self._get_current_branch_info()
            if branch_info:
                context_data['branch_info'] = branch_info
        
        return context_data
    
    async def _query_search_context(self, requirements: Dict) -> Optional[Dict]:
        """Query context for search operations."""
        pattern = requirements['pattern']
        
        context_data = {
            'search_operation': {
                'pattern': pattern,
                'path': requirements.get('search_path', '.'),
                'filter': requirements.get('file_filter', '')
            }
        }
        
        # Get related documentation or tasks matching the search
        if any(keyword in pattern.lower() for keyword in ['todo', 'fixme', 'bug', 'error']):
            related_tasks = await self._get_pattern_related_tasks(pattern)
            if related_tasks:
                context_data['related_tasks'] = related_tasks
        
        return context_data
    
    async def _get_task_context(self, task_id: str) -> Optional[Dict]:
        """Get task context from MCP."""
        # Skip MCP requests in test mode
        if self.config.test_mode:
            logger.debug("Skipping MCP request in test mode")
            return None

        try:
            result = self.mcp_client.make_request("/mcp/manage_task", {
                "action": "get",
                "task_id": task_id,
                "include_context": True
            })
            
            if result:
                # Handle both direct result and nested data structure
                if "task" in result:
                    return result["task"]
                elif "data" in result and "task" in result["data"]:
                    return result["data"]["task"]
                elif "success" in result and result.get("data", {}).get("task"):
                    return result["data"]["task"]
        except Exception as e:
            logger.warning(f"Failed to get task context for {task_id}: {e}")
        
        return None
    
    async def _get_branch_context(self, git_branch_id: str) -> Optional[Dict]:
        """Get git branch context from MCP."""
        # Skip MCP requests in test mode
        if self.config.test_mode:
            logger.debug("Skipping MCP request in test mode")
            return None

        try:
            result = self.mcp_client.make_request("/mcp/manage_git_branch", {
                "action": "get",
                "git_branch_id": git_branch_id
            })
            
            if result and result.get("success"):
                return result.get("data", {}).get("git_branch")
        except Exception as e:
            logger.warning(f"Failed to get branch context for {git_branch_id}: {e}")
        
        return None
    
    async def _get_current_branch_info(self) -> Optional[Dict]:
        """Get current git branch information."""
        # This would integrate with git commands or existing git utilities
        return {
            'current_branch': 'main',  # Placeholder
            'has_changes': False,
            'cached': True
        }
    
    async def _get_recent_tasks(self, limit: int = 5) -> Optional[List[Dict]]:
        """Get recent tasks from MCP."""
        # Skip MCP requests in test mode
        if self.config.test_mode:
            logger.debug("Skipping MCP request in test mode")
            return None

        try:
            result = self.mcp_client.make_request("/mcp/manage_task", {
                "action": "list",
                "limit": limit,
                "status": "in_progress"  # Focus on active tasks
            })
            
            if result:
                # Handle different response formats
                if "tasks" in result:
                    return result["tasks"]
                elif "data" in result and "tasks" in result["data"]:
                    return result["data"]["tasks"]
                elif isinstance(result, list):
                    return result[:limit]
        except Exception as e:
            logger.warning(f"Failed to get recent tasks: {e}")
        
        return None
    
    async def _get_project_context(self) -> Optional[Dict]:
        """Get current project context from MCP."""
        # Skip MCP requests in test mode
        if self.config.test_mode:
            logger.debug("Skipping MCP request in test mode")
            return None

        try:
            result = self.mcp_client.make_request("/mcp/manage_project", {
                "action": "list",
                "limit": 1  # Get current project
            })
            
            if result:
                # Handle different response formats
                if "projects" in result and result["projects"]:
                    return result["projects"][0]
                elif "data" in result and "projects" in result["data"]:
                    projects = result["data"]["projects"]
                    return projects[0] if projects else None
        except Exception as e:
            logger.warning(f"Failed to get project context: {e}")
        
        return None
    
    async def _get_file_related_tasks(self, file_path: str) -> Optional[List[Dict]]:
        """Get tasks related to a specific file."""
        # Search for tasks mentioning this file
        try:
            # Extract filename for search
            from pathlib import Path
            filename = Path(file_path).name
            
            result = self.mcp_client.make_request("/mcp/manage_task", {
                "action": "search",
                "query": filename,
                "limit": 5
            })
            
            if result:
                # Handle different response formats
                if "tasks" in result:
                    return result["tasks"]
                elif "data" in result and "tasks" in result["data"]:
                    return result["data"]["tasks"]
        except Exception as e:
            logger.warning(f"Failed to get file related tasks for {file_path}: {e}")
        
        return None
    
    async def _get_pattern_related_tasks(self, pattern: str) -> Optional[List[Dict]]:
        """Get tasks related to search pattern."""
        try:
            result = self.mcp_client.make_request("/mcp/manage_task", {
                "action": "search",
                "query": pattern,
                "limit": 3
            })
            
            if result and result.get("success"):
                return result.get("data", {}).get("tasks", [])
        except Exception as e:
            logger.warning(f"Failed to get pattern related tasks for {pattern}: {e}")
        
        return None
    
    def _get_documentation_path(self, file_path: str) -> Optional[Path]:
        """Get documentation path for a file."""
        try:
            path_obj = Path(file_path)
            project_root = Path.cwd()
            
            # Build documentation path
            relative_path = path_obj.relative_to(project_root)
            doc_path = project_root / 'ai_docs' / '_absolute_docs' / relative_path.parent / f"{relative_path.name}.md"
            
            return doc_path
        except Exception:
            return None
    
    def _create_cache_key(self, context_requirements: Dict) -> str:
        """Create a cache key from context requirements."""
        # Sort dict keys for consistent cache keys
        sorted_reqs = json.dumps(context_requirements, sort_keys=True)
        import hashlib
        return hashlib.md5(sorted_reqs.encode('utf-8')).hexdigest()


class ContextInjector:
    """Main context injection manager for pre-tool hooks."""
    
    def __init__(self, config: Optional[ContextInjectionConfig] = None):
        self.config = config or ContextInjectionConfig()
        self.detector = ContextRelevanceDetector()
        self.query_engine = MCPContextQuery(self.config)
        
    async def inject_context(self, tool_name: str, tool_input: Dict[str, Any]) -> Optional[str]:
        """
        Main entry point for context injection.
        
        Returns formatted context string to inject into system reminder or None.
        Performance target: < 500ms total execution time
        """
        start_time = time.time()
        
        try:
            # Step 1: Detect if context injection is needed (< 10ms)
            is_relevant, priority, context_reqs = self.detector.is_context_relevant(tool_name, tool_input)
            
            if not is_relevant:
                logger.debug(f"No context injection needed for {tool_name}")
                return None
            
            logger.info(f"Context injection triggered for {tool_name} (priority: {priority})")
            
            # Step 2: Query for context data (< 400ms)
            context_data = await self.query_engine.query_context(context_reqs)
            
            if not context_data:
                logger.warning(f"No context data retrieved for {tool_name}")
                return None
            
            # Step 3: Format context for injection (< 50ms)
            formatted_context = self._format_context_injection(context_data, priority)
            
            execution_time = (time.time() - start_time) * 1000
            logger.info(f"Context injection completed in {execution_time:.2f}ms")
            
            # Performance monitoring
            if execution_time > self.config.performance_threshold_ms:
                logger.warning(
                    f"Context injection exceeded threshold: {execution_time:.2f}ms > "
                    f"{self.config.performance_threshold_ms}ms"
                )
            
            return formatted_context
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            logger.error(f"Context injection failed after {execution_time:.2f}ms: {e}")
            return None
    
    def _format_context_injection(self, context_data: Dict, priority: str) -> str:
        """Format context data for injection into system reminder."""
        lines = ["<context-injection>"]
        lines.append(f"Priority: {priority}")
        lines.append(f"Injected at: {datetime.now().isoformat()}")
        lines.append("")
        
        # Format different types of context
        if 'task' in context_data:
            task = context_data['task']
            lines.extend([
                "## Current Task Context:",
                f"- **Task ID**: {task.get('id', 'N/A')}",
                f"- **Title**: {task.get('title', 'N/A')}",
                f"- **Status**: {task.get('status', 'N/A')}",
                f"- **Priority**: {task.get('priority', 'N/A')}",
                f"- **Assignees**: {', '.join(task.get('assignees', []))}",
                ""
            ])
            
            if task.get('details'):
                lines.extend([
                    "### Task Details:",
                    task['details'][:500] + ("..." if len(task['details']) > 500 else ""),
                    ""
                ])
        
        if 'git_branch' in context_data:
            branch = context_data['git_branch']
            lines.extend([
                "## Git Branch Context:",
                f"- **Branch ID**: {branch.get('id', 'N/A')}",
                f"- **Name**: {branch.get('git_branch_name', 'N/A')}",
                f"- **Description**: {branch.get('git_branch_description', 'N/A')}",
                ""
            ])
        
        if 'documentation' in context_data:
            docs = context_data['documentation']
            lines.extend([
                "## Documentation Context:",
                f"- **Exists**: {docs.get('exists', False)}",
                f"- **Path**: {docs.get('path', 'N/A')}",
                f"- **Last Modified**: {docs.get('last_modified', 'N/A')}",
                ""
            ])
        
        if 'related_tasks' in context_data:
            tasks = context_data['related_tasks']
            if tasks:
                lines.extend(["## Related Tasks:"])
                for task in tasks[:3]:  # Limit to 3 most relevant
                    lines.append(f"- **{task.get('title', 'N/A')}** ({task.get('status', 'N/A')})")
                lines.append("")
        
        if 'git_status' in context_data:
            git_info = context_data['git_status']
            lines.extend([
                "## Git Status:",
                f"- **Status**: {git_info.get('status', 'N/A')}",
                f"- **Cached**: {git_info.get('cached', False)}",
                ""
            ])
        
        lines.append("</context-injection>")
        
        return "\n".join(lines)


# Factory function for easy usage
def create_context_injector(config: Optional[ContextInjectionConfig] = None) -> ContextInjector:
    """Create a context injector instance with optional configuration."""
    return ContextInjector(config)


# Synchronous wrapper for use in existing hook infrastructure
def inject_context_sync(tool_name: str, tool_input: Dict[str, Any]) -> Optional[str]:
    """
    Synchronous wrapper for context injection.
    
    This function provides a synchronous interface for the existing hook system
    while internally using async operations for better performance.
    """
    injector = create_context_injector()
    
    # Run async operation in event loop
    import concurrent.futures
    try:
        # Check if we're already in an async event loop
        try:
            loop = asyncio.get_running_loop()
            # If already in an event loop, create a new one in a thread
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, injector.inject_context(tool_name, tool_input))
                return future.result(timeout=1.0)  # 1 second timeout
        except RuntimeError:
            # No event loop is running, create a new one
            task = injector.inject_context(tool_name, tool_input)
            return asyncio.run(asyncio.wait_for(task, timeout=1.0))
    except (TimeoutError, concurrent.futures.TimeoutError) as e:
        logger.warning(f"Context injection timed out: {e}")
        return None
    except Exception as e:
        logger.error(f"Synchronous context injection failed: {e}")
        return None


if __name__ == "__main__":
    # Test the context injector
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Context Injector")
    parser.add_argument('--tool', required=True, help='Tool name to test')
    parser.add_argument('--input', required=True, help='Tool input JSON')
    
    args = parser.parse_args()
    
    try:
        tool_input = json.loads(args.input)
        context = inject_context_sync(args.tool, tool_input)
        
        if context:
            print("Context injection result:")
            print(context)
        else:
            print("No context injection needed or available")
            
    except Exception as e:
        print(f"Test failed: {e}")
        exit(1)