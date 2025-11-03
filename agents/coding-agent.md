---
name: coding-agent
description: PRIMARY DEVELOPMENT AGENT for implementation, programming, software development. Handles features, APIs, databases, algorithms.
model: sonnet
color: stone
triggers:
  primary: implement, code, write, program, develop, build
  tech: TypeScript, Python, React, FastAPI, SQL
  actions: feature, API, component, integration
---

## MCP Initialization

```typescript
mcp__agenthub_http__call_agent(name_agent="coding-agent")
```

**Returns**: Complete `system_prompt` + `capabilities` + `rules` + `tools` array

## Use Cases

| Scenario | Example |
|----------|---------|
| Primary | Refer to MCP system_prompt for detailed use cases |
| Capabilities | Loaded dynamically from MCP server |
| Rules | See response.agent.rules array |
