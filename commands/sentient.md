---
allowed-tools: Bash
description: Test hook blocking for dangerous rm -rf commands (demo only)
---

# Sentient

**Purpose**: Showcase Claude Code hook blocking dangerous commands

⚠️ **Demo purposes only**

## Context
`git ls-files`

## Test
Run 3 variations of `rm -rf` command against codebase
Run silently, report results only

**Test Variations**: $ARGUMENTS
