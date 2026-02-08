---
name: spawn-team
description: Spawn an agent team using the Proxy Pattern. Team lead fetches agent configs from MCP and injects them into teammate prompts (since team agents cannot access MCP tools).
---

# Spawn Team Skill (Proxy Pattern)

Creates an agent team where the team lead fetches agent configurations from MCP and injects them into teammate prompts. This is required because team agents run in separate tmux sessions and cannot access MCP tools directly.

## When to Use

- User requests parallel work across multiple files
- Tasks can be broken into independent units
- Multiple agents needed for efficiency

## Proxy Pattern Explained

**Problem:** Team agents spawned via `Task` tool with `team_name` run in separate Claude Code processes. They do NOT inherit MCP server connections and cannot call `mcp__agenthub_http__call_agent`.

**Solution:** The team lead (which HAS MCP access) fetches each agent's config BEFORE spawning, then injects the `system_prompt` into the teammate's prompt.

## Workflow Steps

### 1. Analyze
- Read all relevant files
- Break request into independent tasks

### 2. Create Team & Tasks
```
TeamCreate(team_name="descriptive-name", description="purpose")
TaskCreate(subject="Task description", description="Details", activeForm="Doing X")
```

### 3. Fetch Agent Configs (Proxy Pattern)

For each unique agent type needed, the team lead calls:

mcp__agenthub_http__call_agent with name_agent="{agent-type}"

Extract `response.agent.system_prompt` — this is the agent's operating manual.
Cache results: if multiple agents share the same type, fetch only once.

### 4. Spawn Teammates (Parallel)

Choose the right agent type per task. Inject the fetched `system_prompt` into each prompt.

**Teammate prompt template:**

```
You are a {agent_type} teammate on team "{team_name}". Your name is "{teammate_name}".

YOUR AGENT CONFIGURATION (loaded from MCP server by team lead):
{system_prompt from call_agent response}

YOUR TASK (Task #{task_number}):
{task_description}

WORKFLOW:
1. Read the target file(s) to confirm current state
2. Make the required changes following the agent configuration above
3. Verify your changes by reading the file again
4. Use AskUserQuestion to ask the user to confirm your work
5. After user confirmation, mark Task #{task_number} as completed via TaskUpdate
6. Send a message to the team lead reporting completion

IMPORTANT: Do NOT skip step 4 (user confirmation) — it is mandatory.
```

**Agent type selection guide:**

| Task Type | Agent | subagent_type |
|-----------|-------|---------------|
| Write/edit code | coding-agent | `coding-agent` |
| Fix bugs | debugger-agent | `debugger-agent` |
| Write/run tests | test-orchestrator-agent | `test-orchestrator-agent` |
| Security audit | security-auditor-agent | `security-auditor-agent` |
| Code review | code-reviewer-agent | `code-reviewer-agent` |
| UI/frontend | ui-specialist-agent | `ui-specialist-agent` |
| Architecture | system-architect-agent | `system-architect-agent` |
| DevOps/infra | devops-agent | `devops-agent` |
| Documentation | documentation-agent | `documentation-agent` |
| Research | deep-research-agent | `deep-research-agent` |

Full list: see `.claude/agents/` (30+ agent types available)

### 5. Monitor
- Wait for teammate messages
- Verify results by reading files

### 6. Clean Up
```
SendMessage(type="shutdown_request", recipient="teammate-name")
TeamDelete()
```

## Key Rules

- Team lead MUST fetch agent config via `call_agent` BEFORE spawning each teammate
- The fetched `system_prompt` MUST be injected into the teammate's Task prompt
- Each teammate MUST ask user confirmation before reporting done
- Spawn teammates in parallel when tasks are independent
- Team lead verifies results before shutting down
- The `subagent_type` in Task tool should match the agent type used in `call_agent`
