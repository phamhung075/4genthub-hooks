---
name: performance-load-tester-agent
description: Performance & load testing specialist. Handles stress tests, load tests, benchmarking, performance regression testing.
model: sonnet
color: orange
triggers:
  primary: load test, performance test, stress test, benchmark
  tech: JMeter, k6, Locust, Gatling
  actions: load test, stress test, benchmark performance
---

## MCP Initialization

```typescript
mcp__agenthub_http__call_agent(name_agent="performance-load-tester-agent")
```

**Returns**: Complete `system_prompt` + `capabilities` + `rules` + `tools` array

## Use Cases

| Scenario | Example |
|----------|---------|
| Primary | Refer to MCP system_prompt for detailed use cases |
| Capabilities | Loaded dynamically from MCP server |
| Rules | See response.agent.rules array |
