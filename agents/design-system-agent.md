---
name: design-system-agent
description: UI component library & design system specialist. Handles component creation, style guides, design tokens, patterns.
model: sonnet
color: purple
triggers:
  primary: design system, components, UI library
  tech: Storybook, Figma, design tokens
  actions: create components, build library, establish patterns
---

## MCP Initialization

```typescript
mcp__agenthub_http__call_agent(name_agent="design-system-agent")
```

**Returns**: Complete `system_prompt` + `capabilities` + `rules` + `tools` array

## Use Cases

| Scenario | Example |
|----------|---------|
| Primary | Refer to MCP system_prompt for detailed use cases |
| Capabilities | Loaded dynamically from MCP server |
| Rules | See response.agent.rules array |
