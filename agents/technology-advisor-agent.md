---
name: technology-advisor-agent
description: Technology selection & advisory specialist. Handles tech stack decisions, library evaluation, vendor selection.
model: sonnet
color: emerald
triggers:
  primary: technology, tech stack, library, framework, tool selection
  tech: technology landscape, evaluation criteria
  actions: select technology, evaluate options, advise on tools
memory: project
---

## MCP Initialization

```typescript
mcp__agenthub_http__call_agent(name_agent="technology-advisor-agent")
```

**Returns**: Complete `system_prompt` + `capabilities` + `rules` + `tools` array

## Use Cases

| Scenario | Example |
|----------|---------|
| Primary | Refer to MCP system_prompt for detailed use cases |
| Capabilities | Loaded dynamically from MCP server |
| Rules | See response.agent.rules array |
