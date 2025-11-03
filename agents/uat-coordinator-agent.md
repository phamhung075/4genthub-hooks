---
name: uat-coordinator-agent
description: User acceptance testing coordinator. Handles UAT planning, test scripts, stakeholder coordination, acceptance criteria.
model: sonnet
color: green
triggers:
  primary: UAT, acceptance testing, user testing, validation
  tech: UAT tools, test management
  actions: coordinate UAT, create test scripts, validate acceptance
---

## MCP Initialization

```typescript
mcp__agenthub_http__call_agent(name_agent="uat-coordinator-agent")
```

**Returns**: Complete `system_prompt` + `capabilities` + `rules` + `tools` array

## Use Cases

| Scenario | Example |
|----------|---------|
| Primary | Refer to MCP system_prompt for detailed use cases |
| Capabilities | Loaded dynamically from MCP server |
| Rules | See response.agent.rules array |
