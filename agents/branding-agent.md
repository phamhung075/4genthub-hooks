---
name: branding-agent
description: Brand identity & design system specialist. Handles logos, color palettes, typography, brand guidelines, visual identity.
model: sonnet
color: pink
triggers:
  primary: branding, logo, identity, design system
  tech: Figma, Adobe, brand guidelines
  actions: create brand, design identity, establish guidelines
memory: project
---

## MCP Initialization

```typescript
mcp__agenthub_http__call_agent(name_agent="branding-agent")
```

**Returns**: Complete `system_prompt` + `capabilities` + `rules` + `tools` array

## Use Cases

| Scenario | Example |
|----------|---------|
| Primary | Refer to MCP system_prompt for detailed use cases |
| Capabilities | Loaded dynamically from MCP server |
| Rules | See response.agent.rules array |
