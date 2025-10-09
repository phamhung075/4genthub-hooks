# Claude Hook Logging Structure

**Document Status**: ✅ Verified
**Last Updated**: 2025-10-09
**Verification Task**: 625f03c6-61b4-457e-9871-cacc5a3c45f1

## Overview

All Claude Code hook files write logs to a centralized location configured via the `.env.claude` file. This document describes the verified logging structure and configuration.

## Configuration

### Environment Variable
```bash
# .env.claude
AI_DATA=logs/claude-hooks
```

### Path Resolution
The `get_ai_data_path()` function from `utils/env_loader.py` resolves to:
```
/home/daihungpham/__projects__/4genthub/logs/claude-hooks
```

## Directory Structure

```
logs/                               # Application logs only
├── backend.log                     # Backend application logs
├── frontend.log                    # Frontend application logs
├── mcp_client_auth_debug.log      # MCP authentication debugging
├── mcp_connection_cache.json      # MCP connection cache
└── claude-hooks/                   # All Claude hook logs (AI_DATA)
    ├── agent_state.json            # Agent state tracking
    ├── post_tool_use.json          # Post-tool execution logs
    ├── pre_tool_use.json           # Pre-tool execution logs
    ├── user_prompt_submit.json     # User prompt submission logs
    ├── session_start               # Session start logs
    └── [additional hook logs]      # Other hook log files
```

## Verified Hook Files

All hook files have been verified to use `get_ai_data_path()` for logging:

### ✅ Core Hooks (Verified)
| Hook File | Log Location | Status | Implementation |
|-----------|-------------|--------|----------------|
| `pre_tool_use.py` | `logs/claude-hooks/pre_tool_use.json` | ✅ Correct | Uses `get_ai_data_path()` |
| `post_tool_use.py` | `logs/claude-hooks/post_tool_use.json` | ✅ Correct | Uses `get_ai_data_path()` |
| `user_prompt_submit.py` | `logs/claude-hooks/user_prompt_submit.json` | ✅ Correct | Uses `get_ai_data_path()` |
| `notification.py` | `logs/claude-hooks/notification.json` | ✅ Correct | Uses `get_ai_data_path()` |
| `pre_compact.py` | `logs/claude-hooks/pre_compact.json` | ✅ Correct | Uses `get_ai_data_path()` |
| `stop.py` | `logs/claude-hooks/stop.json` | ✅ Correct | Uses `get_ai_data_path()` |
| `subagent_stop.py` | `logs/claude-hooks/subagent_stop.json` | ✅ Correct | Uses `get_ai_data_path()` |
| `session_start.py` | `logs/claude-hooks/session_start` | ✅ Correct | Uses `get_ai_data_path()` |

### ✅ Utility Hooks (Verified)
| Utility File | Log Location | Status |
|-------------|-------------|--------|
| `utils/agent_state_manager.py` | `logs/claude-hooks/agent_state.json` | ✅ Correct |
| `status_lines/status_line.py` | `logs/claude-hooks/status_line.json` | ✅ Correct |

## Implementation Pattern

All hooks follow the same implementation pattern:

```python
#!/usr/bin/env python3
import sys
from pathlib import Path

# Import the AI_DATA path loader
sys.path.insert(0, str(Path(__file__).parent))
from utils.env_loader import get_ai_data_path

def main():
    # Get AI_DATA path from environment
    log_dir = get_ai_data_path()
    log_file = log_dir / 'hook_name.json'

    # Write logs to the resolved path
    # ...
```

## Verification Results (2025-10-09)

### ✅ Current Status
- **Configuration**: `.env.claude` correctly set to `AI_DATA=logs/claude-hooks`
- **Path Resolution**: `get_ai_data_path()` returns correct path
- **Hook Implementation**: All hooks use `get_ai_data_path()` consistently
- **Recent Logs**: All new logs (11:50-11:52) written to `logs/claude-hooks/`

### ⚠️ Legacy Files Found
The following files were found in the root `logs/` directory (old logs from before configuration fix):

| File | Last Modified | Action Needed |
|------|--------------|---------------|
| `notification.json` | 2025-10-09 11:49:27 | Remove (obsolete) |
| `pre_compact.json` | 2025-10-09 03:53:36 | Remove (obsolete) |
| `status_line.json` | 2025-10-09 11:50:43 | Remove (obsolete) |
| `stop.json` | 2025-10-09 11:49:21 | Remove (obsolete) |
| `subagent_stop.json` | 2025-10-09 03:25:45 | Remove (obsolete) |
| `session_start` | 2025-10-09 11:49:46 | Remove (obsolete) |
| `session_start_*_debug.log` | Various | Remove (obsolete) |

**Note**: These files are from sessions BEFORE the `.env.claude` configuration was properly set. Current hooks are writing to the correct location.

## Cleanup Recommendation

To maintain a clean logging structure, remove the legacy hook log files from the root `logs/` directory:

```bash
# Remove obsolete hook logs from root logs/ directory
cd /home/daihungpham/__projects__/4genthub/logs
rm -f notification.json pre_compact.json status_line.json stop.json subagent_stop.json session_start session_start_*_debug.log
```

**Important**: Keep application logs (`backend.log`, `frontend.log`, `mcp_*.log`, `mcp_*.json`)

## Testing the Configuration

To verify the logging configuration is working correctly:

```bash
# Test get_ai_data_path() returns correct path
python3 -c "
import sys
from pathlib import Path
sys.path.insert(0, '/home/daihungpham/__projects__/4genthub/.claude/hooks')
from utils.env_loader import get_ai_data_path
print(f'AI_DATA resolves to: {get_ai_data_path()}')
"

# Expected output:
# AI_DATA resolves to: /home/daihungpham/__projects__/4genthub/logs/claude-hooks
```

## Related Documentation
- [Environment Configuration](../setup-guides/environment-configuration.md)
- [Hook System Architecture](./hook-system-architecture.md)
- [Logging Best Practices](../development-guides/logging-best-practices.md)

## Troubleshooting

### Problem: Hooks writing to wrong location
**Cause**: `.env.claude` not loaded or `AI_DATA` not set
**Solution**: Ensure `.env.claude` exists with `AI_DATA=logs/claude-hooks`

### Problem: Permission denied when creating log directory
**Cause**: Insufficient permissions for `logs/claude-hooks/`
**Solution**: `mkdir -p logs/claude-hooks && chmod 755 logs/claude-hooks`

### Problem: Old log files in root logs/ directory
**Cause**: Legacy files from before configuration fix
**Solution**: Safely remove old hook logs (keep application logs)

## Conclusion

✅ **All Claude hook files are verified to write logs to the correct location** (`logs/claude-hooks/`)
✅ **Configuration is correctly set** via `.env.claude`
✅ **Implementation is consistent** across all hook files using `get_ai_data_path()`
⚠️ **Cleanup recommended** to remove obsolete log files from root `logs/` directory
