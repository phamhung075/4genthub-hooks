# Unused Code Cleanup Examples

Real-world patterns for identifying and removing unused code in TypeScript/React projects.

## Pattern Summary

| # | Pattern | Typical Location | Cleanup Difficulty |
|---|---------|------------------|-------------------|
| 1 | Unused icon imports | Component headers | Easy |
| 2 | Dead feature infrastructure | Throughout component | Complex |
| 3 | React Query error callbacks | Hook definitions | Easy |
| 4 | Debug snapshot variables | Mutation handlers | Easy |
| 5 | Unused component props | Component interfaces | Medium |
| 6 | Unused arrow function params | Event handlers | Easy |
| 7 | Unused React Query client | Component body | Easy |
| 8 | Unused validation variables | Validation blocks | Easy |
| 9 | Unused API imports | File headers | Easy |

## Pattern 1: Unused Icon Imports

**Context**: Imported multiple icons from lucide-react but only using one

**Before** (BranchContextDialog.tsx):
```typescript
import { Save, X, Globe, FolderOpen, GitBranch } from "lucide-react";

function BranchContextDialog() {
  return (
    <div>
      <GitBranch className="icon" />
      {/* Only GitBranch is actually used */}
    </div>
  );
}
```

**Detection**:
```
error TS6133: 'Save' is declared but its value is never read.
error TS6133: 'X' is declared but its value is never read.
error TS6133: 'Globe' is declared but its value is never read.
error TS6133: 'FolderOpen' is declared but its value is never read.
```

**After**:
```typescript
import { GitBranch } from "lucide-react";

function BranchContextDialog() {
  return (
    <div>
      <GitBranch className="icon" />
    </div>
  );
}
```

**Impact**: 4 warnings eliminated, smaller bundle size

## Pattern 2: Dead Feature Infrastructure

**Context**: Edit mode feature removed but infrastructure remains

**Before** (BranchContextDialog.tsx - partial):
```typescript
import { Save, X, Edit, Check } from "lucide-react"; // 9 unused icons

// Parsing functions
const parseKeyValueMarkdown = (md: string) => { /* ... */ };
const parseFeatureFlagsMarkdown = (md: string) => { /* ... */ };
const parseListMarkdown = (md: string) => { /* ... */ };

// Converter functions
const keyValueToMarkdown = (data: any) => { /* ... */ };
const featureFlagsToMarkdown = (data: any) => { /* ... */ };
const listToMarkdown = (data: any) => { /* ... */ };

function BranchContextDialog() {
  // 10 state variables for markdown content
  const [envMarkdown, setEnvMarkdown] = useState('');
  const [flagsMarkdown, setFlagsMarkdown] = useState('');
  const [goalsMarkdown, setGoalsMarkdown] = useState('');
  // ... 7 more

  // Edit mode removed but state remains
}
```

**Detection**: 22 warnings total
- 9 icon imports
- 3 parsing functions
- 3 converter functions
- 10 state variables

**After**:
```typescript
import { GitBranch } from "lucide-react"; // Only what's needed

function BranchContextDialog() {
  // Clean component without edit mode infrastructure
}
```

**Approach**:
1. Identify unused state variables → 10 found
2. Find their setter calls → All removed with edit mode
3. Find functions only called by setters → 6 parsing/converter functions
4. Remove entire feature subsystem → 22 items cleaned

**Impact**: 22 warnings eliminated, revealed entire dead feature

## Pattern 3: React Query Error Callbacks - Unused Parameters

**Context**: Error callback destructures parameters but doesn't use all of them

**Before** (useSubtasks.ts):
```typescript
const createMutation = useMutation({
  mutationFn: createSubtask,
  onError: (err, { taskId }, context: any) => {
    logger.error('Failed to create subtask:', err);
    // taskId destructured but never used
    // Only context.taskId is used
  }
});
```

**Detection**:
```
error TS6133: 'taskId' is declared but its value is never read.
```

**After**:
```typescript
const createMutation = useMutation({
  mutationFn: createSubtask,
  onError: (err, _, context: any) => {
    logger.error('Failed to create subtask:', err);
    // Clean - follows convention for unused parameters
  }
});
```

**Files cleaned**:
- useSubtasks.ts (4 callbacks)
- useTasks.ts (2 callbacks)

**Impact**: 6 warnings eliminated, code follows conventions

## Pattern 4: Debug Snapshot Variables

**Context**: Cache snapshots captured for debugging but never used

**Before** (useRealtimeSync.ts):
```typescript
const handleTaskUpdate = (payload: TaskUpdatePayload) => {
  const beforeCache = queryClient.getQueryData(['tasks']);

  queryClient.setQueryData(['tasks'], (old: any) => {
    return updateTaskInCache(old, payload);
  });

  const afterCache = queryClient.getQueryData(['tasks']);
  // beforeCache and afterCache declared but never read
  // Likely left from debugging session
};
```

**Detection**: 12 instances across mutation handlers
```
error TS6133: 'beforeCache' is declared but its value is never read.
error TS6133: 'afterCache' is declared but its value is never read.
```

**After**:
```typescript
const handleTaskUpdate = (payload: TaskUpdatePayload) => {
  queryClient.setQueryData(['tasks'], (old: any) => {
    return updateTaskInCache(old, payload);
  });
  // Clean - no debug code
};
```

**Impact**: 12 warnings eliminated, improved runtime performance (no extra getQueryData calls)

**Archaeology**: Often paired with console.log statements (already removed)

## Pattern 5: Unused Component Props

**Context**: Prop defined in interface but never used in component

**Before** (TaskRow.tsx):
```typescript
interface TaskRowProps {
  task: Task;
  onDetailsDialogChange: (open: boolean) => void; // Unused
  onActiveDialogChange: (dialog: ActiveDialogState) => void;
}

function TaskRow({
  task,
  onDetailsDialogChange,  // Destructured but never used
  onActiveDialogChange
}: TaskRowProps) {
  // onDetailsDialogChange never called in component
  // Only onActiveDialogChange is used
}
```

**Detection**:
```
error TS6133: 'onDetailsDialogChange' is declared but its value is never read.
```

**After**:
```typescript
interface TaskRowProps {
  task: Task;
  onActiveDialogChange: (dialog: ActiveDialogState) => void;
}

function TaskRow({ task, onActiveDialogChange }: TaskRowProps) {
  // Clean interface - only what's needed
}
```

**Impact**: Clearer component API, interface reflects actual usage

## Pattern 6: Unused Arrow Function Parameters

**Context**: Arrow function parameter declared but not used in body

**Before** (LazyTaskList.tsx):
```typescript
<TaskRow
  task={task}
  onActiveDialogChange={(dialog) => {
    // 'dialog' parameter declared but never used
    setActiveDialog({ type: 'details', taskId: task.id });
  }}
/>
```

**Detection**:
```
error TS6133: 'dialog' is declared but its value is never read.
```

**After**:
```typescript
<TaskRow
  task={task}
  onActiveDialogChange={() => {
    // Clean - no unused parameters
    setActiveDialog({ type: 'details', taskId: task.id });
  }}
/>
```

**Impact**: Code clarity, follows conventions

## Pattern 7: Unused React Query Client

**Context**: useQueryClient hook called but queryClient never used

**Before** (TaskDetailsDialog.tsx):
```typescript
import { useQueryClient } from '@tanstack/react-query';

function TaskDetailsDialog({ taskId }: Props) {
  const queryClient = useQueryClient();
  // queryClient never used in component

  return (
    <div>
      {/* Component content */}
    </div>
  );
}
```

**Detection**:
```
error TS6133: 'queryClient' is declared but its value is never read.
```

**After**:
```typescript
// Remove import if no other usage
// import { useQueryClient } from '@tanstack/react-query';

function TaskDetailsDialog({ taskId }: Props) {
  // Clean - no unused hooks

  return (
    <div>
      {/* Component content */}
    </div>
  );
}
```

**Impact**: Prevents unnecessary hook call, cleaner component

## Pattern 8: Unused Validation Variables

**Context**: Variable assigned in validation block but never used

**Before** (useRealtimeSync.ts):
```typescript
if (!isValidPayload(data)) {
  const invalidData = data as any;  // Assigned but never used
  logger.warn('Invalid WebSocket payload received');
  return;
}
```

**Detection**:
```
error TS6133: 'invalidData' is declared but its value is never read.
```

**After**:
```typescript
if (!isValidPayload(data)) {
  logger.warn('Invalid WebSocket payload received');
  return;
}
```

**Impact**: Cleaner validation logic

## Pattern 9: Unused API Imports

**Context**: Multiple types/APIs imported but only some used

**Before** (api-lazy.ts):
```typescript
import { Project, Task, Subtask } from './api';
import { projectApiV2, taskApiV2, subtaskApiV2 } from './services/apiV2';

// Only Subtask, taskApiV2, subtaskApiV2 actually used
```

**Detection**:
```
error TS6133: 'Project' is declared but its value is never read.
error TS6133: 'Task' is declared but its value is never read.
error TS6133: 'projectApiV2' is declared but its value is never read.
```

**After**:
```typescript
import { Subtask } from './api';
import { taskApiV2, subtaskApiV2 } from './services/apiV2';
```

**Impact**: 4 warnings eliminated, smaller bundle

## Session Example: Complete Cleanup

**Project**: agenthub-frontend
**Date**: 2025-11-08
**Initial warnings**: 148
**Final warnings**: 101
**Reduction**: 32% (47 items removed)

**Workflow**:
```bash
# 1. Initial detection
npx tsc --noEmit --noUnusedLocals --noUnusedParameters 2>&1 | grep "error TS6133" | wc -l
# Output: 148

# 2. Find high-impact files
npx tsc --noEmit --noUnusedLocals --noUnusedParameters 2>&1 | grep "error TS6133" | \
  sed 's/([0-9]*,[0-9]*).*//' | sort | uniq -c | sort -rn | head -5
# Output:
#  22 agenthub-frontend/src/components/dialogs/BranchContextDialog.tsx
#  12 agenthub-frontend/src/hooks/useRealtimeSync.ts
#   6 agenthub-frontend/src/hooks/useTasks.ts
#   5 agenthub-frontend/src/components/LazySubtaskList.tsx
#   4 agenthub-frontend/src/services/api-lazy.ts

# 3. Clean files (highest impact first)
# Edit BranchContextDialog.tsx - remove 22 items
# Edit useRealtimeSync.ts - remove 12 items
# Edit useSubtasks.ts - remove 4 items
# Edit useTasks.ts - remove 2 items
# Edit api-lazy.ts - remove 4 items
# Edit LazySubtaskList/* - remove 5 items

# 4. Verify after cleanup
npm run build
# Success: 15.30s

# 5. Final count
npx tsc --noEmit --noUnusedLocals --noUnusedParameters 2>&1 | grep "error TS6133" | wc -l
# Output: 101

# 6. Progress
echo "Warnings: 148 → 101 (47 removed, 32% reduction)"
```

**Files Cleaned**:

| File | Warnings | Type | Items Removed |
|------|----------|------|---------------|
| BranchContextDialog.tsx | 22 | Dead feature | Icons, parsing functions, state, converters |
| useRealtimeSync.ts | 12 | Debug code | beforeCache, afterCache, invalidData |
| useSubtasks.ts | 4 | Unused params | onError destructuring |
| useTasks.ts | 2 | Unused params | onError destructuring |
| api-lazy.ts | 4 | Unused imports | Types and APIs |
| LazySubtaskList/* | 5 | Mixed | queryClient, props, parameters |
| **TOTAL** | **47** | - | **32% reduction** |

## Cascading Dependencies Example

**Scenario**: Remove edit mode from BranchContextDialog.tsx

**Step 1**: Identify unused state
```typescript
const [envMarkdown, setEnvMarkdown] = useState(''); // Unused
```

**Step 2**: Find setter calls
```bash
grep "setEnvMarkdown" BranchContextDialog.tsx
# Found in handleEditSave() - entire function removed with edit mode
```

**Step 3**: Find functions only called by removed code
```bash
grep "keyValueToMarkdown" BranchContextDialog.tsx
# Only called in handleEditSave() - can be removed
```

**Step 4**: Remove entire subsystem
- 10 state variables → 10 setters → 6 conversion/parsing functions → 9 icon imports

**Result**: 22 items removed by following dependency chain

## Performance Impact Example

**Scenario**: Remove debug snapshots from useRealtimeSync.ts

**Before**:
```typescript
const handleTaskUpdate = (payload: TaskUpdatePayload) => {
  const beforeCache = queryClient.getQueryData(['tasks']);  // Extra call
  queryClient.setQueryData(['tasks'], updater);
  const afterCache = queryClient.getQueryData(['tasks']);   // Extra call
};
```

**Impact per operation**:
- 2 unnecessary `getQueryData()` calls
- Cache serialization overhead
- Memory allocation for snapshots

**After**: Removed 12 such instances across mutation handlers

**Performance gain**:
- Eliminated 24 unnecessary cache reads per full operation cycle
- Reduced memory allocations
- Faster mutation handling

## Common Mistakes - Real Examples

### Mistake 1: Removing Used Destructured Variables

**❌ WRONG**:
```typescript
const { data, error } = useQuery();
// Error shows: 'error' is never read
// Developer removes 'error'
const { data } = useQuery();
// But error was checked later in conditional rendering!
```

**✅ RIGHT**:
```bash
# Search for all uses first
grep -n "error" ComponentFile.tsx
# Found: Line 45 uses error in conditional
# Don't remove - TypeScript was wrong (error used in JSX)
```

### Mistake 2: Missing Dynamic Calls

**❌ WRONG**:
```typescript
const validateEmail = (email: string) => { /* ... */ };
// Error shows: 'validateEmail' is never read
// Developer removes function
// But it's called dynamically:
const validators = {
  email: validateEmail  // Reference via object
};
```

**✅ RIGHT**:
```bash
# Search for function name as string
grep -r "validateEmail" src/
# Found in validators object - keep function
```

## Best Practices from Real Sessions

1. **Clean high-impact files first** - File with 22 warnings more valuable than 22 files with 1 warning each
2. **Verify build after each file** - Catch issues immediately
3. **Track progress** - Motivating to see 148 → 101
4. **Look for patterns** - Debug snapshots appeared in 12 locations (same pattern)
5. **Follow dependencies** - One unused state variable revealed 21 more items
6. **Check for dynamic usage** - String references, reflection, object properties
7. **Preserve API contracts** - Use `_` for unused required parameters

## Next Steps for This Project

**Remaining 101 warnings** distributed across:
- TaskDetailsDialog.tsx (11 warnings)
- useBranches.ts (6 warnings)
- useSubtasks.ts (5 warnings)
- SubtaskRow.tsx (5 warnings)
- TaskRow.tsx (4 warnings)
- 40+ files with 1-3 warnings each

**Strategy**: Same patterns apply - can be cleaned in future session or automated with ESLint rules
