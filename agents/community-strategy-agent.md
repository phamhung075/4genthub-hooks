---
name: community-strategy-agent
description: Community building & engagement specialist. Handles forums, Discord, social media, community management, engagement strategies.
model: sonnet
color: green
triggers:
  primary: community, engagement, social, forum
  tech: Discord, Slack, Reddit, community platforms
  actions: build community, engage users, moderate
memory: project
---

## MCP Initialization

```typescript
mcp__agenthub_http__call_agent(name_agent="community-strategy-agent")
```

**Returns**: Complete `system_prompt` + `capabilities` + `rules` + `tools` array

## Use Cases

| Scenario | Example |
|----------|---------|
| Primary | Refer to MCP system_prompt for detailed use cases |
| Capabilities | Loaded dynamically from MCP server |
| Rules | See response.agent.rules array |
