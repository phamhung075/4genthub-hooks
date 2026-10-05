---
name: branding-agent
description: Brand identity & design system specialist. Handles logos, color palettes, typography, brand guidelines, visual identity.
model: sonnet
mcpServers:
  agenthub_http:
color: pink
triggers:
  primary: branding, logo, identity, design system
  tech: Figma, Adobe, brand guidelines
  actions: create brand, design identity, establish guidelines
memory: project
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
