---
description: Create prompts to fix test failures in parallel sessions
---

# Prompt For Claude Dev Fix Test

**Purpose**: Generate prompts for parallel test failure fixes

## Workflow
1. Call master-orchestrator-agent → Load role
2. Analyze test failures
3. Create MCP tasks for issues
4. Provide prompts for parallel execution

**Test Failures**: $ARGUMENTS
