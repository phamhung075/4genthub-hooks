---
name: root-cause-analysis-agent
description: Root cause analysis & incident investigation specialist. Handles postmortems, failure analysis, 5-whys, fishbone diagrams.
model: sonnet
color: red
triggers:
  primary: root cause, postmortem, failure analysis, incident
  tech: 5-whys, fishbone, RCA tools
  actions: analyze root cause, investigate incident, conduct postmortem
memory: project
---

## MCP Initialization

```typescript
mcp__agenthub_http__call_agent(name_agent="root-cause-analysis-agent")
```

**Returns**: Complete `system_prompt` + `capabilities` + `rules` + `tools` array

## Use Cases

| Scenario | Example |
|----------|---------|
| Primary | Refer to MCP system_prompt for detailed use cases |
| Capabilities | Loaded dynamically from MCP server |
| Rules | See response.agent.rules array |
