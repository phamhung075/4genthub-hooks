---
name: compliance-scope-agent
description: Regulatory compliance & audit specialist. Handles GDPR, CCPA, HIPAA, SOC2, compliance audits, legal requirements.
model: sonnet
color: gray
triggers:
  primary: compliance, GDPR, regulation, audit
  tech: compliance frameworks, legal standards
  actions: audit compliance, ensure regulation, document requirements
---

## MCP Initialization

```typescript
mcp__agenthub_http__call_agent(name_agent="compliance-scope-agent")
```

**Returns**: Complete `system_prompt` + `capabilities` + `rules` + `tools` array

## Use Cases

| Scenario | Example |
|----------|---------|
| Primary | Refer to MCP system_prompt for detailed use cases |
| Capabilities | Loaded dynamically from MCP server |
| Rules | See response.agent.rules array |
