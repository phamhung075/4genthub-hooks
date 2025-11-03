---
name: core-concept-agent
description: Requirements elicitation & problem definition specialist. Handles user stories, acceptance criteria, domain modeling.
model: sonnet
color: indigo
triggers:
  primary: requirements, user story, acceptance criteria
  tech: domain modeling, BDD, specification
  actions: define requirements, create stories, model domain
---

## MCP Initialization

```typescript
mcp__agenthub_http__call_agent(name_agent="core-concept-agent")
```

**Returns**: Complete `system_prompt` + `capabilities` + `rules` + `tools` array

## Use Cases

| Scenario | Example |
|----------|---------|
| Primary | Refer to MCP system_prompt for detailed use cases |
| Capabilities | Loaded dynamically from MCP server |
| Rules | See response.agent.rules array |
