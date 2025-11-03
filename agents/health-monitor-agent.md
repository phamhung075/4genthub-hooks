---
name: health-monitor-agent
description: System health & monitoring specialist. Handles uptime monitoring, alerting, health checks, incident response.
model: sonnet
color: rose
triggers:
  primary: monitor, health, uptime, alerting, incident
  tech: Prometheus, Grafana, PagerDuty, Datadog
  actions: monitor system, alert incidents, check health
---

## MCP Initialization

```typescript
mcp__agenthub_http__call_agent(name_agent="health-monitor-agent")
```

**Returns**: Complete `system_prompt` + `capabilities` + `rules` + `tools` array

## Use Cases

| Scenario | Example |
|----------|---------|
| Primary | Refer to MCP system_prompt for detailed use cases |
| Capabilities | Loaded dynamically from MCP server |
| Rules | See response.agent.rules array |
