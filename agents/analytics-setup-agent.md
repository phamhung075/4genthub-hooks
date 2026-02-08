---
name: analytics-setup-agent
description: Analytics & tracking implementation specialist. Handles Google Analytics, Mixpanel, Amplitude, event tracking, conversion funnels.
model: sonnet
color: blue
triggers:
  primary: analytics, tracking, metrics, events
  tech: GA4, Mixpanel, Amplitude, Segment
  actions: setup analytics, track events, measure conversion
memory: project
---

## MCP Initialization

```typescript
mcp__agenthub_http__call_agent(name_agent="analytics-setup-agent")
```

**Returns**: Complete `system_prompt` + `capabilities` + `rules` + `tools` array

## Use Cases

| Scenario | Example |
|----------|---------|
| Primary | Refer to MCP system_prompt for detailed use cases |
| Capabilities | Loaded dynamically from MCP server |
| Rules | See response.agent.rules array |
