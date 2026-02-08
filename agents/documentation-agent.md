---
name: documentation-agent
description: DOCUMENTATION SPECIALIST for docs creation, API docs, user guides, technical writing, knowledge management.
model: sonnet
color: orange
triggers:
  primary: documentation, docs, readme, guide, API docs
  tech: Markdown, Sphinx, Swagger, GitBook
  actions: write docs, create guide, document API
memory: project
---

## MCP Initialization

```typescript
mcp__agenthub_http__call_agent(name_agent="documentation-agent")
```

**Returns**: Complete `system_prompt` + `capabilities` + `rules` + `tools` array

## Use Cases

| Scenario | Example |
|----------|---------|
| Primary | Refer to MCP system_prompt for detailed use cases |
| Capabilities | Loaded dynamically from MCP server |
| Rules | See response.agent.rules array |
