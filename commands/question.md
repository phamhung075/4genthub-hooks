---
allowed-tools: Bash(git ls-files:*), Read
description: Answer questions about project structure/documentation without coding
---

# Question

**Purpose**: Answer questions by analyzing project structure - NO code changes

| Rule | Action |
|------|--------|
| **NO** file creation/editing | Only read and analyze |
| Focus | Understanding existing code/structure |
| Response | Clear answers based on analysis |
| Code changes requested | Explain conceptually, don't implement |

## Execute
`git ls-files` → Understand project structure

## Read
`README.md` → Project overview

## Workflow
1. Review structure from git ls-files
2. Understand project purpose from README
3. Connect question to relevant parts
4. Provide answer with evidence

## Response Format
- Direct answer
- Supporting evidence
- Documentation references
- Conceptual explanations

**Question**: $ARGUMENTS