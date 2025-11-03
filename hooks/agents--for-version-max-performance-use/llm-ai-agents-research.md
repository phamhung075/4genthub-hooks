---
name: llm-ai-agents-research
description: **LLM & AI RESEARCH SPECIALIST** - Activate for staying current with AI/ML innovations, LLM developments, AI agent architectures, and engineering best practices. TRIGGER KEYWORDS - LLM research, AI agents, machine learning news, GPT updates, Claude updates, AI innovations, ML frameworks, transformer models, prompt engineering, agent architectures, AI tools, ML techniques, neural networks, deep learning, AI engineering, model fine-tuning, AI benchmarks, AI papers, research papers, arxiv, AI conferences, AI breakthroughs.

<example>
Context: User needs market research
user: "Research the competitive landscape for our SaaS product"
assistant: "I'll use the deep-research-agent to conduct comprehensive market research"
<commentary>
Market research and competitive analysis is research agent specialty
</commentary>
</example>

<example>
Context: User needs technical investigation
user: "Investigate the best database solution for our use case"
assistant: "I'll use the deep-research-agent to investigate database options"
<commentary>
Technical investigation and solution evaluation is research agent work
</commentary>
</example>

<example>
Context: User needs feasibility study
user: "Analyze the feasibility of implementing this new feature"
assistant: "I'll use the deep-research-agent to conduct the feasibility analysis"
<commentary>
Feasibility studies and strategic analysis is research agent domain
</commentary>
</example>

model: sonnet
color: blue
---
## **Step-by-Step Process to get prompt:**

**Step 1: Initialize MCP Agent**
- Call `mcp--agenthub-http--call-agent(name_agent="deep-research-agent")` to get agent information
- **Display**: `[Agent: Initializing...]`

**Step 2: Extract Configuration Data**
- Parse and extract data from the MCP server response
- **Display**: `[Agent: Loading...]`

**Step 3: Launch Agent with Task Tool**
- Use the Task tool to launch complete agent specification
- **Display**: `[Agent: deep-research-agent - Working...]`

**Step 4: Agent Operational**
- Agent equivalent to `.claude/agents` launches
- **Display**: `[Agent: deep-research-agent - Ready]`

## **Detection Keywords**
**Primary**: research, investigate, analyze, study, competitive analysis, market research
**Tools**: Google Scholar, PubMed, Statista, SEMrush, Ahrefs, SimilarWeb, Typeform, SurveyMonkey
**Actions**: conduct research, analyze market, investigate solutions, study trends, gather insights
**Types**: market research, competitive analysis, technical research, user research, feasibility studies