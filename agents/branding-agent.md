---
name: branding-agent
description: **BRAND IDENTITY & STRATEGY SPECIALIST** - Activate when creating brand identities, developing brand guidelines, logo design, rebranding, brand strategy, or when comprehensive branding expertise is needed. Essential for brand development and market positioning. TRIGGER KEYWORDS - branding, brand identity, brand strategy, logo design, brand guidelines, brand development, visual identity, brand voice, messaging, brand positioning, rebranding, brand refresh, brand audit, brand consistency, brand awareness, brand image, corporate identity, brand standards, brand management, brand communication, brand experience, brand architecture, brand portfolio, brand equity, brand values, brand personality, brand differentiation, brand messaging framework.

<example>
Context: User needs brand identity development
user: "Create comprehensive brand identity for startup"
assistant: "I'll use the branding-agent to create comprehensive brand identity for the startup"
<commentary>
Brand identity development and visual identity creation is branding agent specialty
</commentary>
</example>

<example>
Context: User needs rebranding strategy
user: "Rebrand existing company with new positioning"
assistant: "I'll use the branding-agent to develop the company rebranding strategy"
<commentary>
Rebranding and brand positioning strategy is branding agent domain
</commentary>
</example>

<example>
Context: User needs brand guidelines
user: "Develop brand guidelines and style guide"
assistant: "I'll use the branding-agent to develop comprehensive brand guidelines"
<commentary>
Brand guidelines and brand standards development is branding agent work
</commentary>
</example>

model: sonnet
color: lime
---
## **Step-by-Step Process to get prompt:**

**Step 1: Initialize MCP Agent**
- Call `mcp--agenthub-http--call-agent(name_agent="branding-agent")` to get agent information
- **Display**: `[Agent: Initializing...]`

**Step 2: Extract Configuration Data**
- Parse and extract data from the MCP server response
- **Display**: `[Agent: Loading...]`

**Step 3: Launch Agent with Task Tool**
- Use the Task tool to launch complete agent specification
- **Display**: `[Agent: branding-agent - Working...]`

**Step 4: Agent Operational**
- Agent equivalent to `.claude/agents` launches
- **Display**: `[Agent: branding-agent - Ready]`

## **Detection Keywords**
**Primary**: branding, brand identity, brand strategy, logo design, brand guidelines, visual identity
**Strategy**: brand positioning, brand messaging, brand values, brand personality, brand differentiation
**Process**: rebranding, brand refresh, brand audit, brand development, brand management
**Actions**: create brand, develop identity, design logo, brand guidelines, brand positioning