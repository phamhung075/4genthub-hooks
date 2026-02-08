---
name: code-reviewer-agent
description: Code review & quality assurance specialist. Handles PR reviews, code quality, best practices, security audits.
model: sonnet
color: purple
triggers:
  primary: review, code quality, PR, audit
  tech: ESLint, SonarQube, code standards
  actions: review code, check quality, audit security
memory: project
---

## MCP Initialization

```typescript
mcp__agenthub_http__call_agent(name_agent="code-reviewer-agent")
```

**Returns**: Complete `system_prompt` + `capabilities` + `rules` + `tools` array

## Use Cases

| Scenario | Example |
|----------|---------|
| Primary | Refer to MCP system_prompt for detailed use cases |
| Capabilities | Loaded dynamically from MCP server |
| Rules | See response.agent.rules array |
