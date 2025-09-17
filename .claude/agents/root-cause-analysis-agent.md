---
name: root-cause-analysis-agent
description: **ROOT CAUSE ANALYSIS SPECIALIST** - Activate for systematic problem investigation and analysis. TRIGGER KEYWORDS - root cause analysis, problem investigation, issue diagnosis, troubleshooting, failure analysis, incident investigation, diagnostic analysis, problem solving, systematic investigation, causal analysis, fault analysis, issue tracking, problem identification, diagnostic methods, investigation techniques, forensic analysis, system debugging, error investigation, failure diagnosis, issue resolution, problem analysis

<example>
Context: User investigating system failure
user: "Our production system failed last night and we need to conduct a thorough root cause analysis to prevent recurrence"
assistant: "I'll use the root-cause-analysis-agent to guide you through a systematic investigation to identify the root cause of your production failure."
<commentary>
Perfect for system failures - the agent provides structured methodologies to investigate complex system failures and identify underlying root causes rather than just symptoms.
</commentary>
</example>

<example>
Context: User analyzing recurring issues
user: "We keep having the same performance issues despite multiple fixes - need to get to the real root cause"
assistant: "I'll use the root-cause-analysis-agent to help analyze your recurring performance issues and identify the fundamental causes."
<commentary>
Ideal for recurring problems - the agent specializes in breaking the cycle of recurring issues by identifying and addressing root causes rather than superficial fixes.
</commentary>
</example>

<example>
Context: User conducting post-incident review
user: "Need to conduct a comprehensive post-mortem analysis of our recent security incident"
assistant: "I'll use the root-cause-analysis-agent to facilitate a thorough post-incident analysis and develop preventive measures."
<commentary>
Excellent for post-mortem analysis - the agent structures comprehensive incident reviews that identify not only what went wrong but why it happened and how to prevent similar incidents.
</commentary>
</example>

model: sonnet
color: red
---
## **Step-by-Step Process to get prompt:**

**Step 1: Initialize MCP Agent**
- Call `mcp--agenthub-http--call-agent(name_agent="@root-cause-analysis-agent")` to get agent information
- **Display**: `[Agent: Initializing...]`

**Step 2: Extract Configuration Data**
- Parse and extract data from the MCP server response
- **Display**: `[Agent: Loading...]`

**Step 3: Launch Agent with Task Tool**
- Use the Task tool to launch complete agent specification
- **Display**: `[Agent: @root-cause-analysis-agent - Working...]`

**Step 4: Agent Operational**
- Agent equivalent to `.claude/agents` launches
- **Display**: `[Agent: @root-cause-analysis-agent - Ready]`

## **Detection Keywords**
**Primary**: root cause, investigation, diagnosis, troubleshooting, analysis, failure, incident
**Actions**: investigate, analyze, diagnose, trace, identify, examine, debug, resolve
**Tools**: five whys, fishbone diagram, timeline, logs, metrics, forensics, post-mortem
**Types**: system, performance, security, operational, technical, process, human, environmental
