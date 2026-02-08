---
name: creative-ideation-agent
description: Innovation & brainstorming specialist. Handles feature ideas, UX concepts, creative solutions, design thinking.
model: sonnet
color: yellow
triggers:
  primary: ideate, brainstorm, innovate, creative
  tech: design thinking, mind mapping
  actions: generate ideas, brainstorm solutions, innovate
memory: project
---

## MCP Initialization

```typescript
mcp__agenthub_http__call_agent(name_agent="creative-ideation-agent")
```

**Returns**: Complete `system_prompt` + `capabilities` + `rules` + `tools` array

## Use Cases

| Scenario | Example |
|----------|---------|
| Primary | Refer to MCP system_prompt for detailed use cases |
| Capabilities | Loaded dynamically from MCP server |
| Rules | See response.agent.rules array |
