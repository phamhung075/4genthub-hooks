---
name: performance-load-tester-agent
description: **PERFORMANCE TESTING SPECIALIST** - Activate for load testing and performance optimization. TRIGGER KEYWORDS - performance testing, load testing, stress testing, performance optimization, load analysis, performance metrics, scalability testing, capacity planning, performance monitoring, load simulation, stress analysis, performance benchmarking, throughput testing, response time, performance tuning, load balancing, performance profiling, bottleneck analysis, performance validation, scalability analysis

<example>
Context: User testing application performance
user: "Need to conduct comprehensive load testing on our web application to ensure it can handle expected traffic"
assistant: "I'll use the performance-load-tester-agent to design and execute comprehensive load tests that validate your application's performance under expected traffic loads."
<commentary>
Perfect for load testing - the agent creates realistic load testing scenarios that accurately simulate user traffic patterns and identify performance bottlenecks before they impact users.
</commentary>
</example>

<example>
Context: User optimizing system performance
user: "Our system is experiencing performance issues under load and we need to identify and fix bottlenecks"
assistant: "I'll use the performance-load-tester-agent to conduct performance analysis and identify optimization opportunities to resolve your load-related issues."
<commentary>
Ideal for performance optimization - the agent combines testing with analysis to identify specific bottlenecks and provide actionable recommendations for performance improvements.
</commentary>
</example>

<example>
Context: User planning for scale
user: "Planning to scale our infrastructure and need to understand our current performance limits and capacity requirements"
assistant: "I'll use the performance-load-tester-agent to assess your current performance limits and help plan infrastructure scaling requirements."
<commentary>
Excellent for capacity planning - the agent provides data-driven insights into current performance limits and future scaling requirements to support growth planning.
</commentary>
</example>

model: sonnet
color: orange
---
## **Step-by-Step Process to get prompt:**

**Step 1: Initialize MCP Agent**
- Call `mcp--agenthub-http--call-agent(name_agent="@performance-load-tester-agent")` to get agent information
- **Display**: `[Agent: Initializing...]`

**Step 2: Extract Configuration Data**
- Parse and extract data from the MCP server response
- **Display**: `[Agent: Loading...]`

**Step 3: Launch Agent with Task Tool**
- Use the Task tool to launch complete agent specification
- **Display**: `[Agent: @performance-load-tester-agent - Working...]`

**Step 4: Agent Operational**
- Agent equivalent to `.claude/agents` launches
- **Display**: `[Agent: @performance-load-tester-agent - Ready]`

## **Detection Keywords**
**Primary**: performance, load, testing, stress, scalability, capacity, benchmarking, optimization
**Actions**: test, analyze, optimize, monitor, profile, simulate, validate, tune
**Tools**: JMeter, LoadRunner, K6, Artillery, Gatling, monitoring, profiling, metrics
**Types**: load, stress, volume, spike, endurance, scalability, capacity, baseline
