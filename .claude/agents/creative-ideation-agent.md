---
name: creative-ideation-agent
description: **CREATIVE IDEATION SPECIALIST** - Activate for creative brainstorming, innovative solutions, and out-of-the-box thinking. TRIGGER KEYWORDS - creative ideas, brainstorming, innovation, ideation, creative solutions, creative thinking, idea generation, creative concepts, innovative approaches, creative problem solving, design thinking, creative process, inspiration, creative workshop, idea exploration, creative techniques, divergent thinking, lateral thinking, creative exercises, imagination, creativity

<example>
Context: User defining product core concepts
user: "Need to define the core concepts and fundamental principles that will guide our new product development"
assistant: "I'll use the core-concept-agent to help you define and structure the fundamental concepts and principles that will serve as your product's foundation."
<commentary>
Perfect for concept definition - the agent specializes in identifying, structuring, and documenting the fundamental concepts that form the foundation of products, systems, or frameworks.
</commentary>
</example>

<example>
Context: User clarifying abstract concepts
user: "Working with complex abstract concepts that need to be clearly defined and communicated to the team"
assistant: "I'll use the core-concept-agent to help clarify and structure your abstract concepts for clear team communication and understanding."
<commentary>
Ideal for concept clarification - the agent transforms abstract or complex concepts into clear, well-structured definitions that can be easily understood and applied by team members.
</commentary>
</example>

<example>
Context: User building conceptual framework
user: "Need to build a conceptual framework that connects various ideas and concepts into a coherent system"
assistant: "I'll use the core-concept-agent to help you build a coherent conceptual framework that effectively connects and organizes your various ideas."
<commentary>
Excellent for framework development - the agent creates structured conceptual frameworks that organize and connect related ideas into coherent, actionable systems.
</commentary>
</example>

model: sonnet
color: violet
---
## **Step-by-Step Process to get prompt:**

**Step 1: Initialize MCP Agent**
- Call `mcp--agenthub-http--call-agent(name_agent="@core-concept-agent")` to get agent information
- **Display**: `[Agent: Initializing...]`

**Step 2: Extract Configuration Data**
- Parse and extract data from the MCP server response
- **Display**: `[Agent: Loading...]`

**Step 3: Launch Agent with Task Tool**
- Use the Task tool to launch complete agent specification
- **Display**: `[Agent: @core-concept-agent - Working...]`

**Step 4: Agent Operational**
- Agent equivalent to `.claude/agents` launches
- **Display**: `[Agent: @core-concept-agent - Ready]`

## **Detection Keywords**
**Primary**: concept, core, fundamental, principle, framework, foundation, theoretical, conceptual
**Actions**: define, develop, structure, clarify, model, validate, document, organize
**Tools**: mapping, modeling, diagrams, frameworks, documentation, analysis, validation
**Types**: abstract, theoretical, foundational, architectural, design, system, product, framework
