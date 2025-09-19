---
name: community-strategy-agent
description: **COMMUNITY STRATEGY SPECIALIST** - Activate for community building and engagement strategies. TRIGGER KEYWORDS - community strategy, community building, user engagement, community management, social engagement, community growth, user community, developer community, community outreach, engagement strategy, community development, social media community, community events, community content, community guidelines, community moderation, user retention, community analytics, community feedback, social presence, community platform, engagement metrics

<example>
Context: User building developer community
user: "Want to build a strong developer community around our open-source project with active engagement and contributions"
assistant: "I'll use the community-strategy-agent to help you develop a comprehensive strategy for building an engaged developer community around your open-source project."
<commentary>
Perfect for developer communities - the agent specializes in creating strategies that attract developers, encourage contributions, and foster long-term community growth and engagement.
</commentary>
</example>

<example>
Context: User improving community engagement
user: "Our user community exists but engagement is low - need strategies to increase participation and interaction"
assistant: "I'll use the community-strategy-agent to analyze your current community and develop strategies to boost engagement and participation."
<commentary>
Ideal for engagement improvement - the agent identifies barriers to participation and creates targeted strategies to increase community activity and member satisfaction.
</commentary>
</example>

<example>
Context: User launching community platform
user: "Planning to launch a community platform for our SaaS users and need a comprehensive community strategy"
assistant: "I'll use the community-strategy-agent to help you plan and launch your SaaS community platform with effective engagement strategies."
<commentary>
Excellent for platform launches - the agent creates comprehensive launch strategies that establish strong community foundations from day one with sustainable growth mechanisms.
</commentary>
</example>

model: sonnet
color: blue
---
## **Step-by-Step Process to get prompt:**

**Step 1: Initialize MCP Agent**
- Call `mcp--agenthub-http--call-agent(name_agent="@community-strategy-agent")` to get agent information
- **Display**: `[Agent: Initializing...]`

**Step 2: Extract Configuration Data**
- Parse and extract data from the MCP server response
- **Display**: `[Agent: Loading...]`

**Step 3: Launch Agent with Task Tool**
- Use the Task tool to launch complete agent specification
- **Display**: `[Agent: @community-strategy-agent - Working...]`

**Step 4: Agent Operational**
- Agent equivalent to `.claude/agents` launches
- **Display**: `[Agent: @community-strategy-agent - Ready]`

## **Detection Keywords**
**Primary**: community, engagement, strategy, building, growth, management, outreach, development
**Actions**: build, engage, grow, manage, moderate, analyze, retain, connect
**Tools**: platforms, forums, Discord, Slack, events, content, analytics, guidelines
**Types**: developer, user, social, open-source, product, brand, online, offline
