# Claude Hooks Logging Architecture

## Overview

The Claude hooks system implements a comprehensive logging architecture that tracks all hook executions, errors, and system events. This documentation explains the logging directory structure, configuration, and best practices for working with the logging system.

## Table of Contents

1. [Logging Configuration](#logging-configuration)
2. [Directory Structure](#directory-structure)
3. [Hook Logging Patterns](#hook-logging-patterns)
4. [Log File Types](#log-file-types)
5. [Troubleshooting Guide](#troubleshooting-guide)
6. [Configuration Examples](#configuration-examples)

---

## Logging Configuration

### Environment Variable Configuration

The logging system is configured through the `.env.claude` file (or `.env` as fallback) using the `AI_DATA` environment variable:

```bash
# .env.claude or .env
AI_DATA=logs
```

### Path Resolution Function

The `get_ai_data_path()` utility function from `utils/env_loader.py` handles path resolution:

```python
from utils.env_loader import get_ai_data_path

# Get the configured AI_DATA path
log_dir = get_ai_data_path()
# Returns: /home/user/project/logs (absolute path)
```

**Key Features:**
- **Default Fallback**: Falls back to `logs` directory if `AI_DATA` not set
- **Relative to Project Root**: Always resolves paths relative to project root, not current working directory
- **Auto-Creation**: Automatically creates the directory if it doesn't exist
- **Absolute Paths**: Converts relative paths to absolute for consistency

**Source Code Reference:**
- File: `.claude/hooks/utils/env_loader.py`
- Lines: 44-63

```python
def get_ai_data_path():
    """
    Get the AI_DATA path from .env.claude file.
    Falls back to 'logs' if not set.
    Always relative to project root, not current working directory.
    """
    # Get AI_DATA from environment, default to 'logs'
    ai_data_path = os.getenv('AI_DATA', 'logs')

    # Convert to Path object and ensure it's absolute
    if not os.path.isabs(ai_data_path):
        ai_data_path = PROJECT_ROOT / ai_data_path
    else:
        ai_data_path = Path(ai_data_path)

    # Ensure the directory exists
    ai_data_path.mkdir(parents=True, exist_ok=True)

    return ai_data_path
```

---

## Directory Structure

### Project Root Logging Layout

```
project-root/
├── logs/                          # Main application logs (AI_DATA path)
│   ├── backend.log               # Backend application logs
│   ├── frontend.log              # Frontend application logs
│   ├── session_start             # Session start hook logs
│   ├── session_start_active_tasks_debug.log
│   ├── session_start_mcp_context_debug.log
│   ├── notification.json         # Notification system logs
│   ├── status_line.json          # Status line updates
│   ├── stop.json                 # Stop hook logs
│   ├── subagent_stop.json        # Subagent termination logs
│   │
│   └── claude-hooks/             # Hook system logs (isolated)
│       ├── pre_tool_use.json     # Pre-tool hook execution logs
│       ├── post_tool_use.json    # Post-tool hook execution logs
│       ├── session_start         # Session start detailed logs
│       ├── user_prompt_submit.json
│       └── agent_state.json      # Agent state tracking
```

### Separation of Concerns

The logging architecture follows a clear separation:

1. **Application Logs** (`logs/`): Runtime logs for backend, frontend, and Docker services
2. **Hook System Logs** (`logs/claude-hooks/`): All hook execution logs, isolated from application logs

**Benefits:**
- **Clear Organization**: Hook logs don't interfere with application logs
- **Easy Debugging**: Find hook-specific issues in dedicated subdirectory
- **Performance**: Reduced file size per log category
- **Maintenance**: Easier to clean up or archive specific log types

---

## Hook Logging Patterns

### Pattern 1: FileLogger Class (Recommended)

The `FileLogger` class provides a structured, JSON-based logging interface used by the refactored hooks.

**Implementation Example** (from `post_tool_use.py:70-106`):

```python
class FileLogger(Logger):
    """File-based logger implementation."""

    def __init__(self, log_dir: Path, log_name: str):
        self.log_dir = log_dir
        self.log_name = log_name
        self.log_path = log_dir / f"{log_name}.json"
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def log(self, level: str, message: str, data: Optional[Dict] = None):
        """Log to JSON file."""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message,
            'data': data
        }

        # Load existing log
        log_data = []
        if self.log_path.exists():
            try:
                with open(self.log_path, 'r') as f:
                    log_data = json.load(f)
            except:
                pass

        # Append and save
        log_data.append(entry)

        # Keep only last 100 entries
        if len(log_data) > 100:
            log_data = log_data[-100:]

        with open(self.log_path, 'w') as f:
            json.dump(log_data, f, indent=2)
```

**Usage:**

```python
from utils.env_loader import get_ai_data_path

# Initialize logger
log_dir = get_ai_data_path() / 'claude-hooks'
logger = FileLogger(log_dir, 'post_tool_use')

# Log messages
logger.log('info', 'Processing tool execution')
logger.log('error', 'Failed to update context', {'error': str(e)})
```

**Features:**
- **JSON Format**: Structured logging with timestamps and severity levels
- **Auto-Rotation**: Keeps only last 100 entries to prevent unbounded growth
- **Error Handling**: Gracefully handles corrupted log files
- **Nested Data**: Supports complex data structures in the `data` field

### Pattern 2: Direct Path Writing (Legacy Pattern)

Some hooks write directly to log paths for specific use cases:

```python
from utils.env_loader import get_ai_data_path

log_dir = get_ai_data_path() / 'claude-hooks'
log_path = log_dir / 'custom_log.json'

# Ensure directory exists
log_dir.mkdir(parents=True, exist_ok=True)

# Write log data
with open(log_path, 'w') as f:
    json.dump(log_data, f, indent=2)
```

**When to Use:**
- Simple one-time writes
- Custom log formats not fitting `FileLogger` interface
- Performance-critical operations (avoid object overhead)

### Pattern 3: Debug Logging (Conditional)

Debug logs are created only when `APP_LOG_LEVEL=DEBUG` is set in environment:

```python
import os
import logging
from utils.env_loader import get_ai_data_path

DEBUG_ENABLED = os.getenv('APP_LOG_LEVEL', '').upper() == 'DEBUG'

if DEBUG_ENABLED:
    log_dir = get_ai_data_path()
    debug_log = log_dir / 'session_start_mcp_context_debug.log'

    logger = logging.getLogger('session_start.mcp_context')
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        handler = logging.FileHandler(debug_log)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
```

**Example Usage** (from `session_start.py:690-835`):

```python
# Only log if debug is enabled
if logger:
    logger.debug(f"_query_active_tasks called with git_branch_id: {git_branch_id}")
    logger.debug(f"Response status code: {response.status_code}")
    logger.debug(f"Parsed result structure: {type(result)}")
```

**Benefits:**
- **Production Performance**: No debug overhead in production
- **Detailed Troubleshooting**: Rich diagnostic information when needed
- **Selective Activation**: Enable/disable without code changes

---

## Log File Types

### Hook System Logs (`logs/claude-hooks/`)

| File | Purpose | Format | Rotation |
|------|---------|--------|----------|
| `pre_tool_use.json` | File system protection validations | JSON | Last 100 |
| `post_tool_use.json` | Documentation updates, context sync | JSON | Last 100 |
| `session_start` | Session initialization details | JSON | Last 100 |
| `user_prompt_submit.json` | User input submissions | JSON | Last 100 |
| `agent_state.json` | Agent loading and transitions | JSON | Last 100 |

### Application Logs (`logs/`)

| File | Purpose | Format | Notes |
|------|---------|--------|-------|
| `backend.log` | Backend server runtime logs | Text | Application managed |
| `frontend.log` | Frontend build and runtime logs | Text | Application managed |
| `session_start` | Hook session details | JSON | Hook managed |
| `notification.json` | System notifications | JSON | Hook managed |
| `status_line.json` | Status line updates | JSON | Hook managed |
| `stop.json` | Stop hook executions | JSON | Hook managed |

### Debug Logs (Conditional)

| File | Trigger | Purpose |
|------|---------|---------|
| `session_start_mcp_context_debug.log` | `APP_LOG_LEVEL=DEBUG` | MCP context loading diagnostics |
| `session_start_active_tasks_debug.log` | `APP_LOG_LEVEL=DEBUG` | Active task query diagnostics |
| `pre_tool_use_errors.log` | Error occurs | Pre-tool hook errors |
| `post_tool_use_errors.log` | Error occurs | Post-tool hook errors |

---

## Troubleshooting Guide

### Issue 1: Logs Not Being Created

**Symptoms:**
- Expected log files not appearing in `logs/` directory
- Hook operations seem to run but no logs generated

**Diagnosis:**

```bash
# Check if AI_DATA is configured
cat .env.claude | grep AI_DATA
# or
cat .env | grep AI_DATA

# Check permissions on logs directory
ls -la logs/

# Verify project root detection
python3 -c "from pathlib import Path; from .claude.hooks.utils.env_loader import get_ai_data_path; print(get_ai_data_path())"
```

**Solutions:**

1. **Set AI_DATA in environment file:**
   ```bash
   echo "AI_DATA=logs" >> .env.claude
   ```

2. **Check directory permissions:**
   ```bash
   chmod 755 logs/
   chmod 755 logs/claude-hooks/
   ```

3. **Manual directory creation:**
   ```bash
   mkdir -p logs/claude-hooks
   ```

### Issue 2: Wrong Log Location

**Symptoms:**
- Logs appearing in unexpected directory
- Multiple `logs/` directories in different locations

**Diagnosis:**

```python
# Check actual path resolution
from .claude.hooks.utils.env_loader import get_ai_data_path, PROJECT_ROOT

print(f"Project Root: {PROJECT_ROOT}")
print(f"AI_DATA Path: {get_ai_data_path()}")
```

**Root Cause:**
- `AI_DATA` set to absolute path instead of relative
- Working directory different from project root

**Solutions:**

1. **Use relative paths in configuration:**
   ```bash
   # ✅ CORRECT - relative to project root
   AI_DATA=logs

   # ❌ WRONG - absolute path
   AI_DATA=/home/user/some/other/location/logs
   ```

2. **Verify project root detection:**
   - Hook system uses `.env.claude` or `.git` directory as markers
   - Ensure one of these exists at project root

### Issue 3: Debug Logs Not Appearing

**Symptoms:**
- `*_debug.log` files not created
- No detailed diagnostic information available

**Diagnosis:**

```bash
# Check log level configuration
env | grep APP_LOG_LEVEL

# Check if debug logs are being created
ls -la logs/*debug.log
```

**Solutions:**

1. **Enable debug logging:**
   ```bash
   # In .env or .env.claude
   APP_LOG_LEVEL=DEBUG
   ```

2. **Restart Claude Code session:**
   - Debug logging is checked at hook initialization
   - Changes require new session to take effect

### Issue 4: Log Files Growing Too Large

**Symptoms:**
- JSON log files exceeding several MB
- Slow log file operations

**Root Cause:**
- `FileLogger` rotation not working (keeps more than 100 entries)
- Custom logging without rotation

**Solutions:**

1. **Verify FileLogger usage:**
   - Check if hooks use `FileLogger` class (auto-rotates at 100 entries)
   - Legacy direct writes may not have rotation

2. **Manual cleanup:**
   ```bash
   # Archive old logs
   tar -czf logs-archive-$(date +%Y%m%d).tar.gz logs/

   # Clear log files
   rm logs/claude-hooks/*.json
   rm logs/*.log
   ```

3. **Automated cleanup script:**
   ```bash
   # Keep only last 7 days of logs
   find logs/ -type f -name "*.log" -mtime +7 -delete
   find logs/ -type f -name "*.json" -mtime +7 -delete
   ```

### Issue 5: Permission Denied Errors

**Symptoms:**
- Hooks fail silently
- Error logs show permission denied

**Diagnosis:**

```bash
# Check ownership and permissions
ls -la logs/
ls -la logs/claude-hooks/

# Check process user
whoami
```

**Solutions:**

1. **Fix ownership:**
   ```bash
   # Make current user owner
   chown -R $(whoami):$(whoami) logs/
   ```

2. **Fix permissions:**
   ```bash
   # Read/write for owner, read for group
   chmod -R 755 logs/
   ```

---

## Configuration Examples

### Example 1: Default Development Setup

```bash
# .env.claude
AI_DATA=logs
APP_LOG_LEVEL=DEBUG
```

**Result:**
- Logs in `project-root/logs/`
- Hook logs in `project-root/logs/claude-hooks/`
- Debug logs enabled for troubleshooting

### Example 2: Production Setup

```bash
# .env
AI_DATA=logs
APP_LOG_LEVEL=WARNING
```

**Result:**
- Logs in `project-root/logs/`
- Hook logs in `project-root/logs/claude-hooks/`
- Debug logs disabled (performance optimization)
- Only warnings and errors logged

### Example 3: Custom Log Location

```bash
# .env.claude
AI_DATA=/var/log/claude-agent
APP_LOG_LEVEL=INFO
```

**Result:**
- Logs in `/var/log/claude-agent/`
- Hook logs in `/var/log/claude-agent/claude-hooks/`
- Info-level logging (balanced verbosity)

**Note:** Ensure absolute paths have proper permissions

### Example 4: Multi-Environment Setup

```bash
# .env.dev (development)
AI_DATA=logs/dev
APP_LOG_LEVEL=DEBUG

# .env.staging (staging)
AI_DATA=logs/staging
APP_LOG_LEVEL=INFO

# .env.prod (production)
AI_DATA=/var/log/claude-agent
APP_LOG_LEVEL=ERROR
```

**Usage:**
```bash
# Load specific environment
ln -sf .env.dev .env.claude
```

---

## Code Reference Summary

### Key Files and Functions

| File | Function/Class | Purpose |
|------|---------------|---------|
| `utils/env_loader.py:44-63` | `get_ai_data_path()` | Path resolution with fallback |
| `utils/env_loader.py:85-103` | `get_log_path()` | Alternative log path getter |
| `post_tool_use.py:70-106` | `FileLogger` | JSON logging with rotation |
| `session_start.py:139-175` | `FileLogger` | Session logging implementation |
| `session_start.py:690-835` | `_query_active_tasks()` | Debug logging example |

### Hook Initialization Examples

**Post Tool Use Hook** (`post_tool_use.py:274-292`):

```python
def __init__(self):
    # Get paths
    from utils.env_loader import get_ai_data_path

    self.log_dir = get_ai_data_path()
    self.ai_docs_path = PROJECT_ROOT / 'ai_docs'

    # Create components using factory
    self.factory = ComponentFactory()
    self.logger = self.factory.create_logger(self.log_dir)
```

**Session Start Hook** (`session_start.py:1770-1787`):

```python
def __init__(self):
    # Get paths
    from utils.env_loader import get_ai_data_path

    self.log_dir = get_ai_data_path()
    self.config_dir = Path(__file__).parent / 'config'

    # Create components using factory
    self.factory = ComponentFactory()
    self.logger = self.factory.create_logger(self.log_dir)
```

---

## Best Practices

### For Hook Developers

1. **Always use `get_ai_data_path()`** instead of hardcoded paths
2. **Use `FileLogger` class** for structured logging
3. **Create subdirectories** for hook-specific logs (e.g., `claude-hooks/`)
4. **Implement log rotation** to prevent unbounded growth
5. **Use conditional debug logging** with `APP_LOG_LEVEL` check
6. **Handle errors gracefully** - don't fail hooks due to logging errors

### For System Administrators

1. **Monitor log directory size** regularly
2. **Implement log rotation** or archival strategy
3. **Set appropriate `APP_LOG_LEVEL`** for environment
4. **Use relative paths** in `AI_DATA` configuration
5. **Ensure proper permissions** on log directories

### For Troubleshooting

1. **Start with session logs** (`logs/session_start`)
2. **Enable debug logging** temporarily for diagnostics
3. **Check error logs** first (`*_errors.log` files)
4. **Verify configuration** with `get_ai_data_path()` directly
5. **Review recent entries** in JSON logs (last 100 auto-kept)

---

## Related Documentation

- [Environment Configuration Guide](../setup-guides/environment-configuration.md)
- [Hook System Architecture](./hook-system-architecture.md)
- [Troubleshooting Claude Hooks](../troubleshooting-guides/claude-hooks-issues.md)

---

**Last Updated:** 2025-10-09
**Document Version:** 1.0
**Maintained By:** Documentation Agent
