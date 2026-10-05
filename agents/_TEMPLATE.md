---
name: agent-name
description: Brief 1-line purpose. Handles X, Y, Z.
model: sonnet
color: stone
mcpServers:
  agenthub_http:
triggers:
  primary: keyword1, keyword2, keyword3
  tech: tool1, tool2, framework1
  actions: action1, action2, action3
---

## Agent Initialization

### If you are a TEAM AGENT (spawned with team_name):
Your agent configuration has been injected into your prompt by the team lead under "YOUR AGENT CONFIGURATION".
Read that section carefully — it defines your capabilities, rules, and quality standards.
You do NOT need to call any MCP tools for initialization.

### If you are a STANDALONE agent (no team):
**Your VERY FIRST action is `rig whoami --json`** (a shell command). It returns your rig, pod, member, peers and edges.

If you have MCP access, read your seat's resolved config with the MCP tool `mcp__agenthub_http__call_seat` (parameters `room` and `seat`) or `mcp__agenthub_http__manage_seat` (`action="get"`). That is an MCP tool call, NOT a bash command.
Follow the returned runtime, policy and role files before any task.

## Capabilities

All capabilities, rules, and use cases are loaded dynamically — either via the proxy pattern (team agents) or from the seat's resolved config (standalone agents).
