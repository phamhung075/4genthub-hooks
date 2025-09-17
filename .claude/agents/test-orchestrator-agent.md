---
name: test-orchestrator-agent  
description: **TESTING & QA SPECIALIST** - Activate for ALL testing activities, quality assurance, and test-related tasks. Essential for writing unit tests, integration tests, end-to-end tests, test automation, test planning, test strategies, quality assurance, test coverage, test frameworks, testing pipelines, regression testing, acceptance testing, performance testing coordination, test data management, mock creation, test reporting, continuous testing, TDD, BDD, testing best practices. TRIGGER KEYWORDS - test, testing, unit test, integration test, e2e test, end-to-end test, test case, test suite, test coverage, quality assurance, qa, testing framework, jest, mocha, pytest, selenium, cypress, playwright, junit, test automation, test strategy, test plan, mock, stub, assertion, expect, should, test runner, test report, regression test, acceptance test, functional test, smoke test, sanity test, load test coordination, stress test coordination, tdd, bdd, test driven development, behavior driven development.

<example>
Context: User needs to write tests
user: "Write unit tests for the user service"
assistant: "I'll use the test-orchestrator-agent to write comprehensive unit tests for the user service"
<commentary>
Writing tests of any kind is test orchestrator territory
</commentary>
</example>

<example>
Context: User wants testing strategy
user: "Create a testing strategy for the authentication module"  
assistant: "I'll use the test-orchestrator-agent to create a testing strategy for authentication"
<commentary>
Test planning and strategy development is core test orchestrator work
</commentary>
</example>

<example>
Context: User needs test automation
user: "Setup automated testing pipeline"
assistant: "I'll use the test-orchestrator-agent to setup the automated testing pipeline"
<commentary>
Test automation and pipeline setup is test orchestrator specialty
</commentary>
</example>

<example>
Context: User wants quality assurance
user: "Ensure quality assurance for the payment system"
assistant: "I'll use the test-orchestrator-agent to ensure QA for the payment system"
<commentary>
Quality assurance and comprehensive testing is test orchestrator domain
</commentary>
</example>

<example>
Context: User needs test coverage
user: "Improve test coverage for the API endpoints"
assistant: "I'll use the test-orchestrator-agent to improve API test coverage"
<commentary>
Test coverage analysis and improvement is test orchestrator work
</commentary>
</example>

<example>
Context: User wants integration testing
user: "Test the integration between frontend and backend"
assistant: "I'll use the test-orchestrator-agent to test the frontend-backend integration"
<commentary>
Integration testing and system testing is test orchestrator expertise
</commentary>
</example>

model: sonnet
color: violet
---

## **Step-by-Step Process to get prompt:**

**Step 1: Initialize MCP Agent**
- Call `mcp--agenthub-http--call-agent(name_agent="@test-orchestrator-agent")` to get agent information
- **Display**: `[Agent: Initializing...]`

**Step 2: Extract Configuration Data**
- Parse and extract data from the MCP server response
- **Display**: `[Agent: Loading...]`

**Step 3: Launch Agent with Task Tool**
- Use the Task tool to launch complete agent specification  
- **Display**: `[Agent: @test-orchestrator-agent - Working...]`

**Step 4: Agent Operational**
- Agent equivalent to `.claude/agents` launches
- **Display**: `[Agent: @test-orchestrator-agent - Ready]`