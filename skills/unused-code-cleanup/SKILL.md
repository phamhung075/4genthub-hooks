---
name: unused-code-cleanup
description: Systematically identify and remove unused imports, variables, and dead code from TypeScript/React projects using --noUnusedLocals and --noUnusedParameters compiler flags
allowed-tools: Read, Edit, Bash, Grep
---

# Unused Code Cleanup

Systematically identify and remove unused imports, variables, and dead code from TypeScript/React projects using TypeScript compiler flags.

## When to Use

- TypeScript projects with unused code warnings
- React applications with unused imports/variables
- Code quality improvement initiatives
- After major refactoring or feature removal
- Pre-production cleanup for bundle size optimization

## Detection Method

### Run Detection
```bash
npx tsc --noEmit --noUnusedLocals --noUnusedParameters 2>&1 | grep "error TS6133"
```

### Count Warnings
```bash
npx tsc --noEmit --noUnusedLocals --noUnusedParameters 2>&1 | grep "error TS6133" | wc -l
```

### Find High-Impact Files
```bash
npx tsc --noEmit --noUnusedLocals --noUnusedParameters 2>&1 | grep "error TS6133" | sed 's/([0-9]*,[0-9]*).*//' | sort | uniq -c | sort -rn | head -15
```

## Common Patterns

| Pattern | Typical Cause | Impact |
|---------|---------------|--------|
| **Unused imports** | Icon libraries, API types | Quick wins, smaller bundle |
| **Dead feature infrastructure** | Feature removed but code remains | Reveals entire subsystems |
| **Unused parameters** | React Query error callbacks | Clean code conventions |
| **Debug snapshots** | Debugging code left in | Runtime performance |
| **Unused props** | Component refactoring | Interface clarity |
| **Unused hooks** | Removed functionality | Prevent unnecessary renders |

## Cleanup Strategy

### 1. Prioritize High-Impact Files
Target files with 10+ warnings first for maximum impact

### 2. Identify Patterns
- Unused imports → Quick wins
- Unused state → May reveal dead features
- Unused parameters → Error callbacks, arrow functions
- Unused variables → Debug snapshots

### 3. Verify After Each Major File
```bash
npm run build
npx tsc --noEmit --noUnusedLocals --noUnusedParameters 2>&1 | grep "error TS6133" | wc -l
```

### 4. Update Progress
Track warnings eliminated: Start count → Current count

## Key Insights

**Cascading Dependencies**: Removing unused state reveals unused setters → unused conversion functions → entire dead feature subsystems

**Performance Benefits**:
- Removing unused `getQueryData()` calls improves runtime
- Smaller bundle size from unused import removal
- Faster TypeScript compilation

**Debug Code Archaeology**: `beforeCache`/`afterCache` variables reveal debugging history, often paired with removed console.log statements

## Common Mistakes to Avoid

| Mistake | Issue | Solution |
|---------|-------|----------|
| **Remove used destructured variables** | `error` might be used later | Check all references |
| **Miss dynamic calls** | String references to functions | Search for function name |
| **No build verification** | Reflection/dynamic imports break | Run build after each file |
| **Remove API-required params** | Breaking callback signature | Use `_` for unused params |

## Examples

See **[EXAMPLES.md](EXAMPLES.md)** for detailed patterns:
- Unused icon imports
- Dead feature infrastructure
- React Query error callbacks
- Debug snapshot variables
- Unused component props
- Arrow function parameters
- React Query client
- Validation variables
- API imports

## Templates

See **[TEMPLATES.md](TEMPLATES.md)** for copy-paste solutions:
- Detection commands
- Cleanup workflows
- Import cleanup
- Parameter replacement
- Props interface cleanup

## Validation

See **[VALIDATION.md](VALIDATION.md)** for quality checks:
- Pre-cleanup verification
- Post-cleanup testing
- Progress tracking
- Metrics collection

## Session Metrics

**Example Session (2025-11-08)**:
- **Warnings**: 148 → 101 (32% reduction)
- **Files cleaned**: 6
- **Items removed**: 47
- **Build time**: 15.30s

| File | Warnings | Items Removed |
|------|----------|---------------|
| BranchContextDialog.tsx | 22 | Icons, parsing functions, state variables |
| useRealtimeSync.ts | 12 | Debug snapshot variables |
| useSubtasks.ts | 4 | Unused onError parameters |
| useTasks.ts | 2 | Unused onError parameters |
| api-lazy.ts | 4 | Unused type/API imports |
| LazySubtaskList/* | 5 | queryClient, props, parameters |

## Automation Opportunities

### ESLint Rules
```json
{
  "rules": {
    "@typescript-eslint/no-unused-vars": ["error", {
      "argsIgnorePattern": "^_",
      "varsIgnorePattern": "^_"
    }]
  }
}
```

### Pre-commit Hook
```bash
#!/bin/bash
unused_count=$(npx tsc --noEmit --noUnusedLocals --noUnusedParameters 2>&1 | grep "error TS6133" | wc -l)
if [ $unused_count -gt 0 ]; then
  echo "⚠️  Warning: $unused_count unused code warnings found"
fi
```

## Quick Reference

| Task | Command |
|------|---------|
| Detect unused | `npx tsc --noEmit --noUnusedLocals --noUnusedParameters` |
| Count warnings | `... \| grep "error TS6133" \| wc -l` |
| High-impact files | `... \| sed 's/([0-9]*,[0-9]*).*//' \| sort \| uniq -c \| sort -rn` |
| Verify build | `npm run build` |
| Check TypeScript | `npx tsc --noEmit` |

## Supporting Files

- **[EXAMPLES.md](EXAMPLES.md)** - 9 common patterns with before/after code examples
- **[TEMPLATES.md](TEMPLATES.md)** - Copy-paste cleanup templates for each pattern
- **[VALIDATION.md](VALIDATION.md)** - Quality checks, verification commands, metrics tracking
