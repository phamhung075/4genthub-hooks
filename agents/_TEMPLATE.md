---
name: agent-name
description: Brief 1-line purpose. Handles X, Y, Z.
model: sonnet
color: stone
triggers:
  primary: keyword1, keyword2, keyword3
  tech: tool1, tool2, framework1
  actions: action1, action2, action3
---

## MCP Initialization

```typescript
mcp__agenthub_http__call_agent(name_agent="agent-name")
```

**Returns**: Complete `system_prompt` + `capabilities` + `rules` + `tools` array

## Use Cases

| Scenario | Example Request |
|----------|----------------|
| Primary task | "Do X with Y" |
| Secondary task | "Help with Z" |
| Edge case | "Handle special situation" |
