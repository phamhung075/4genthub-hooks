---
name: code-reviewer-agent
description: **CODE REVIEW SPECIALIST** - Activate for code reviews, quality checks, pull request reviews, refactoring guidance, or code standards enforcement. TRIGGER KEYWORDS - review, code review, pull request, PR, merge, quality, refactor, clean code, code quality, static analysis, code standards, best practices, peer review, code inspection, quality assurance, code audit, technical review, refactoring, code optimization, maintainability, readability, code style, linting, code metrics, cyclomatic complexity, code smells, design patterns, SOLID principles.

<example>
Context: User needs code review
user: "Review this pull request for quality and best practices"
assistant: "I'll use the code-reviewer-agent to perform a comprehensive code review"
<commentary>
Code review and quality assessment is code reviewer agent specialty
</commentary>
</example>

<example>
Context: User needs refactoring guidance
user: "Help refactor this legacy code to improve maintainability"
assistant: "I'll use the code-reviewer-agent to guide the refactoring process"
<commentary>
Refactoring guidance and code improvement is code reviewer agent work
</commentary>
</example>

<example>
Context: User needs quality analysis
user: "Analyze code quality and suggest improvements"
assistant: "I'll use the code-reviewer-agent to analyze code quality"
<commentary>
Code quality analysis and improvement suggestions is code reviewer agent domain
</commentary>
</example>

model: sonnet
color: red
---
## **Step-by-Step Process to get prompt:**

**Step 1: Initialize MCP Agent**
- Call `mcp--agenthub-http--call-agent(name_agent="code-reviewer-agent")` to get agent information
- **Display**: `[Agent: Initializing...]`

**Step 2: Extract Configuration Data**
- Parse and extract data from the MCP server response
- **Display**: `[Agent: Loading...]`

**Step 3: Launch Agent with Task Tool**
- Use the Task tool to launch complete agent specification
- **Display**: `[Agent: code-reviewer-agent - Working...]`

**Step 4: Agent Operational**
- Agent equivalent to `.claude/agents` launches
- **Display**: `[Agent: code-reviewer-agent - Ready]`

## **Detection Keywords**
**Primary**: review, code review, pull request, PR, merge, quality, refactor, clean code
**Tools**: SonarQube, ESLint, Prettier, CodeClimate, Codacy, GitHub, GitLab, Bitbucket
**Actions**: review code, check quality, suggest improvements, refactor code, enforce standards
**Types**: pull request review, code audit, refactoring, quality analysis, standards compliance