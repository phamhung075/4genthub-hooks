# Templates

## #1: Table
```markdown
| [Col1] | [Col2] | [Col3] |
|--------|--------|--------|
| [Val] | [Val] | [Val] |
```

## #2: Bullets with Pipes
```markdown
**[Concept]**: [Part1] | [Part2] | [Part3]
```

## #3: Numbered Steps
```markdown
1. [Step] → [Result]
2. [Condition] → IF [x]: [do] | ELSE: [do]
```

## #4: One Example
```[lang]
[3-5 KEY LINES ONLY]
```

## #5: Pattern
```markdown
**Pattern**: All [category] [what they do].
```

## #6: Why
```markdown
**[Decision]**
**Why**: [1-2 line reason]
```

## #7: Error
```markdown
**Error**: `[EXACT MESSAGE]`
**Fix**: [Solution]
```

## #8: No Fluff
Use `##` headers, not ASCII/emojis/decorations

## #9: Scannable
```markdown
## [Topic]
**[Critical]**
Details: [how]
Context: [why]
```

## #10: Consolidate
Merge duplicate sections into one table/list

## #11: Compact Code
```[lang]
[3-5 lines]
// ...
```

## #12: Quick List
```markdown
| Task | Command |
| [T] | `[cmd]` |
```

## #13: Inverted Pyramid
Critical info first → Details → Context → Optional

## #14: Verbosity
- Complex/critical: HIGH (detailed)
- Routine: LOW (one line)

## #15: No Teaching
```markdown
**[func]([params])**: [Does what]
```
Not: "Let me explain what X is..."

## MCP

**Task**:
```
Requirements: [WHAT]
Files: [PATH:LINES] (action)
Acceptance: [CRITERIA]
Why: [CONTEXT]
```

**progress_notes**: `[ACTION] [WHAT]. [NEXT].`

**completion_summary**: `[DONE]. [TECH]. Files: [PATHS]. [IMPACT].`

## Placeholders

- [WHAT]: JWT auth, Cache fix
- [PATH:LINES]: auth.js:45-67
- [CRITERIA]: Tests passing
- [WHY]: SOC2, Performance
- [IMPACT]: 50% faster
