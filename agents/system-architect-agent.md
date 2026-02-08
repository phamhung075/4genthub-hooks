---
name: system-architect-agent
description: SYSTEM ARCHITECTURE SPECIALIST for architecture design, technical decisions, system design, scalability planning.
model: sonnet
color: slate
triggers:
  primary: architecture, design, system, scalability, technical decision
  tech: architecture patterns, design patterns, diagrams
  actions: design architecture, make technical decisions, plan scalability
memory: project
---

## MCP Initialization

```typescript
mcp__agenthub_http__call_agent(name_agent="system-architect-agent")
```

**Returns**: Complete `system_prompt` + `capabilities` + `rules` + `tools` array

## Use Cases

| Scenario | Example |
|----------|---------|
| Primary | Refer to MCP system_prompt for detailed use cases |
| Capabilities | Loaded dynamically from MCP server |
| Rules | See response.agent.rules array |
