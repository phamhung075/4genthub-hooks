# Unused Code Cleanup Templates

Copy-paste templates. Replace `[PLACEHOLDERS]`.

## Detection

| Task | Template |
|------|----------|
| **Basic detection** | `npx tsc --noEmit --noUnusedLocals --noUnusedParameters 2>&1 \| grep "error TS6133"` |
| **Count** | `... \| wc -l` |
| **High-impact files** | `... \| sed 's/([0-9]*,[0-9]*).*//' \| sort \| uniq -c \| sort -rn \| head -15` |
| **Specific directory** | `npx tsc --project [DIR]/tsconfig.json ... \| grep "error TS6133"` |

## Pattern Templates

### 1. Unused Imports
```typescript
// Before
import { [ICON1], [ICON2], [USED_ICON] } from "lucide-react";

// After
import { [USED_ICON] } from "lucide-react";
```

**Find used**: `grep -o "<[A-Z][a-zA-Z]*" [FILE].tsx | sort | uniq`

### 2. React Query Error Callbacks
```typescript
// Before
onError: (err, { [UNUSED_PARAM] }, context: any) => {
  logger.error('[MSG]:', err);
}

// After
onError: (err, _, context: any) => {
  logger.error('[MSG]:', err);
}
```

### 3. Debug Snapshots
```typescript
// Before
const beforeCache = queryClient.getQueryData(['[KEY]']);
queryClient.setQueryData(['[KEY]'], updater);
const afterCache = queryClient.getQueryData(['[KEY]']);

// After
queryClient.setQueryData(['[KEY]'], updater);
```

### 4. Unused Props
```typescript
// Before
interface [NAME]Props {
  [PROP1]: [TYPE1];
  [UNUSED_PROP]: [TYPE2];  // Remove
  [PROP2]: [TYPE3];
}
function [NAME]({ [PROP1], [UNUSED_PROP], [PROP2] }: [NAME]Props) {}

// After
interface [NAME]Props {
  [PROP1]: [TYPE1];
  [PROP2]: [TYPE3];
}
function [NAME]({ [PROP1], [PROP2] }: [NAME]Props) {}
```

**Verify unused**: `grep "[UNUSED_PROP]" [FILE].tsx`

### 5. Unused Arrow Function Parameters
```typescript
// Before
<[COMPONENT] [PROP]={([UNUSED_PARAM]) => { [BODY] }} />

// After
<[COMPONENT] [PROP]={() => { [BODY] }} />
```

### 6. Unused Hook
```typescript
// Before
const [HOOK_RETURN] = [HOOK_NAME]();

// After
// Remove line (and import if no other usage)
```

### 7. Unused Validation Variable
```typescript
// Before
if (![VALIDATION_FN](data)) {
  const [UNUSED_VAR] = data as any;
  logger.warn('[MSG]');
  return;
}

// After
if (![VALIDATION_FN](data)) {
  logger.warn('[MSG]');
  return;
}
```

### 8-9. Quick Fixes

| Pattern | Action |
|---------|--------|
| **Unused imports** | Remove from import statement |
| **Unused variable** | Delete declaration line |
| **Unused hook** | Remove call + import if unused |

## Workflows

### Single File Cleanup
```bash
# 1. Detect in file
npx tsc --noEmit --noUnusedLocals --noUnusedParameters 2>&1 | grep "[FILENAME]"

# 2. Edit file
# [PERFORM EDITS]

# 3. Verify
npx tsc --noEmit --noUnusedLocals --noUnusedParameters 2>&1 | grep "[FILENAME]"  # No output

# 4. Build
npm run build && npm test
```

### High-Impact Workflow
```bash
# 1. Find top 10
npx tsc --noEmit --noUnusedLocals --noUnusedParameters 2>&1 | grep "error TS6133" | \
  sed 's/([0-9]*,[0-9]*).*//' | sort | uniq -c | sort -rn | head -10

# 2. Clean highest first
# [EDIT FILES]

# 3. Progress
npx tsc --noEmit --noUnusedLocals --noUnusedParameters 2>&1 | grep "error TS6133" | wc -l
```

### Progressive Cleanup
```bash
# 1. Baseline
INITIAL=$(npx tsc --noEmit --noUnusedLocals --noUnusedParameters 2>&1 | grep "error TS6133" | wc -l)

# 2. Clean files
# [PERFORM EDITS]

# 3. Progress
CURRENT=$(npx tsc --noEmit --noUnusedLocals --noUnusedParameters 2>&1 | grep "error TS6133" | wc -l)
echo "Progress: $INITIAL → $CURRENT ($((INITIAL - CURRENT)) removed, $((((INITIAL - CURRENT) * 100 / INITIAL)))%)"

# 4. Verify
npm run build
```

## Verification

### Before Cleanup
```bash
# Count
npx tsc --noEmit --noUnusedLocals --noUnusedParameters 2>&1 | grep "error TS6133" | wc -l

# High-impact
... | sed 's/([0-9]*,[0-9]*).*//' | sort | uniq -c | sort -rn | head -5

# Build
npm run build
```

### After Cleanup
```bash
# TypeScript
npx tsc --noEmit

# Count remaining
npx tsc --noEmit --noUnusedLocals --noUnusedParameters 2>&1 | grep "error TS6133" | wc -l

# Build
npm run build && npm test

# Bundle size
npm run build && du -sh dist/
```

## Search Commands

| Task | Command |
|------|---------|
| **Find usage** | `grep -n "[VAR_NAME]" [FILE].tsx` |
| **Find imports** | `grep -r "from '[PACKAGE]'" [DIR]/` |
| **Find calls** | `grep -n "[FUNCTION](" [FILE].tsx` |
| **Find component** | `grep -r "<[COMPONENT]" [DIR]/` |
| **Find prop** | `grep -n "[PROP]" [FILE].tsx \| grep -v "interface\|type\|:"` |

## Git Workflow

```bash
# Branch
git checkout -b cleanup/unused-code-[DATE]

# Baseline
npx tsc --noEmit --noUnusedLocals --noUnusedParameters 2>&1 | grep "error TS6133" | wc -l > baseline.txt

# Clean
# [EDIT FILES]

# Verify
npm run build && npm test

# Commit
git add .
git commit -m "chore: remove unused code

- Removed [N] unused imports/variables/parameters
- Cleaned [FILE_LIST]
- Warnings: [BEFORE] → [AFTER] ([PERCENT]%)
- Build time: [TIME]s
- Tests: [COUNT]/[COUNT] passing
"
```

## Quick Reference

| Placeholder | Example |
|-------------|---------|
| `[COMPONENT_NAME]` | `TaskRow`, `BranchDialog` |
| `[FILE]` | `BranchContextDialog` |
| `[DIR]` | `src/components` |
| `[ICON1]` | `Save`, `Edit`, `X` |
| `[UNUSED_PARAM]` | `taskId`, `dialog` |
| `[PROP_NAME]` | `onDetailsDialogChange` |
| `[HOOK_NAME]` | `useQueryClient`, `useState` |
| `[VAR_NAME]` | `invalidData`, `beforeCache` |
| `[N]` | `22`, `12`, `148` |
| `[BEFORE]` `[AFTER]` | `148 → 101` |
| `[PERCENT]` | `32`, `55.7` |

## Shortcuts

```bash
# Aliases
alias tsc-unused='npx tsc --noEmit --noUnusedLocals --noUnusedParameters 2>&1 | grep "error TS6133" | wc -l'
alias tsc-list='npx tsc --noEmit --noUnusedLocals --noUnusedParameters 2>&1 | grep "error TS6133"'
alias tsc-impact='npx tsc --noEmit --noUnusedLocals --noUnusedParameters 2>&1 | grep "error TS6133" | sed "s/([0-9]*,[0-9]*).*//" | sort | uniq -c | sort -rn | head -10'

# Usage
tsc-unused    # Count
tsc-impact    # High-impact files
```

## Progress Tracking

```bash
#!/bin/bash
# track_progress.sh

CURRENT=$(npx tsc --noEmit --noUnusedLocals --noUnusedParameters 2>&1 | grep "error TS6133" | wc -l)

if [ -f .cleanup_baseline ]; then
  BASELINE=$(cat .cleanup_baseline)
  REMOVED=$((BASELINE - CURRENT))
  PERCENT=$((REMOVED * 100 / BASELINE))
  echo "Baseline: $BASELINE | Current: $CURRENT | Removed: $REMOVED ($PERCENT%)"
else
  echo "Current: $CURRENT"
  echo $CURRENT > .cleanup_baseline
fi
```
