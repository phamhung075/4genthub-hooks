# Claude Code Hooks - Complete Reference

## Quick Reference

| Hook | When | Common Use | Block Capability |
|------|------|-----------|------------------|
| `SessionStart` | Session begins | Load context, check status | No |
| `UserPromptSubmit` | User sends prompt | Add context, validate | Yes (exit 2) |
| `PreToolUse` | Before tool runs | Validate, block dangerous ops | Yes (deny) |
| `PostToolUse` | After tool completes | Update docs, sync context | Feedback only |
| `Stop`/`SubagentStop` | Agent finishing | Continue work, add tasks | Yes (block) |
| `Notification` | System notifications | Log, external alerts | No |
| `PreCompact` | Before context compact | Save state | No |
| `SessionEnd` | Session terminating | Cleanup, logging | No |

---

## Configuration

### Settings File Location
```json
// ~/.claude/settings.json OR .claude/settings.json
{
  "hooks": {
    "EventName": [{
      "matcher": "ToolPattern",  // Only for PreToolUse/PostToolUse
      "hooks": [{
        "type": "command",
        "command": "your-command",
        "timeout": 60000  // Optional, milliseconds
      }]
    }]
  }
}
```

### Matcher Patterns
- **Exact match**: `"Write"` → Only Write tool
- **Regex**: `"Edit|Write"`, `"Bash:git.*"`
- **All tools**: `"*"` or `""` or omit `matcher`
- **MCP tools**: `"mcp__<server>__<tool>"` (e.g., `"mcp__memory__.*"`)

### Project Scripts
Use `$CLAUDE_PROJECT_DIR` for portable paths:
```json
{
  "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/check-style.sh"
}
```

---

## Hook Input/Output

### Input Structure (All Hooks)
```json
{
  "session_id": "abc123",
  "transcript_path": "~/.claude/projects/.../session.jsonl",
  "cwd": "/current/working/directory",
  "hook_event_name": "PreToolUse"
  // ... hook-specific fields
}
```

### Output Methods

**1. Exit Codes**
- `0`: Success, stdout shown to user (UserPromptSubmit/SessionStart add to context)
- `2`: Block operation, stderr shown to Claude
- `Other`: Non-blocking error, stderr to user only

**2. JSON Output** (Advanced)
```json
{
  "continue": false,  // Stop processing (overrides decision)
  "stopReason": "Reason shown to user",
  "suppressOutput": true,  // Hide from transcript
  "systemMessage": "Warning shown to user",
  "hookSpecificOutput": { /* varies by hook */ }
}
```

---

## Hook-Specific Details

### PreToolUse

**Input**: `tool_name`, `tool_input`
**Block Method**: Exit 2 OR `permissionDecision: "deny"`

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow" | "deny" | "ask",
    "permissionDecisionReason": "Explanation"
  }
}
```

**Example**: Block grep, suggest ripgrep
```python
#!/usr/bin/env python3
import json, sys

data = json.load(sys.stdin)
if data.get("tool_name") == "Bash" and "grep" in data.get("tool_input", {}).get("command", ""):
    print("Use 'rg' instead of 'grep' for better performance", file=sys.stderr)
    sys.exit(2)
```

### PostToolUse

**Input**: `tool_name`, `tool_input`, `tool_response`
**Feedback**: `decision: "block"` provides automatic feedback

```json
{
  "decision": "block",  // Prompts Claude with reason
  "reason": "Explanation",
  "hookSpecificOutput": {
    "hookEventName": "PostToolUse",
    "additionalContext": "Info for Claude"
  }
}
```

### UserPromptSubmit

**Input**: `prompt`
**Block**: `decision: "block"` prevents processing, erases prompt

```json
{
  "decision": "block",  // Erases prompt
  "reason": "Shown to user only",
  "hookSpecificOutput": {
    "hookEventName": "UserPromptSubmit",
    "additionalContext": "Added to context if not blocked"
  }
}
```

### Stop/SubagentStop

**Input**: `stop_hook_active` (boolean)
**Block**: `decision: "block"` + `reason` for how to continue

```json
{
  "decision": "block",  // Prevent stopping
  "reason": "Must complete X before stopping"
}
```

### SessionStart

**Input**: `source` (startup|resume|clear|compact)
**Context Injection**: `additionalContext` added to session

```json
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "Session context here"
  }
}
```

### SessionEnd

**Input**: `reason` (clear|logout|prompt_input_exit|other)
**No blocking capability** - cleanup only

---

## Architecture

### Directory Structure
```
.claude/hooks/
├── pre_tool_use.py          # File protection, validation
├── post_tool_use.py         # Doc indexing, context sync
├── session_start.py         # Session initialization
├── user_prompt_submit.py    # Prompt processing
├── stop.py                  # Session cleanup
├── utils/                   # Core utilities
│   ├── env_loader.py        # Environment config
│   ├── config_factory.py    # Message management
│   ├── docs_indexer.py      # Auto-documentation
│   ├── session_tracker.py   # 2-hour work sessions
│   ├── mcp_client.py        # MCP server connection
│   └── context_injector.py  # Context management
└── config/                  # YAML configurations
```

### Execution Flow
```
SessionStart → UserPromptSubmit → PreToolUse → Tool Execution → PostToolUse → Stop
```

### Core Components

**File Protection** (`pre_tool_use.py`)
- Blocks unauthorized root file creation
- Enforces documentation requirements
- Validates test file locations
- Prevents dangerous commands

**Documentation System** (`post_tool_use.py`)
- Auto-updates `ai_docs/index.json`
- Moves docs to `_obsolete_docs` when source deleted
- Tracks file hashes for change detection

**Session Tracking** (`utils/session_tracker.py`)
- 2-hour sessions prevent documentation disruption
- Allows edits without constant doc updates
- Auto-expires after session timeout

---

## Logging

### Configuration
```bash
# .env.claude
AI_DATA=logs/claude-hooks
APP_LOG_LEVEL=DEBUG  # Optional: DEBUG|INFO|WARNING|ERROR
```

### Log Structure
```
logs/claude-hooks/
├── pre_tool_use.json        # Validation logs
├── post_tool_use.json       # Documentation updates
├── session_start            # Session initialization
├── user_prompt_submit.json  # Prompt processing
└── agent_state.json         # Agent transitions
```

### Logger Pattern
```python
from utils.env_loader import get_ai_data_path

class FileLogger:
    def __init__(self, log_dir, log_name):
        self.log_path = log_dir / f"{log_name}.json"

    def log(self, level, message, data=None):
        entry = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message,
            'data': data
        }
        # Auto-rotates to last 100 entries
```

---

## MCP Integration

### Tool Naming
`mcp__<server>__<tool>` (e.g., `mcp__memory__create_entities`)

### Hook Configuration
```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "mcp__memory__.*",  // All memory server tools
      "hooks": [{
        "type": "command",
        "command": "echo 'Memory op' >> ~/mcp-ops.log"
      }]
    }]
  }
}
```

### Query Methods

**HTTP Client** (`utils/mcp_client.py`)
```python
from utils.mcp_client import get_default_client

client = get_default_client()
tasks = client.query_pending_tasks(limit=5)
context = client.query_project_context(project_id="uuid")
```

**Session Functions** (cached)
```python
from session_start import query_mcp_pending_tasks
pending = query_mcp_pending_tasks()
```

---

## Security & Best Practices

### Security Rules
1. **Validate inputs** - Never trust data blindly
2. **Quote variables** - Always use `"$VAR"` not `$VAR`
3. **Block path traversal** - Check for `..` in paths
4. **Use absolute paths** - Leverage `$CLAUDE_PROJECT_DIR`
5. **Skip sensitive files** - Avoid `.env`, `.git/`, keys

### Hook Development
1. **Error handling** - Wrap in try/except
2. **Logging** - Use appropriate levels
3. **Performance** - Minimize execution time
4. **Testing** - Write unit tests
5. **Documentation** - Document inputs/outputs

### Configuration Safety
- Settings snapshot captured at startup
- External changes require `/hooks` menu review
- Prevents malicious mid-session modifications

---

## Execution Details

| Aspect | Behavior |
|--------|----------|
| **Timeout** | 60s default, configurable per command |
| **Parallelization** | All matching hooks run in parallel |
| **Deduplication** | Identical commands auto-deduplicated |
| **Environment** | Claude Code's env + `$CLAUDE_PROJECT_DIR` |
| **Output Display** | PreTool/PostTool/Stop: transcript (Ctrl-R)<br>Notification/SessionEnd: debug only<br>UserPrompt/SessionStart: added to context |

---

## Troubleshooting

| Issue | Diagnosis | Solution |
|-------|-----------|----------|
| Hooks not executing | Run `/hooks` to check registration | Verify JSON syntax, check permissions |
| Wrong matcher | Tool names are case-sensitive | Use exact tool names |
| Command not found | Scripts not in PATH | Use full paths with `$CLAUDE_PROJECT_DIR` |
| Permission errors | Scripts not executable | `chmod +x script.sh` |
| Logs missing | `AI_DATA` not set | Set in `.env.claude` |
| Debug logs missing | `APP_LOG_LEVEL` not DEBUG | Set `APP_LOG_LEVEL=DEBUG` |

**Debug Mode**: `claude --debug` shows detailed hook execution

---

## Examples

### Auto-approve Documentation Reads
```python
#!/usr/bin/env python3
import json, sys

data = json.load(sys.stdin)
if data.get("tool_name") == "Read" and data.get("tool_input", {}).get("file_path", "").endswith((".md", ".txt")):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "allow",
            "permissionDecisionReason": "Docs auto-approved"
        },
        "suppressOutput": True
    }))
    sys.exit(0)
```

### Add Time Context to Prompts
```python
#!/usr/bin/env python3
import datetime, sys
print(f"Current time: {datetime.datetime.now()}")
sys.exit(0)
```

### Block Sensitive Pattern Detection
```python
#!/usr/bin/env python3
import json, sys, re

data = json.load(sys.stdin)
prompt = data.get("prompt", "")

if re.search(r"(?i)\b(password|secret|key)\s*[:=]", prompt):
    print(json.dumps({
        "decision": "block",
        "reason": "Security policy: Prompt contains potential secrets"
    }))
    sys.exit(0)
```

---

## Related Resources
- [Claude Code Documentation](https://docs.claude.com/en/docs/claude-code)
- [MCP Protocol](https://docs.claude.com/en/docs/claude-code/mcp)
- [Settings Reference](https://docs.claude.com/en/docs/claude-code/settings)
