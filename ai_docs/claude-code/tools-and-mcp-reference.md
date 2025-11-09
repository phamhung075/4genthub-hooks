# Claude Code Tools & MCP Reference

## Core Tools (12)

| Tool | Signature | Purpose |
|------|-----------|---------|
| `Task` | `(description, prompt, subagent_type)` | Launch specialized agents for complex tasks |
| `Bash` | `(command, description?, run_in_background?, timeout?)` | Execute shell commands with persistent session |
| `Glob` | `(pattern, path?)` | Fast file pattern matching |
| `Grep` | `(pattern, path?, glob?, type?, output_mode?, -A?, -B?, -C?, -i?, -n?, multiline?, head_limit?)` | Search file contents with ripgrep |
| `Read` | `(file_path, limit?, offset?)` | Read files (text, images, PDFs, notebooks) |
| `Edit` | `(file_path, old_string, new_string, replace_all?)` | Exact string replacement in files |
| `MultiEdit` | `(file_path, edits[])` | Multiple edits to single file |
| `Write` | `(file_path, content)` | Write/overwrite file |
| `WebFetch` | `(url, prompt)` | Fetch and analyze web content |
| `WebSearch` | `(query, allowed_domains?, blocked_domains?)` | Search web for current info |
| `TodoWrite` | `(todos[{content, status, activeForm}])` | Track task progress |
| `ExitPlanMode` | `(plan)` | Exit planning mode with implementation plan |

---

## File Operations (2)

| Tool | Format |
|------|--------|
| `NotebookEdit` | `(notebook_path, new_source, cell_id?, cell_type?, edit_mode?)` |
| Process Mgmt | `BashOutput(bash_id, filter?)`, `KillShell(shell_id)` |

---

## AgentHub MCP Tools (8)

### Task Management
```typescript
// Task CRUD + workflow
mcp__agenthub_http__manage_task(
  action: "create|update|get|delete|complete|list|search|next",
  git_branch_id?, title?, assignees?, details?, ...
)

// Subtask hierarchy
mcp__agenthub_http__manage_subtask(
  action: "create|update|get|delete|complete|list",
  task_id, subtask_id?, title?, progress_notes?, ...
)

// 4-tier context (Global→Project→Branch→Task)
mcp__agenthub_http__manage_context(
  action: "create|get|update|delete|resolve|delegate",
  level: "global|project|branch|task",
  context_id?, data?, ...
)
```

### Project & Agent Management
```typescript
// Projects
mcp__agenthub_http__manage_project(
  action: "create|get|list|update|delete|project_health_check",
  project_id?, name?, ...
)

// Git branches
mcp__agenthub_http__manage_git_branch(
  action: "create|get|list|update|delete|assign_agent|get_statistics",
  project_id, git_branch_id?, git_branch_name?, ...
)

// 33 specialized agents
mcp__agenthub_http__manage_agent(
  action: "register|assign|get|list|update|unassign",
  project_id, agent_id?, name?, ...
)

// Load agent capabilities
mcp__agenthub_http__call_agent(name_agent: string)

// System health
mcp__agenthub_http__manage_connection(include_details?, user_id?)
```

---

## AI & UI Tools (9)

### Sequential Thinking
```typescript
mcp__sequential-thinking__sequentialthinking(
  thought: string,
  nextThoughtNeeded: boolean,
  thoughtNumber: number,
  totalThoughts: number,
  isRevision?, revisesThought?, branchId?, ...
)
```

### shadcn/ui Components
```typescript
mcp__shadcn-ui-server__list-components()
mcp__shadcn-ui-server__get-component-docs(component: string)
mcp__shadcn-ui-server__install-component(component: string, runtime?: string)
mcp__shadcn-ui-server__list-blocks()
mcp__shadcn-ui-server__get-block-docs(block: string)
mcp__shadcn-ui-server__install-blocks(block: string, runtime?: string)
```

### IDE Integration
```typescript
mcp__ide__getDiagnostics(uri?: string)  // VS Code diagnostics
mcp__ide__executeCode(code: string)     // Jupyter Python execution
```

---

## Browser Automation (12)

| Category | Tools |
|----------|-------|
| **Navigation** | `browser_navigate(url)`, `browser_go_back()`, `browser_go_forward()` |
| **Inspection** | `browser_snapshot()`, `browser_screenshot()`, `browser_get_console_logs()` |
| **Interaction** | `browser_click(element, ref)`, `browser_hover(element, ref)`, `browser_type(element, ref, text, submit)`, `browser_select_option(element, ref, values[])`, `browser_press_key(key)` |
| **Utilities** | `browser_wait(time)` |

All tools prefixed: `mcp__browsermcp__`

---

## ElevenLabs Audio (26 tools)

### Text-to-Speech & Effects
```typescript
mcp__ElevenLabs__text_to_speech(text, voice_name?, model_id?, ...)
mcp__ElevenLabs__text_to_voice(voice_description, text?, output_directory?)
mcp__ElevenLabs__text_to_sound_effects(text, duration_seconds?, loop?, ...)
```

### Speech Processing
```typescript
mcp__ElevenLabs__speech_to_text(input_file_path, language_code?, diarize?, ...)
mcp__ElevenLabs__speech_to_speech(input_file_path, voice_name?, output_directory?)
mcp__ElevenLabs__isolate_audio(input_file_path, output_directory?)
mcp__ElevenLabs__play_audio(input_file_path)
```

### Voice Management
```typescript
mcp__ElevenLabs__search_voices(search?, sort?, sort_direction?)
mcp__ElevenLabs__list_models()
mcp__ElevenLabs__get_voice(voice_id)
mcp__ElevenLabs__voice_clone(name, files[], description?)
mcp__ElevenLabs__create_voice_from_preview(generated_voice_id, voice_name, voice_description)
mcp__ElevenLabs__search_voice_library(search?, page?, page_size?)
```

### AI Agents & Communication
```typescript
// Conversational agents
mcp__ElevenLabs__create_agent(name, first_message, system_prompt, ...)
mcp__ElevenLabs__add_knowledge_base_to_agent(agent_id, knowledge_base_name, url?, input_file_path?, text?)
mcp__ElevenLabs__list_agents()
mcp__ElevenLabs__get_agent(agent_id)
mcp__ElevenLabs__get_conversation(conversation_id)
mcp__ElevenLabs__list_conversations(agent_id?, cursor?, ...)

// Phone calls
mcp__ElevenLabs__make_outbound_call(agent_id, agent_phone_number_id, to_number)
mcp__ElevenLabs__list_phone_numbers()
```

### Music Generation
```typescript
mcp__ElevenLabs__compose_music(prompt?, composition_plan?, music_length_ms?, output_directory?)
mcp__ElevenLabs__create_composition_plan(prompt, music_length_ms?, source_composition_plan?)
```

### Account
```typescript
mcp__ElevenLabs__check_subscription()
```

**Note**: Most ElevenLabs tools incur API costs

---

## MCP Resources (2)

```typescript
ListMcpResourcesTool(server?: string)  // List resources from MCP servers
ReadMcpResourceTool(server: string, uri: string)  // Read specific resource
```

---

## MCP Query Integration

### HTTP Client Method (Primary)
```python
from utils.mcp_client import get_default_client

client = get_default_client()

# Task queries
pending = client.query_pending_tasks(limit=5, user_id="user_id")
next_task = client.query_next_task(branch_id="uuid", include_context=True)

# Context queries
context = client.query_project_context(project_id="uuid")
hierarchy = client.query_context_hierarchy(level="task", context_id="uuid")

# Branch queries
branch_data = client.query_git_branch_info(branch_id="uuid")
stats = client.query_branch_statistics(branch_id="uuid")

# Connection
connected = client.test_connection()
```

### Session Functions (Cached)
```python
from session_start import query_mcp_pending_tasks, query_mcp_next_task

pending = query_mcp_pending_tasks()  # Uses cache
next_task = query_mcp_next_task(branch_id="uuid")
```

### Context Injection (Advanced)
```python
from utils.context_injector import ContextInjector

injector = ContextInjector()
context = await injector.query_context({
    'query_type': 'mcp_operation',
    'operation': 'task_management',
    'context_requirements': {
        'include_tasks': True,
        'branch_id': 'uuid'
    }
})
```

### Authentication
```bash
# Environment variables
MCP_SERVER_URL=http://localhost:8000
TOKEN_REFRESH_BEFORE_EXPIRY=60
MCP_REQUEST_TIMEOUT=30
MCP_MAX_RETRIES=3
```

**Token**: Auto-managed via `TokenManager`, stored in `~/.claude/.mcp_token_cache`

### Error Handling Pattern
```python
from utils.mcp_client import get_default_client, MCPAuthenticationError

try:
    client = get_default_client()
    if client and client.test_connection():
        result = client.query_pending_tasks()
except MCPAuthenticationError:
    print("🔐 Auth failed")
except Exception as e:
    print(f"❌ Query failed: {e}")
```

---

## Tool Categories Summary

| Category | Count | Tools |
|----------|-------|-------|
| **Core Dev** | 5 | Task, Bash, Glob, Grep, ExitPlanMode |
| **Files** | 5 | Read, Edit, MultiEdit, Write, NotebookEdit |
| **Web** | 2 | WebFetch, WebSearch |
| **Tasks** | 1 | TodoWrite |
| **Process** | 2 | BashOutput, KillShell |
| **AgentHub** | 8 | Task, subtask, context, project, branch, agent mgmt |
| **AI** | 1 | Sequential thinking |
| **UI** | 6 | shadcn/ui components & blocks |
| **IDE** | 2 | Diagnostics, code execution |
| **Browser** | 12 | Navigation, interaction, utilities |
| **ElevenLabs** | 26 | TTS, STT, voices, agents, music |
| **MCP Resources** | 2 | List/read MCP resources |

**Total: 77 tools**

---

## Tool Usage Best Practices

### Prefer Specialized Tools
```bash
# ❌ BAD - Using bash for file operations
Bash("cat file.txt")
Bash("grep pattern file.txt")

# ✅ GOOD - Using dedicated tools
Read("file.txt")
Grep("pattern", path="file.txt")
```

### MCP Tool Naming Convention
- Pattern: `mcp__<server>__<tool>`
- Example: `mcp__agenthub_http__manage_task`
- Hooks matcher: `"mcp__agenthub.*"` (all AgentHub tools)

### Task Management Flow
```python
# 1. Create task
task = mcp__agenthub_http__manage_task(
    action="create",
    git_branch_id="uuid",
    title="Implement feature X",
    assignees="coding-agent",
    details="Requirements..."
)

# 2. Create subtasks
subtask = mcp__agenthub_http__manage_subtask(
    action="create",
    task_id=task["id"],
    title="Design schema",
    progress_notes="Starting design phase"
)

# 3. Update progress
mcp__agenthub_http__manage_subtask(
    action="update",
    task_id=task["id"],
    subtask_id=subtask["id"],
    progress_percentage=50,
    progress_notes="Schema designed, starting implementation"
)

# 4. Complete
mcp__agenthub_http__manage_subtask(
    action="complete",
    task_id=task["id"],
    subtask_id=subtask["id"],
    completion_summary="Schema complete with indexes",
    progress_notes="All tests passing"
)
```

---

## Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| MCP auth failure | Check `~/.claude/.mcp_token_cache`, verify server running |
| Connection timeout | Increase `MCP_REQUEST_TIMEOUT` |
| Tools not available | Verify MCP server running: `curl http://localhost:8000/health` |
| Cache stale data | Clear cache: `cache.clear()` |
| Permission denied | Check file/directory permissions |

---

## Related Documentation
- [Hooks Complete Guide](./hooks-complete-guide.md)
- [Claude Code Documentation](https://docs.claude.com/en/docs/claude-code)
- [MCP Protocol](https://docs.claude.com/en/docs/claude-code/mcp)
