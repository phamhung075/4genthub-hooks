---
name: debugger-agent
description: DEBUGGING & TROUBLESHOOTING SPECIALIST for bug fixes, error resolution, crash investigation, performance issues.
model: sonnet
color: red
triggers:
  primary: debug, fix, error, bug, crash, troubleshoot
  tech: debugger, profiler, logging, stack trace
  actions: fix bug, resolve error, troubleshoot issue
---

## MCP Initialization

```typescript
mcp__agenthub_http__call_agent(name_agent="debugger-agent")
```

**Returns**: Complete `system_prompt` + `capabilities` + `rules` + `tools` array

## Use Cases

| Scenario | Example |
|----------|---------|
| Primary | Refer to MCP system_prompt for detailed use cases |
| Capabilities | Loaded dynamically from MCP server |
| Rules | See response.agent.rules array |
