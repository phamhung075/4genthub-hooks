---
name: elicitation-agent
description: Requirements gathering & stakeholder interview specialist. Handles user research, interviews, requirement elicitation.
model: sonnet
color: lime
triggers:
  primary: elicit, gather requirements, interview, research
  tech: user research, interview techniques
  actions: gather requirements, interview stakeholders, research needs
---

## MCP Initialization

```typescript
mcp__agenthub_http__call_agent(name_agent="elicitation-agent")
```

**Returns**: Complete `system_prompt` + `capabilities` + `rules` + `tools` array

## Use Cases

| Scenario | Example |
|----------|---------|
| Primary | Refer to MCP system_prompt for detailed use cases |
| Capabilities | Loaded dynamically from MCP server |
| Rules | See response.agent.rules array |
