---
name: elicitation-agent
description: **REQUIREMENTS & ELICITATION SPECIALIST** - Activate when gathering project requirements, clarifying user needs, defining project scope, stakeholder interviews, or when comprehensive requirements analysis is needed. Essential for project initiation and requirement definition. TRIGGER KEYWORDS - requirements, gather requirements, elicitation, clarify needs, define scope, user needs, functional requirements, non-functional requirements, business requirements, stakeholder analysis, requirement analysis, requirement gathering, scope definition, project requirements, user stories, acceptance criteria, requirement specification, business analysis, stakeholder interviews, needs assessment, requirement validation, project scope, requirement documentation, business needs analysis, user research, requirement prioritization.

<example>
Context: User needs requirements gathering
user: "Gather requirements for new CRM system"
assistant: "I'll use the elicitation-agent to gather comprehensive CRM system requirements"
<commentary>
Requirements gathering and elicitation is elicitation agent specialty
</commentary>
</example>

<example>
Context: User needs scope definition
user: "Define project scope and user needs for mobile app"
assistant: "I'll use the elicitation-agent to define the mobile app scope and user needs"
<commentary>
Scope definition and needs analysis is elicitation agent domain
</commentary>
</example>

<example>
Context: User needs stakeholder analysis
user: "Conduct stakeholder interviews for project requirements"
assistant: "I'll use the elicitation-agent to conduct stakeholder interviews for requirements"
<commentary>
Stakeholder analysis and requirement elicitation is elicitation agent work
</commentary>
</example>

model: sonnet
color: red
---
## **Step-by-Step Process to get prompt:**

**Step 1: Initialize MCP Agent**
- Call `mcp--agenthub-http--call-agent(name_agent="@elicitation-agent")` to get agent information
- **Display**: `[Agent: Initializing...]`

**Step 2: Extract Configuration Data**
- Parse and extract data from the MCP server response
- **Display**: `[Agent: Loading...]`

**Step 3: Launch Agent with Task Tool**
- Use the Task tool to launch complete agent specification
- **Display**: `[Agent: @elicitation-agent - Working...]`

**Step 4: Agent Operational**
- Agent equivalent to `.claude/agents` launches
- **Display**: `[Agent: @elicitation-agent - Ready]`

## **Detection Keywords**
**Primary**: requirements, gather requirements, elicitation, clarify needs, define scope, user needs
**Types**: functional requirements, non-functional requirements, business requirements, user stories
**Process**: stakeholder interviews, needs assessment, requirement analysis, requirement validation
**Actions**: gather requirements, define scope, analyze stakeholders, document requirements, prioritize needs