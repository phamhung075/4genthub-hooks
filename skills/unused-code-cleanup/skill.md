# Unused Code Cleanup Skill

## Purpose
Systematically identify and remove unused imports, variables, and dead code from TypeScript/React projects using TypeScript compiler flags `--noUnusedLocals` and `--noUnusedParameters`.

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

## Common Patterns & Solutions

### 1. Unused Icon Imports
**Pattern:**
```typescript
import { Save, X, Globe, FolderOpen } from "lucide-react";
// Only GitBranch is actually used
```

**Solution:** Remove unused icons from import
```typescript
import { GitBranch } from "lucide-react";
```

### 2. Dead Feature Infrastructure
**Pattern:** Entire feature removed but infrastructure remains
- Unused state variables
- Unused setter functions
- Unused conversion/parsing functions
- Unused helper functions

**Example (BranchContextDialog.tsx):**
- Removed edit mode → 22 items cleaned:
  - 9 icon imports
  - 3 parsing functions (parseKeyValueMarkdown, parseFeatureFlagsMarkdown, parseListMarkdown)
  - 3 converter functions (keyValueToMarkdown, featureFlagsToMarkdown, listToMarkdown)
  - 10 state variables (markdown content for each section)

**Approach:**
1. Identify unused state variables
2. Find their setter calls
3. Find functions only called by those setters
4. Remove entire feature subsystem

### 3. React Query Error Callbacks - Unused Parameters
**Pattern:**
```typescript
onError: (err, { taskId }, context: any) => {
  logger.error('Failed:', err);
  // taskId never used, only context.taskId
}
```

**Solution:** Replace with underscore
```typescript
onError: (err, _, context: any) => {
  logger.error('Failed:', err);
  // Clean and follows convention
}
```

**Files cleaned:** useSubtasks.ts (4), useTasks.ts (2)

### 4. Debug Snapshot Variables
**Pattern:** Cache snapshots for debugging never used
```typescript
const beforeCache = queryClient.getQueryData(['tasks']);
queryClient.setQueryData(['tasks'], newData);
const afterCache = queryClient.getQueryData(['tasks']);
// beforeCache and afterCache declared but never read
```

**Solution:** Remove snapshot calls
```typescript
queryClient.setQueryData(['tasks'], newData);
```

**Files cleaned:** useRealtimeSync.ts (12 debug variables)

### 5. Unused Component Props
**Pattern:**
```typescript
interface Props {
  onDetailsDialogChange: (open: boolean) => void; // Unused
  onActiveDialogChange: (dialog: ActiveDialogState) => void;
}

function Component({
  onDetailsDialogChange,  // Unused
  onActiveDialogChange
}: Props) {
  // onDetailsDialogChange never called
}
```

**Solution:** Remove from interface and destructuring
```typescript
interface Props {
  onActiveDialogChange: (dialog: ActiveDialogState) => void;
}

function Component({ onActiveDialogChange }: Props) {
  // Clean
}
```

### 6. Unused Arrow Function Parameters
**Pattern:**
```typescript
onActiveDialogChange={(dialog) => {/* dialog never used */}}
```

**Solution:**
```typescript
onActiveDialogChange={() => {/* clean */}}
```

### 7. Unused React Query Client
**Pattern:**
```typescript
const queryClient = useQueryClient();
// Never used in component
```

**Solution:** Remove the hook call entirely

### 8. Unused Validation Variables
**Pattern:**
```typescript
if (!isValidPayload(data)) {
  const invalidData = data as any; // Never used
  logger.warn('Invalid payload');
  return;
}
```

**Solution:**
```typescript
if (!isValidPayload(data)) {
  logger.warn('Invalid payload');
  return;
}
```

### 9. Unused API Imports
**Pattern:**
```typescript
import { Project, Task, Subtask } from './api';
import { projectApiV2, taskApiV2, subtaskApiV2 } from './services/apiV2';
// Only Subtask, taskApiV2, subtaskApiV2 used
```

**Solution:**
```typescript
import { Subtask } from './api';
import { taskApiV2, subtaskApiV2 } from './services/apiV2';
```

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

## Files Cleaned (Session 2025-11-08)

| File | Warnings | Items Removed |
|------|----------|---------------|
| BranchContextDialog.tsx | 22 | Icons, parsing functions, state variables, dead edit mode |
| useRealtimeSync.ts | 12 | Debug snapshot variables (beforeCache, afterCache, invalidData) |
| useSubtasks.ts | 4 | Unused onError parameters |
| useTasks.ts | 2 | Unused onError parameters |
| api-lazy.ts | 4 | Unused type/API imports |
| LazySubtaskList/* | 5 | queryClient, props, parameters |

**Result:** 148 → 101 warnings (32% reduction, 47 items removed)

## Key Insights

### Cascading Dependencies
Removing unused state reveals:
1. Unused setter calls
2. Unused conversion functions
3. Unused parsing functions
4. Entire dead feature subsystems

### Performance Benefits
- Removing unused `getQueryData()` calls improves runtime
- Smaller bundle size from unused import removal
- Faster TypeScript compilation

### Debug Code Archaeology
- `beforeCache`/`afterCache` variables reveal debugging history
- Often paired with console.log statements (since removed)
- Common in React Query mutation optimistic updates

### React Import Pattern
Many components have `import React from 'react'` but don't use JSX namespace.
Modern React (17+) doesn't require this import.

## Common Mistakes to Avoid

1. **Don't remove used destructured variables**
   ```typescript
   const { data, error } = useQuery(); // error might be used later
   ```

2. **Check all occurrences before removing functions**
   - Search for function name usage
   - Check for dynamic calls via string references

3. **Verify build after major removals**
   - Unused doesn't always mean safe to remove
   - Some code used via reflection/dynamic imports

4. **Keep context parameters even if unused**
   ```typescript
   // Keep context even if unused - API requirement
   onError: (err, _, context: any) => { }
   ```

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

## Next Steps for This Project

Remaining 101 warnings across:
- TaskDetailsDialog.tsx (11)
- useBranches.ts (6)
- useSubtasks.ts (5)
- SubtaskRow.tsx (5)
- TaskRow.tsx (4)
- 40+ files with 1-3 warnings each

Same patterns as cleaned files - can be automated or done in future session.
