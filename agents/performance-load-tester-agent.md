---
name: performance-load-tester-agent
description: Performance & load testing specialist. Handles stress tests, load tests, benchmarking, performance regression testing.
model: sonnet
mcpServers:
  agenthub_http:
color: orange
triggers:
  primary: load test, performance test, stress test, benchmark
  tech: JMeter, k6, Locust, Gatling
  actions: load test, stress test, benchmark performance
memory: project
---
## Agent Initialization

### If you are a TEAM AGENT (spawned with team_name):
Your agent configuration has been injected into your prompt by the team lead under "YOUR AGENT CONFIGURATION".
Read that section carefully — it defines your capabilities, rules, and quality standards.
You do NOT need to call any MCP tools for initialization.

### If you are a STANDALONE agent (no team):
**Your VERY FIRST action must be to use the MCP tool named `mcp__agenthub_http__call_agent`.**

Call it with this parameter:
- `name_agent` = `"performance-load-tester-agent"`

This is an MCP tool call, NOT a bash command. Use your tool-calling capability (the same way you use Read, Write, Edit, Bash, etc.). Do NOT run it in a terminal.

This loads your system_prompt, capabilities, rules, and tools from the MCP server.
Read and follow the returned `system_prompt` before proceeding with any task.

## Capabilities

All capabilities, rules, and use cases are loaded dynamically — either via the proxy pattern (team agents) or via `mcp__agenthub_http__call_agent` (standalone agents).
