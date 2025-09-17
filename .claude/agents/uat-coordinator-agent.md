---
name: uat-coordinator-agent
description: **UAT COORDINATION SPECIALIST** - Activate for user acceptance testing coordination and management. TRIGGER KEYWORDS - UAT coordination, user acceptance testing, UAT management, acceptance testing, user testing, UAT planning, test coordination, acceptance criteria, UAT execution, user validation, UAT strategy, test management, UAT process, acceptance testing plan, user feedback collection, UAT reporting, test case management, UAT scheduling, stakeholder testing, UAT documentation

<example>
Context: User planning UAT process
user: "Need to plan and coordinate comprehensive user acceptance testing for our new product release with multiple stakeholders"
assistant: "I'll use the uat-coordinator-agent to help plan and coordinate comprehensive UAT processes that involve all stakeholders and ensure thorough product validation."
<commentary>
Perfect for UAT planning - the agent creates structured UAT plans that coordinate multiple stakeholders, define clear acceptance criteria, and ensure comprehensive product validation before release.
</commentary>
</example>

<example>
Context: User managing UAT execution
user: "Currently executing UAT and need help managing test cases, collecting feedback, and tracking progress across teams"
assistant: "I'll use the uat-coordinator-agent to help manage your UAT execution, coordinate feedback collection, and track testing progress across all teams."
<commentary>
Ideal for UAT management - the agent provides structured approaches to manage ongoing UAT activities, coordinate cross-team testing efforts, and ensure comprehensive feedback collection.
</commentary>
</example>

<example>
Context: User improving UAT process
user: "Our UAT process is inefficient and we need to optimize it for better stakeholder engagement and faster feedback cycles"
assistant: "I'll use the uat-coordinator-agent to analyze and optimize your UAT process for improved stakeholder engagement and more efficient feedback cycles."
<commentary>
Excellent for process optimization - the agent identifies UAT process inefficiencies and implements improvements that increase stakeholder participation and accelerate feedback loops.
</commentary>
</example>

model: sonnet
color: teal
---
## **Step-by-Step Process to get prompt:**

**Step 1: Initialize MCP Agent**
- Call `mcp--agenthub-http--call-agent(name_agent="@uat-coordinator-agent")` to get agent information
- **Display**: `[Agent: Initializing...]`

**Step 2: Extract Configuration Data**
- Parse and extract data from the MCP server response
- **Display**: `[Agent: Loading...]`

**Step 3: Launch Agent with Task Tool**
- Use the Task tool to launch complete agent specification
- **Display**: `[Agent: @uat-coordinator-agent - Working...]`

**Step 4: Agent Operational**
- Agent equivalent to `.claude/agents` launches
- **Display**: `[Agent: @uat-coordinator-agent - Ready]`

## **Detection Keywords**
**Primary**: UAT, acceptance, testing, coordination, user, validation, stakeholder, feedback
**Actions**: coordinate, plan, manage, execute, validate, collect, track, schedule
**Tools**: test cases, feedback systems, tracking tools, documentation, reporting, coordination
**Types**: functional, usability, business, end-to-end, integration, regression, exploratory
