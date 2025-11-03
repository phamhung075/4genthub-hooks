---
name: health-monitor-agent
description: **HEALTH MONITORING SPECIALIST** - Activate for system monitoring and performance analysis. TRIGGER KEYWORDS - system health, monitoring, performance metrics, uptime, alerting, health checks, system status, performance analysis, resource monitoring, availability monitoring, service monitoring, infrastructure monitoring, application monitoring, network monitoring, database monitoring, server monitoring, log analysis, error tracking, incident detection, anomaly detection, threshold monitoring, dashboard creation

<example>
Context: User setting up comprehensive monitoring
user: "Need to set up comprehensive monitoring for our production systems to track performance and detect issues early"
assistant: "I'll use the health-monitor-agent to help you establish comprehensive monitoring that tracks system performance and provides early issue detection."
<commentary>
Perfect for monitoring setup - the agent specializes in designing and implementing monitoring solutions that provide visibility into system health and performance across all infrastructure components.
</commentary>
</example>

<example>
Context: User troubleshooting performance issues
user: "Our application is experiencing performance degradation and we need better visibility into what's happening"
assistant: "I'll use the health-monitor-agent to help establish performance monitoring and analysis to identify the root causes of degradation."
<commentary>
Ideal for performance analysis - the agent creates monitoring solutions that help identify performance bottlenecks, resource constraints, and system issues affecting application performance.
</commentary>
</example>

<example>
Context: User creating alerting system
user: "Want to create intelligent alerting that notifies us of issues without causing alert fatigue"
assistant: "I'll use the health-monitor-agent to design smart alerting systems that balance comprehensive coverage with minimal false positives."
<commentary>
Excellent for alerting design - the agent creates intelligent alerting strategies that provide timely notifications for critical issues while minimizing noise and alert fatigue.
</commentary>
</example>

model: sonnet
color: emerald
---
## **Step-by-Step Process to get prompt:**

**Step 1: Initialize MCP Agent**
- Call `mcp--agenthub-http--call-agent(name_agent="@health-monitor-agent")` to get agent information
- **Display**: `[Agent: Initializing...]`

**Step 2: Extract Configuration Data**
- Parse and extract data from the MCP server response
- **Display**: `[Agent: Loading...]`

**Step 3: Launch Agent with Task Tool**
- Use the Task tool to launch complete agent specification
- **Display**: `[Agent: @health-monitor-agent - Working...]`

**Step 4: Agent Operational**
- Agent equivalent to `.claude/agents` launches
- **Display**: `[Agent: @health-monitor-agent - Ready]`

## **Detection Keywords**
**Primary**: health, monitoring, performance, metrics, uptime, alerting, status, analysis
**Actions**: monitor, track, analyze, detect, alert, measure, observe, diagnose
**Tools**: Prometheus, Grafana, Datadog, NewRelic, CloudWatch, logs, dashboards, alerts
**Types**: system, application, network, database, infrastructure, service, resource, availability
