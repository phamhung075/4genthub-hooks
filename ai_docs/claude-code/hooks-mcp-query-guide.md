# Claude Hooks MCP Query Integration Guide

## Overview

The `.claude/hooks` system provides multiple ways to query and interact with your MCP (Model Context Protocol) server. This guide shows you how to leverage MCP tools within the hooks system for data queries, task management, and context operations.

## 🔧 MCP Integration Architecture

### Current MCP Query Methods

```
📋 HOOKS MCP INTEGRATION
├── 🌐 mcp_client.py (603 lines) - HTTP client with auth
├── 🔄 mcp_task_interceptor.py (228 lines) - Task interception
├── 📋 context_injector.py (740 lines) - Context queries
├── 📊 session_start.py (991 lines) - Session initialization
└── 🔄 role_enforcer.py (298 lines) - Permission checking
```

## 🌐 Method 1: HTTP Client Queries (Primary)

### Location: `.claude/hooks/utils/mcp_client.py`

The main MCP client provides direct HTTP communication with your MCP server:

```python
# Get default MCP client
from utils.mcp_client import get_default_client

client = get_default_client()

# Query pending tasks
pending_tasks = client.query_pending_tasks(limit=5, user_id="your_user_id")

# Query project context
project_context = client.query_project_context(project_id="proj_uuid")

# Query git branch info
branch_info = client.query_git_branch_info(branch_id="branch_uuid")

# Test connectivity
is_connected = client.test_connection()
```

### Available Query Methods

#### 1. **Task Queries**
```python
# Query pending tasks
tasks = client.query_pending_tasks(
    limit=10,           # Max tasks to return
    user_id="user_123"  # Optional user filter
)

# Query next recommended task
next_task = client.query_next_task(
    branch_id="branch_uuid",
    include_context=True
)
```

#### 2. **Context Queries**
```python
# Query project context
context = client.query_project_context(
    project_id="proj_uuid"
)

# Query hierarchical context
hierarchy = client.query_context_hierarchy(
    level="task",          # global/project/branch/task
    context_id="task_uuid"
)
```

#### 3. **Branch Queries**
```python
# Query git branch information
branch_data = client.query_git_branch_info(
    branch_id="branch_uuid"
)

# Query branch statistics
stats = client.query_branch_statistics(
    branch_id="branch_uuid"
)
```

## 🔄 Method 2: Session-Level Query Functions

### Location: `.claude/hooks/session_start.py`

Session hooks provide convenience functions for common queries:

```python
# Query pending tasks (cached)
from session_start import query_mcp_pending_tasks, query_mcp_next_task

# Get pending tasks (uses cache when available)
pending = query_mcp_pending_tasks()

# Get next recommended task for branch
next_task = query_mcp_next_task(branch_id="branch_uuid")
```

### Session Query Features
- **Automatic caching** - Results cached for session duration
- **Fallback handling** - Graceful degradation when MCP unavailable
- **Performance optimization** - Reduced API calls through intelligent caching

## 📋 Method 3: Context Injection Queries

### Location: `.claude/hooks/utils/context_injector.py`

For advanced context-aware queries:

```python
from utils.context_injector import ContextInjector

injector = ContextInjector()

# Query context based on requirements
context_data = await injector.query_context({
    'query_type': 'mcp_operation',
    'operation': 'task_management',
    'context_requirements': {
        'include_tasks': True,
        'include_context': True,
        'branch_id': 'branch_uuid'
    }
})
```

### Context Query Types
- **`mcp_operation`** - Query for MCP-specific operations
- **`task_context`** - Get task-related context
- **`project_context`** - Retrieve project information
- **`agent_context`** - Agent-specific data

## 🛡️ Method 4: Task Interception Queries

### Location: `.claude/hooks/utils/mcp_task_interceptor.py`

For intercepting and querying task operations:

```python
from utils.mcp_task_interceptor import get_mcp_interceptor

interceptor = get_mcp_interceptor()

# Intercept task creation
task_result = interceptor.intercept_task_creation({
    'title': 'New task',
    'assignees': 'coding-agent',
    'details': 'Task requirements...'
})

# Query intercepted tasks
intercepted = interceptor.get_intercepted_tasks()
```

## 🔐 Authentication & Configuration

### Token Management
The hooks system automatically handles MCP authentication:

```python
# Token is automatically managed via TokenManager
# Stored in: ~/.claude/.mcp_token_cache

# Manual token refresh (if needed)
from utils.mcp_client import TokenManager

token_mgr = TokenManager()
valid_token = token_mgr.get_valid_token()
```

### Environment Configuration
```bash
# Required environment variables
MCP_SERVER_URL=http://localhost:8000
TOKEN_REFRESH_BEFORE_EXPIRY=60  # Refresh 60s before expiry

# Optional configuration
MCP_REQUEST_TIMEOUT=30
MCP_MAX_RETRIES=3
```

## 📊 Practical Usage Examples

### Example 1: Query Tasks in Pre-Tool Hook
```python
# In pre_tool_use.py or custom hook
from utils.mcp_client import get_default_client

def check_pending_work():
    """Check for pending tasks before tool execution."""
    client = get_default_client()
    if client and client.test_connection():
        tasks = client.query_pending_tasks(limit=3)
        if tasks:
            print(f"📋 You have {len(tasks)} pending tasks")
            for task in tasks:
                print(f"  • {task.get('title', 'Untitled')}")
    return tasks
```

### Example 2: Context-Aware Operations
```python
# Query context for current operation
from utils.context_injector import ContextInjector

async def get_operation_context(tool_name: str):
    """Get relevant context for tool operation."""
    injector = ContextInjector()

    context = await injector.query_context({
        'query_type': 'mcp_operation',
        'tool_name': tool_name,
        'context_requirements': {
            'include_related_tasks': True,
            'include_project_info': True
        }
    })

    return context
```

### Example 3: Branch-Specific Queries
```python
# Get branch-specific information
from utils.mcp_client import get_default_client

def get_branch_context(branch_id: str):
    """Get comprehensive branch information."""
    client = get_default_client()

    if client:
        # Get branch info
        branch_info = client.query_git_branch_info(branch_id)

        # Get branch tasks
        branch_tasks = client.query_pending_tasks(
            limit=10,
            filters={'git_branch_id': branch_id}
        )

        # Get next recommended task
        next_task = client.query_next_task(branch_id)

        return {
            'branch': branch_info,
            'tasks': branch_tasks,
            'next_task': next_task
        }

    return None
```

## 🔄 Query Caching & Performance

### Session-Level Caching
```python
from utils.cache_manager import get_session_cache

cache = get_session_cache()

# Cache query results
cache.cache_pending_tasks(tasks)
cache.cache_branch_info(branch_id, branch_data)

# Retrieve cached data
cached_tasks = cache.get_pending_tasks()
cached_branch = cache.get_branch_info(branch_id)
```

### Cache Invalidation
- **Time-based**: Caches expire after session timeout
- **Event-based**: Invalidated on relevant MCP operations
- **Manual**: Can be cleared via `cache.clear()`

## ⚠️ Error Handling & Fallbacks

### Connection Handling
```python
from utils.mcp_client import get_default_client, MCPAuthenticationError

def safe_mcp_query():
    """Safe MCP query with error handling."""
    try:
        client = get_default_client()
        if not client:
            print("⚠️ MCP client not available")
            return None

        if not client.test_connection():
            print("⚠️ MCP server not responding")
            return None

        # Perform query
        result = client.query_pending_tasks()
        return result

    except MCPAuthenticationError:
        print("🔐 MCP authentication failed")
        return None
    except Exception as e:
        print(f"❌ MCP query failed: {e}")
        return None
```

### Graceful Degradation
The hooks system is designed to work even when MCP is unavailable:
- **Cached fallbacks** - Use last known good data
- **Local operations** - Continue with reduced functionality
- **Silent failures** - Log errors but don't block execution

## 🚀 Advanced Integration Patterns

### Pattern 1: Real-time Task Monitoring
```python
# Monitor tasks during hook execution
class TaskMonitor:
    def __init__(self):
        self.client = get_default_client()

    def monitor_session_tasks(self):
        """Monitor tasks throughout session."""
        if self.client:
            return self.client.query_pending_tasks(limit=5)
        return []

    def get_priority_tasks(self):
        """Get high-priority tasks."""
        tasks = self.monitor_session_tasks()
        return [t for t in tasks if t.get('priority') in ['high', 'urgent']]
```

### Pattern 2: Context-Driven Operations
```python
# Use MCP data to drive hook behavior
async def context_driven_hook(tool_name: str, tool_input: dict):
    """Hook that adapts based on MCP context."""
    # Get current context
    context = await get_operation_context(tool_name)

    # Adapt behavior based on context
    if context and 'active_tasks' in context:
        active_tasks = context['active_tasks']
        if len(active_tasks) > 5:
            print("⚠️ Many active tasks - consider completing some first")

    # Continue with normal hook operation
    return True
```

## 📈 Query Performance Tips

1. **Use caching** - Leverage session cache for repeated queries
2. **Batch requests** - Combine multiple queries when possible
3. **Limit results** - Use reasonable limits for large datasets
4. **Async operations** - Use async queries for better performance
5. **Error handling** - Always handle connection failures gracefully

## 🔧 Troubleshooting

### Common Issues

#### 1. **Authentication Failures**
```bash
# Check token file
ls -la ~/.claude/.mcp_token_cache

# Verify MCP server is running
curl http://localhost:8000/health
```

#### 2. **Connection Issues**
```python
# Test connection manually
from utils.mcp_client import get_default_client

client = get_default_client()
if client:
    connected = client.test_connection()
    print(f"MCP Connection: {'✅' if connected else '❌'}")
```

#### 3. **Query Timeouts**
```bash
# Increase timeout in environment
export MCP_REQUEST_TIMEOUT=60
```

## 📝 Summary

The hooks system provides multiple layers for MCP queries:

- **🌐 Direct HTTP Client** - Full-featured MCP communication
- **🔄 Session Functions** - Cached convenience methods
- **📋 Context Injection** - Smart context-aware queries
- **🛡️ Task Interception** - Operation monitoring and control

Choose the method that best fits your specific use case:
- Use **HTTP client** for direct control
- Use **session functions** for performance
- Use **context injection** for smart operations
- Use **task interception** for monitoring

All methods include proper error handling, authentication, and fallback mechanisms to ensure robust operation.