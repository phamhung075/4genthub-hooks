---
name: deep-research-agent
description: Technical research & analysis specialist. Handles technology evaluation, feasibility studies, competitive analysis.
model: sonnet
color: teal
triggers:
  primary: research, analysis, evaluate, investigate
  tech: research tools, data analysis
  actions: research technology, analyze options, evaluate feasibility
---

## MCP Initialization

```typescript
mcp__agenthub_http__call_agent(name_agent="deep-research-agent")
```

**Returns**: Complete `system_prompt` + `capabilities` + `rules` + `tools` array

## Use Cases

| Scenario | Example |
|----------|---------|
| Primary | Refer to MCP system_prompt for detailed use cases |
| Capabilities | Loaded dynamically from MCP server |
| Rules | See response.agent.rules array |
