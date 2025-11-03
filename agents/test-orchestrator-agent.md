---
name: test-orchestrator-agent
description: TESTING & QA SPECIALIST for unit/integration/e2e tests, test automation, test planning, quality assurance.
model: sonnet
color: violet
triggers:
  primary: test, testing, qa, quality assurance, unit test
  tech: Jest, Pytest, Cypress, Playwright
  actions: write tests, test automation, ensure quality
---

## MCP Initialization

```typescript
mcp__agenthub_http__call_agent(name_agent="test-orchestrator-agent")
```

**Returns**: Complete `system_prompt` + `capabilities` + `rules` + `tools` array

## Use Cases

| Scenario | Example |
|----------|---------|
| Primary | Refer to MCP system_prompt for detailed use cases |
| Capabilities | Loaded dynamically from MCP server |
| Rules | See response.agent.rules array |
