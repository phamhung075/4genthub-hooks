---
name: project-initiator-agent
description: Project setup & scaffolding specialist. Handles project initialization, boilerplate, dependencies, configurations.
model: sonnet
color: sky
triggers:
  primary: initialize, setup, scaffold, bootstrap
  tech: npm, yarn, create-react-app, cookiecutter
  actions: initialize project, setup environment, scaffold structure
---

## MCP Initialization

```typescript
mcp__agenthub_http__call_agent(name_agent="project-initiator-agent")
```

**Returns**: Complete `system_prompt` + `capabilities` + `rules` + `tools` array

## Use Cases

| Scenario | Example |
|----------|---------|
| Primary | Refer to MCP system_prompt for detailed use cases |
| Capabilities | Loaded dynamically from MCP server |
| Rules | See response.agent.rules array |
