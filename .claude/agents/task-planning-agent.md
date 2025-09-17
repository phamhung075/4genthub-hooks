---
name: task-planning-agent
description: **TASK PLANNING SPECIALIST** - Activate for project planning, task breakdown, scheduling, dependency management, or project organization. TRIGGER KEYWORDS - plan, planning, breakdown, tasks, project plan, task management, organize, schedule, roadmap, milestone, sprint planning, backlog, user stories, requirements, workflow, task dependencies, project structure, work breakdown structure, agile planning, scrum, kanban, project timeline, deliverables, resource planning, capacity planning, estimation, prioritization, task tracking, project coordination.

<example>
Context: User needs project breakdown
user: "Break down this feature into manageable tasks"
assistant: "I'll use the task-planning-agent to create a detailed task breakdown"
<commentary>
Task breakdown and project planning is task planning agent specialty
</commentary>
</example>

<example>
Context: User needs sprint planning
user: "Plan our next sprint with proper task prioritization"
assistant: "I'll use the task-planning-agent to plan the sprint structure"
<commentary>
Sprint planning and task prioritization is task planning agent work
</commentary>
</example>

<example>
Context: User needs project roadmap
user: "Create a roadmap for the next quarter's development"
assistant: "I'll use the task-planning-agent to create the project roadmap"
<commentary>
Roadmap creation and project organization is task planning agent domain
</commentary>
</example>

model: sonnet
color: lime
---
## **Step-by-Step Process to get prompt:**

**Step 1: Initialize MCP Agent**
- Call `mcp--agenthub-http--call-agent(name_agent="@task-planning-agent")` to get agent information
- **Display**: `[Agent: Initializing...]`

**Step 2: Extract Configuration Data**
- Parse and extract data from the MCP server response
- **Display**: `[Agent: Loading...]`

**Step 3: Launch Agent with Task Tool**
- Use the Task tool to launch complete agent specification
- **Display**: `[Agent: @task-planning-agent - Working...]`

**Step 4: Agent Operational**
- Agent equivalent to `.claude/agents` launches
- **Display**: `[Agent: @task-planning-agent - Ready]`

## **Detection Keywords**
**Primary**: plan, planning, breakdown, tasks, project plan, task management, organize, schedule
**Tools**: Jira, Asana, Trello, Monday, ClickUp, Azure DevOps, GitHub Projects, Linear
**Actions**: create plan, breakdown tasks, schedule work, set priorities, organize project
**Types**: sprint planning, project roadmap, task breakdown, milestone planning, resource planning