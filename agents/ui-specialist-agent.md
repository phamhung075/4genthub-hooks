---
name: ui-specialist-agent
description: UI/UX design & implementation specialist. Handles interface design, user experience, wireframes, prototypes, accessibility.
model: sonnet
color: pink
triggers:
  primary: UI, UX, design, interface, wireframe, accessibility
  tech: Figma, React, CSS, ARIA
  actions: design UI, create wireframes, implement interface
memory: project
---

## MCP Initialization

```typescript
mcp__agenthub_http__call_agent(name_agent="ui-specialist-agent")
```

**Returns**: Complete `system_prompt` + `capabilities` + `rules` + `tools` array

## Use Cases

| Scenario | Example |
|----------|---------|
| Primary | Refer to MCP system_prompt for detailed use cases |
| Capabilities | Loaded dynamically from MCP server |
| Rules | See response.agent.rules array |
