---
description: Complete MCP tools testing plan (project/branch/task/subtask)
---

# Test MCP

**Purpose**: Test all MCP tool actions systematically

## Test Checklist

| Test | Actions |
|------|---------|
| Projects | Create 2, get, list, update, health check, set context, delete 1 |
| Branches | Create 2, get, list, update, assign agent, set context, delete 1 |
| Tasks (Branch 1) | Create 2, update, get, list, search, next, dependencies, assign agent |
| Tasks (Branch 2) | Same as Branch 1 |
| Subtasks (Branch 1) | Create 2 per task, update, list, get, complete all for 1 task → complete task |
| Issues | Summarize all issues in `.md` format → `ai_docs/` |
| Fix Prompts | Write detailed prompts per issue in same `.md` |

**Additional Test Parameters**: $ARGUMENTS
