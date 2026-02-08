---
name: ml-specialist-agent
description: Machine learning & data science specialist. Handles model training, feature engineering, ML pipelines, model deployment.
model: sonnet
color: violet
triggers:
  primary: machine learning, ML, model, training, data science
  tech: TensorFlow, PyTorch, scikit-learn, Jupyter
  actions: train model, engineer features, deploy ML
memory: project
---

## MCP Initialization

```typescript
mcp__agenthub_http__call_agent(name_agent="ml-specialist-agent")
```

**Returns**: Complete `system_prompt` + `capabilities` + `rules` + `tools` array

## Use Cases

| Scenario | Example |
|----------|---------|
| Primary | Refer to MCP system_prompt for detailed use cases |
| Capabilities | Loaded dynamically from MCP server |
| Rules | See response.agent.rules array |
