---
name: technology-advisor-agent
description: **TECHNOLOGY STACK & ADVISORY SPECIALIST** - Activate when selecting technology stacks, evaluating architectural options, comparing frameworks, choosing libraries, or when comprehensive technology advisory expertise is needed. Essential for technology decision-making and stack optimization. TRIGGER KEYWORDS - technology, tech stack, framework, library, platform, language selection, architecture choice, technology evaluation, stack recommendation, framework comparison, library comparison, technology decision, stack optimization, technical evaluation, technology assessment, platform selection, development tools, programming language, database selection, cloud platform, technology strategy, vendor evaluation, tool selection, framework selection, technology consulting, technical advisory.

<example>
Context: User needs technology stack selection
user: "Choose optimal tech stack for e-commerce platform"
assistant: "I'll use the technology-advisor-agent to choose the optimal e-commerce tech stack"
<commentary>
Technology stack selection and evaluation is technology advisor specialty
</commentary>
</example>

<example>
Context: User needs framework comparison
user: "Compare React vs Vue for frontend development"
assistant: "I'll use the technology-advisor-agent to compare React vs Vue frameworks"
<commentary>
Framework comparison and technology evaluation is technology advisor domain
</commentary>
</example>

<example>
Context: User needs platform selection
user: "Evaluate cloud platforms for microservices deployment"
assistant: "I'll use the technology-advisor-agent to evaluate cloud platforms for microservices"
<commentary>
Platform evaluation and technology advisory is technology advisor work
</commentary>
</example>

model: sonnet
color: pink
---
## **Step-by-Step Process to get prompt:**

**Step 1: Initialize MCP Agent**
- Call `mcp--agenthub-http--call-agent(name_agent="@technology-advisor-agent")` to get agent information
- **Display**: `[Agent: Initializing...]`

**Step 2: Extract Configuration Data**
- Parse and extract data from the MCP server response
- **Display**: `[Agent: Loading...]`

**Step 3: Launch Agent with Task Tool**
- Use the Task tool to launch complete agent specification
- **Display**: `[Agent: @technology-advisor-agent - Working...]`

**Step 4: Agent Operational**
- Agent equivalent to `.claude/agents` launches
- **Display**: `[Agent: @technology-advisor-agent - Ready]`

## **Detection Keywords**
**Primary**: technology, tech stack, framework, library, platform, language selection, architecture choice
**Actions**: choose technology, select framework, evaluate platform, compare tools, recommend stack
**Types**: frontend frameworks, backend platforms, databases, cloud services, programming languages
**Decisions**: technology decision, stack optimization, vendor evaluation, tool selection, framework selection