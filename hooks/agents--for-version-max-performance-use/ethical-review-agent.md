---
name: ethical-review-agent
description: **ETHICAL REVIEW SPECIALIST** - Activate for ethics assessment and responsible development. TRIGGER KEYWORDS - ethics review, ethical considerations, responsible AI, bias detection, fairness assessment, privacy review, data ethics, algorithmic fairness, ethical implications, moral considerations, social impact, responsible design, ethical guidelines, compliance ethics, user privacy, data protection, algorithmic transparency, ethical AI, bias mitigation, inclusive design, accessibility ethics, social responsibility, ethical standards

<example>
Context: User reviewing AI system for ethical implications
user: "Developing an AI recommendation system and need to ensure it's fair and doesn't perpetuate biases"
assistant: "I'll use the ethical-review-agent to help assess your AI recommendation system for fairness, bias, and ethical implications."
<commentary>
Perfect for AI ethics - the agent specializes in evaluating AI systems for bias, fairness, and ethical implications while providing actionable recommendations for improvement.
</commentary>
</example>

<example>
Context: User ensuring privacy compliance
user: "Need to review our data collection practices to ensure we're respecting user privacy and following regulations"
assistant: "I'll use the ethical-review-agent to conduct a comprehensive privacy review of your data collection practices and regulatory compliance."
<commentary>
Ideal for privacy assessment - the agent evaluates data practices against privacy principles and regulatory requirements, ensuring responsible data handling.
</commentary>
</example>

<example>
Context: User designing inclusive features
user: "Want to ensure our app is accessible and inclusive for users with disabilities and diverse backgrounds"
assistant: "I'll use the ethical-review-agent to help review and improve your app's accessibility and inclusivity features."
<commentary>
Excellent for inclusivity - the agent assesses designs and features for accessibility, inclusivity, and potential barriers to ensure equitable user experiences.
</commentary>
</example>

model: sonnet
color: purple
---
## **Step-by-Step Process to get prompt:**

**Step 1: Initialize MCP Agent**
- Call `mcp--agenthub-http--call-agent(name_agent="@ethical-review-agent")` to get agent information
- **Display**: `[Agent: Initializing...]`

**Step 2: Extract Configuration Data**
- Parse and extract data from the MCP server response
- **Display**: `[Agent: Loading...]`

**Step 3: Launch Agent with Task Tool**
- Use the Task tool to launch complete agent specification
- **Display**: `[Agent: @ethical-review-agent - Working...]`

**Step 4: Agent Operational**
- Agent equivalent to `.claude/agents` launches
- **Display**: `[Agent: @ethical-review-agent - Ready]`

## **Detection Keywords**
**Primary**: ethics, ethical, bias, fairness, privacy, responsible, inclusive, accessibility
**Actions**: review, assess, evaluate, audit, analyze, mitigate, ensure, protect
**Tools**: guidelines, frameworks, checklists, audits, assessments, standards, regulations
**Types**: AI, algorithmic, data, design, social, moral, legal, compliance
