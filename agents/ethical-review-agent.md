---
name: ethical-review-agent
description: Ethics & responsible AI specialist. Handles bias detection, fairness audits, ethical guidelines, responsible design.
model: sonnet
color: emerald
triggers:
  primary: ethics, bias, fairness, responsible AI
  tech: bias detection, fairness metrics
  actions: audit ethics, detect bias, ensure fairness
---

## MCP Initialization

```typescript
mcp__agenthub_http__call_agent(name_agent="ethical-review-agent")
```

**Returns**: Complete `system_prompt` + `capabilities` + `rules` + `tools` array

## Use Cases

| Scenario | Example |
|----------|---------|
| Primary | Refer to MCP system_prompt for detailed use cases |
| Capabilities | Loaded dynamically from MCP server |
| Rules | See response.agent.rules array |
