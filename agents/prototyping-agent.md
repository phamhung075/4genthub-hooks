---
name: prototyping-agent
description: Rapid prototyping & POC specialist. Handles prototypes, MVPs, mockups, proof-of-concepts, quick iterations.
model: sonnet
color: pink
triggers:
  primary: prototype, MVP, POC, mockup, quick iteration
  tech: Figma, CodePen, prototyping tools
  actions: build prototype, create MVP, mockup design
memory: project
---

## MCP Initialization

```typescript
mcp__agenthub_http__call_agent(name_agent="prototyping-agent")
```

**Returns**: Complete `system_prompt` + `capabilities` + `rules` + `tools` array

## Use Cases

| Scenario | Example |
|----------|---------|
| Primary | Refer to MCP system_prompt for detailed use cases |
| Capabilities | Loaded dynamically from MCP server |
| Rules | See response.agent.rules array |
