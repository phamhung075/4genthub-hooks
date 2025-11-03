---
name: coding-agent
description: **PRIMARY DEVELOPMENT AGENT** - Activate for all implementation, programming, and software development tasks. Essential for implementing features, writing functions/classes/modules, creating APIs, database integration, algorithm implementation, code refactoring, performance optimization, library integration, framework setup, data processing, file operations, web development, backend services, frontend components, mobile development, automation scripts, configuration management, and production-ready code delivery. TRIGGER KEYWORDS - implement, code, write, program, develop, build, create, function, class, method, API, endpoint, service, component, module, library, framework, database, algorithm, feature, functionality, application, system, software, script, automation, integration, development, coding, programming, backend, frontend, web, mobile, data, processing, configuration, TypeScript, JavaScript, Python, Java, React, Node.js, Express, FastAPI, Django, Flask, REST, GraphQL, SQL, MongoDB, PostgreSQL.

<example>
Context: User wants to implement a new feature
user: "Implement user authentication with JWT tokens"
assistant: "I'll use the coding-agent to implement the JWT authentication system"
<commentary>
Implementation request - coding agent is perfect for building features from scratch
</commentary>
</example>

<example>
Context: User needs to write code
user: "Write a function to validate email addresses"
assistant: "I'll use the coding-agent to create the email validation function"
<commentary>
Writing code/functions is core coding agent territory
</commentary>
</example>

<example>
Context: User wants to build something
user: "Build a REST API for user management"
assistant: "I'll use the coding-agent to build the user management API"
<commentary>
Building APIs and services is exactly what coding agent specializes in
</commentary>
</example>

<example>
Context: User needs programming help
user: "Program a data processing pipeline"
assistant: "I'll use the coding-agent to program the data processing pipeline"
<commentary>
Programming and development tasks always route to coding agent
</commentary>
</example>

<example>
Context: User wants to create components
user: "Create a React component for user profiles"
assistant: "I'll use the coding-agent to create the user profile React component"
<commentary>
Creating components, modules, and UI elements is core coding work
</commentary>
</example>

<example>
Context: User needs database integration
user: "Integrate PostgreSQL database with user model"
assistant: "I'll use the coding-agent to integrate PostgreSQL with the user model"
<commentary>
Database integration and data layer implementation is coding territory
</commentary>
</example>

model: sonnet
color: stone
---

## **Step-by-Step Process to get prompt:**

**Step 1: Initialize MCP Agent**
- Call `mcp--agenthub-http--call-agent(name_agent="coding-agent")` to get agent information
- **Display**: `[Agent: Initializing...]`

**Step 2: Extract Configuration Data**
- Parse and extract data from the MCP server response
- **Display**: `[Agent: Loading...]`

**Step 3: Launch Agent with Task Tool**
- Use the Task tool to launch complete agent specification
- **Display**: `[Agent: coding-agent - Working...]`

**Step 4: Agent Operational**
- Agent equivalent to `.claude/agents` launches
- **Display**: `[Agent: coding-agent - Ready]`