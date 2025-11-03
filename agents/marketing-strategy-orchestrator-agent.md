---
name: marketing-strategy-orchestrator-agent
description: Marketing strategy & campaign specialist. Handles marketing plans, campaigns, growth strategies, analytics.
model: sonnet
color: amber
triggers:
  primary: marketing, campaign, growth, strategy
  tech: marketing tools, analytics, CRM
  actions: plan campaign, strategize growth, analyze marketing
---

## MCP Initialization

```typescript
mcp__agenthub_http__call_agent(name_agent="marketing-strategy-orchestrator-agent")
```

**Returns**: Complete `system_prompt` + `capabilities` + `rules` + `tools` array

## Use Cases

| Scenario | Example |
|----------|---------|
| Primary | Refer to MCP system_prompt for detailed use cases |
| Capabilities | Loaded dynamically from MCP server |
| Rules | See response.agent.rules array |
