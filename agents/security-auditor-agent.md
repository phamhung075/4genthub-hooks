---
name: security-auditor-agent
description: SECURITY & AUDIT SPECIALIST for security audits, vulnerability assessments, compliance, penetration testing.
model: sonnet
color: indigo
triggers:
  primary: security, audit, vulnerability, compliance, pentest
  tech: OWASP, security scanners, compliance frameworks
  actions: audit security, scan vulnerabilities, assess compliance
memory: project
---

## MCP Initialization

```typescript
mcp__agenthub_http__call_agent(name_agent="security-auditor-agent")
```

**Returns**: Complete `system_prompt` + `capabilities` + `rules` + `tools` array

## Use Cases

| Scenario | Example |
|----------|---------|
| Primary | Refer to MCP system_prompt for detailed use cases |
| Capabilities | Loaded dynamically from MCP server |
| Rules | See response.agent.rules array |
