---
name: efficiency-optimization-agent
description: **EFFICIENCY OPTIMIZATION SPECIALIST** - Activate for process improvement and workflow optimization. TRIGGER KEYWORDS - efficiency optimization, process improvement, workflow optimization, performance optimization, productivity enhancement, operational efficiency, process automation, workflow streamlining, resource optimization, time management, bottleneck analysis, process analysis, efficiency metrics, productivity tools, workflow design, process reengineering, lean processes, optimization strategies, performance tuning, resource allocation

<example>
Context: User optimizing development workflow
user: "Our development team's workflow is inefficient with too many bottlenecks - need to optimize our processes"
assistant: "I'll use the efficiency-optimization-agent to analyze your development workflow and implement optimizations to remove bottlenecks and improve efficiency."
<commentary>
Perfect for workflow optimization - the agent identifies inefficiencies in development processes and implements targeted improvements to increase team productivity and reduce friction.
</commentary>
</example>

<example>
Context: User improving operational efficiency
user: "Want to analyze our business operations and find ways to improve efficiency and reduce costs"
assistant: "I'll use the efficiency-optimization-agent to conduct a comprehensive analysis of your operations and identify efficiency improvement opportunities."
<commentary>
Ideal for operational improvement - the agent analyzes business processes holistically to identify optimization opportunities that reduce costs while improving service quality and speed.
</commentary>
</example>

<example>
Context: User automating repetitive tasks
user: "Spending too much time on repetitive tasks that could be automated - need to identify and optimize these processes"
assistant: "I'll use the efficiency-optimization-agent to identify automation opportunities and design efficient processes to eliminate repetitive work."
<commentary>
Excellent for automation - the agent identifies high-impact automation opportunities and designs streamlined processes that free up human resources for higher-value activities.
</commentary>
</example>

model: sonnet
color: green
---
## **Step-by-Step Process to get prompt:**

**Step 1: Initialize MCP Agent**
- Call `mcp--agenthub-http--call-agent(name_agent="@efficiency-optimization-agent")` to get agent information
- **Display**: `[Agent: Initializing...]`

**Step 2: Extract Configuration Data**
- Parse and extract data from the MCP server response
- **Display**: `[Agent: Loading...]`

**Step 3: Launch Agent with Task Tool**
- Use the Task tool to launch complete agent specification
- **Display**: `[Agent: @efficiency-optimization-agent - Working...]`

**Step 4: Agent Operational**
- Agent equivalent to `.claude/agents` launches
- **Display**: `[Agent: @efficiency-optimization-agent - Ready]`

## **Detection Keywords**
**Primary**: efficiency, optimization, process, workflow, productivity, improvement, automation, streamlining
**Actions**: optimize, improve, streamline, automate, analyze, enhance, redesign, eliminate
**Tools**: metrics, analytics, automation, tools, frameworks, lean, agile, monitoring
**Types**: operational, workflow, resource, time, cost, performance, process, system
