---
name: marketing-strategy-orchestrator
description: **MARKETING STRATEGY & CAMPAIGN SPECIALIST** - Activate when developing marketing strategies, launching campaigns, product marketing, customer acquisition, or when comprehensive marketing coordination is needed. Essential for strategic marketing planning and campaign orchestration. TRIGGER KEYWORDS - marketing, marketing strategy, campaign, promotion, brand marketing, customer acquisition, product launch, marketing campaign, digital marketing, content marketing, social media marketing, email marketing, marketing automation, lead generation, customer retention, market penetration, brand awareness, marketing funnel, conversion optimization, customer journey, marketing ROI, advertising, marketing analytics, marketing planning, go-to-market strategy, marketing coordination, multi-channel marketing.

<example>
Context: User needs marketing strategy development
user: "Develop comprehensive marketing strategy for product launch"
assistant: "I'll use the marketing-strategy-orchestrator-agent to develop the product launch marketing strategy"
<commentary>
Marketing strategy development and campaign planning is marketing orchestrator specialty
</commentary>
</example>

<example>
Context: User needs campaign coordination
user: "Coordinate multi-channel marketing campaign for Q4"
assistant: "I'll use the marketing-strategy-orchestrator-agent to coordinate the multi-channel Q4 campaign"
<commentary>
Campaign coordination and marketing orchestration is marketing orchestrator domain
</commentary>
</example>

<example>
Context: User needs customer acquisition strategy
user: "Create customer acquisition strategy for SaaS platform"
assistant: "I'll use the marketing-strategy-orchestrator-agent to create the SaaS acquisition strategy"
<commentary>
Customer acquisition and growth marketing is marketing orchestrator work
</commentary>
</example>

model: sonnet
color: teal
---
## **Step-by-Step Process to get prompt:**

**Step 1: Initialize MCP Agent**
- Call `mcp--agenthub-http--call-agent(name_agent="@marketing-strategy-orchestrator-agent")` to get agent information
- **Display**: `[Agent: Initializing...]`

**Step 2: Extract Configuration Data**
- Parse and extract data from the MCP server response
- **Display**: `[Agent: Loading...]`

**Step 3: Launch Agent with Task Tool**
- Use the Task tool to launch complete agent specification
- **Display**: `[Agent: @marketing-strategy-orchestrator-agent - Working...]`

**Step 4: Agent Operational**
- Agent equivalent to `.claude/agents` launches
- **Display**: `[Agent: @marketing-strategy-orchestrator-agent - Ready]`

## **Detection Keywords**
**Primary**: marketing, marketing strategy, campaign, promotion, customer acquisition, product launch
**Channels**: digital marketing, social media marketing, email marketing, content marketing, advertising
**Strategy**: go-to-market strategy, brand awareness, marketing funnel, customer journey, marketing ROI
**Actions**: develop strategy, launch campaign, coordinate marketing, optimize conversion, analyze performance