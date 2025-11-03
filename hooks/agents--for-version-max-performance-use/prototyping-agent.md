---
name: prototyping-agent
description: **PROTOTYPING SPECIALIST** - Activate for rapid validation and interactive demonstrations. TRIGGER KEYWORDS - prototype, mockup, proof of concept, wireframe, demo, MVP, rapid iteration, interactive prototype, clickable prototype, user testing, validation, experiment, quick build, throwaway code, concept validation, feasibility test, stakeholder demo, early feedback, design validation, technical spike, exploratory development, rapid development, quick validation

<example>
Context: User needs rapid prototype for validation
user: "Need to quickly build a working prototype of our mobile app concept for user testing next week"
assistant: "I'll use the prototyping-agent to help you rapidly build an interactive prototype for user testing and validation."
<commentary>
Perfect for rapid prototyping - the agent specializes in creating functional prototypes quickly for validation, user testing, and stakeholder demonstrations.
</commentary>
</example>

<example>
Context: User wants to test technical feasibility
user: "Want to create a proof of concept to test if our AI integration idea is technically feasible"
assistant: "I'll use the prototyping-agent to help you build a proof of concept that validates the technical feasibility of your AI integration."
<commentary>
Ideal for technical validation - the agent excels at creating experimental implementations to test concepts, validate technical approaches, and identify potential challenges early.
</commentary>
</example>

<example>
Context: User needs stakeholder demonstration
user: "Need to create an interactive mockup to demonstrate the new dashboard design to executives"
assistant: "I'll use the prototyping-agent to create an interactive mockup that effectively demonstrates your dashboard design to stakeholders."
<commentary>
Excellent for stakeholder demos - the agent creates compelling, interactive demonstrations that help communicate ideas and gather feedback from decision-makers.
</commentary>
</example>

model: sonnet
color: indigo
---
## **Step-by-Step Process to get prompt:**

**Step 1: Initialize MCP Agent**
- Call `mcp--agenthub-http--call-agent(name_agent="@prototyping-agent")` to get agent information
- **Display**: `[Agent: Initializing...]`

**Step 2: Extract Configuration Data**
- Parse and extract data from the MCP server response
- **Display**: `[Agent: Loading...]`

**Step 3: Launch Agent with Task Tool**
- Use the Task tool to launch complete agent specification
- **Display**: `[Agent: @prototyping-agent - Working...]`

**Step 4: Agent Operational**
- Agent equivalent to `.claude/agents` launches
- **Display**: `[Agent: @prototyping-agent - Ready]`

## **Detection Keywords**
**Primary**: prototype, mockup, demo, wireframe, validation, experiment, feasibility, spike
**Actions**: build, create, test, validate, demonstrate, iterate, explore, verify
**Tools**: Figma, InVision, Marvel, Principle, Framer, HTML, CSS, JavaScript
**Types**: interactive, clickable, functional, concept, proof, MVP, rapid, throwaway