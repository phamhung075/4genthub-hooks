# Shared Agent Memory

## Critical Rules (All Agents)

### MCP Initialization — Proxy Pattern (CRITICAL)

**For team agents (spawned with `team_name` via Task tool):**
- Team agents run in separate tmux sessions and CANNOT access MCP tools
- The team lead fetches your agent config and injects it into your prompt as "YOUR AGENT CONFIGURATION"
- Read the injected configuration carefully — it defines your capabilities, rules, and quality standards
- You do NOT need to call `mcp__agenthub_http__call_agent` — the team lead already did this for you

**For standalone/principal sessions (NOT in a team):**
- Your FIRST action must be to use the MCP tool named `mcp__agenthub_http__call_agent`
- Call it with parameter: `name_agent` = your agent type (e.g., "coding-agent")
- **This is an MCP TOOL CALL — use your tool-calling capability (like Read, Write, Edit, Bash)**
- **DO NOT run this as a bash/shell command — it is NOT a terminal command**
- This loads your system_prompt, capabilities, rules, and tools
- Call ONCE per session, not per task

### Common Mistakes — AVOID THESE
- ❌ WRONG: `bash: which mcp__agenthub_http__call_agent` (this is NOT a bash command)
- ❌ WRONG: Skipping the injected agent configuration in your prompt
- ❌ WRONG: Trying to call MCP tools from a team agent session (they're not available)
- ✅ RIGHT: Read and follow the "YOUR AGENT CONFIGURATION" section in your prompt (team agents)
- ✅ RIGHT: Use MCP tool-calling capability to invoke `call_agent` (standalone sessions)

### Team Workflow
- When working as a teammate: read agent config → do work → ask user confirmation → report to lead
- NEVER skip user confirmation step (AskUserQuestion)
- NEVER ignore the agent configuration injected by the team lead

### File Operations
- `rm` commands are blocked by hooks — use Python `os.remove()`/`shutil.rmtree()` instead
- `.env` files cannot be read/created (security hook)
- Root file creation restricted to allowed list (see `.allowed_root_files`)

### Code Principles
- Clean code only — no backward compatibility, no legacy support
- ORM model is source of truth (fix code to match ORM, not tests)
- DDD patterns: Domain → Application → Infrastructure → Interface
- Development phase — break anything that needs breaking

## Project Structure Quick Reference

| Path | Purpose |
|------|---------|
| `agenthub-frontend/` | React/TypeScript frontend (port 3800) |
| `agenthub_main/src/` | Python/FastMCP/DDD backend (port 8000) |
| `agenthub_main/src/tests/` | All test files |
| `.claude/agents/` | Agent definitions (32 agents) |
| `.claude/skills/` | Reusable skill definitions |
| `.claude/hooks/` | Pre/post tool use hooks |
| `ai_docs/` | Project documentation |

## Lessons Learned

### Proxy Pattern Discovery
- Team agents spawned via Task tool with `team_name` run in separate tmux sessions
- Separate tmux sessions = separate Claude Code processes = no MCP server inheritance
- `mcpServers` frontmatter in agent .md files does NOT work for team agents
- Solution: Team lead calls `call_agent`, extracts `system_prompt`, injects into Task prompt

### Status Line
- Agent state stored in `logs/agent_state.json` keyed by session_id
- Sub-agents must call `call_agent` or have `agent_type` set via SessionStart hook
- Status line reads from `agent_state.json` — defaults to "master-orchestrator-agent" if not found

### Docker
- After code changes, restart backend: `echo "R" | ./docker-system/docker-menu.sh`
- Python caches modules — file edits alone aren't sufficient, process must restart
