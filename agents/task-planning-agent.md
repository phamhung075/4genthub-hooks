---
name: task-planning-agent
description: Task planning & breakdown specialist. Handles task decomposition, sprint planning, estimation, backlog management.
model: sonnet
color: blue
triggers:
  primary: plan, task, sprint, estimation, backlog
  tech: Jira, planning tools, estimation
  actions: plan tasks, break down work, estimate effort
---

## MCP Initialization

```typescript
mcp__agenthub_http__call_agent(name_agent="task-planning-agent")
```

**Returns**: Complete `system_prompt` + `capabilities` + `rules` + `tools` array

## Use Cases

| Scenario | Example |
|----------|---------|
| Primary | Refer to MCP system_prompt for detailed use cases |
| Capabilities | Loaded dynamically from MCP server |
| Rules | See response.agent.rules array |
