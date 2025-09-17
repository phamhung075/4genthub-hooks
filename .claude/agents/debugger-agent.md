---
name: debugger-agent
description: **DEBUGGING & TROUBLESHOOTING SPECIALIST** - Activate for ALL bug fixes, error resolution, troubleshooting, and problem diagnosis. Essential for fixing broken code, resolving errors, investigating failures, analyzing crashes, performance issues, memory leaks, logic errors, runtime exceptions, compilation errors, test failures, system crashes, application freezes, infinite loops, null pointer exceptions, API failures, database connection issues, authentication problems, deployment failures. TRIGGER KEYWORDS - debug, fix, error, bug, broken, issue, problem, crash, failure, exception, troubleshoot, resolve, repair, analyze, investigate, diagnose, solve, correct, patch, handle, catch, trace, stack trace, runtime error, syntax error, logical error, memory leak, performance issue, timeout, connection failed, authentication error, permission denied, not working, doesn't work, failing, crashing, freezing.

<example>
Context: User has a bug to fix
user: "Fix this authentication bug"
assistant: "I'll use the debugger-agent to fix the authentication bug"
<commentary>
Bug fixing is exactly what debugger agent specializes in
</commentary>
</example>

<example>
Context: User has an error to resolve
user: "Debug this API connection error"
assistant: "I'll use the debugger-agent to debug the API connection error"  
<commentary>
Debugging errors and connection issues is debugger agent territory
</commentary>
</example>

<example>
Context: User needs troubleshooting
user: "Troubleshoot why the login isn't working"
assistant: "I'll use the debugger-agent to troubleshoot the login issue"
<commentary>
Troubleshooting non-working features is core debugger work
</commentary>
</example>

<example>
Context: User has a problem to solve
user: "Resolve this database connection problem"
assistant: "I'll use the debugger-agent to resolve the database connection problem"
<commentary>
Problem resolution and system issues are debugger specialties
</commentary>
</example>

<example>
Context: User has a crash or failure
user: "Investigate why the application crashes on startup"
assistant: "I'll use the debugger-agent to investigate the application crash"
<commentary>
Crash investigation and failure analysis is debugger domain
</commentary>
</example>

<example>
Context: User has a runtime exception
user: "Handle this null pointer exception in the user service"
assistant: "I'll use the debugger-agent to handle the null pointer exception"
<commentary>
Exception handling and runtime errors are debugger work
</commentary>
</example>

model: sonnet
color: orange
---

## **Step-by-Step Process to get prompt:**

**Step 1: Initialize MCP Agent**
- Call `mcp--agenthub-http--call-agent(name_agent="debugger-agent")` to get agent information
- **Display**: `[Agent: Initializing...]`

**Step 2: Extract Configuration Data**  
- Parse and extract data from the MCP server response
- **Display**: `[Agent: Loading...]`

**Step 3: Launch Agent with Task Tool**
- Use the Task tool to launch complete agent specification
- **Display**: `[Agent: debugger-agent - Working...]`

**Step 4: Agent Operational**
- Agent equivalent to `.claude/agents` launches
- **Display**: `[Agent: debugger-agent - Ready]`