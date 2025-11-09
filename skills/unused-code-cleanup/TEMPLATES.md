# Unused Code Cleanup Templates

Copy-paste templates for common unused code cleanup operations. Replace [PLACEHOLDERS] with actual values.

## Detection Commands

### Basic Detection
```bash
npx tsc --noEmit --noUnusedLocals --noUnusedParameters 2>&1 | grep "error TS6133"
```

### Count Total Warnings
```bash
npx tsc --noEmit --noUnusedLocals --noUnusedParameters 2>&1 | grep "error TS6133" | wc -l
```

### Find High-Impact Files
```bash
npx tsc --noEmit --noUnusedLocals --noUnusedParameters 2>&1 | grep "error TS6133" | \
  sed 's/([0-9]*,[0-9]*).*//' | sort | uniq -c | sort -rn | head -15
```

### Detect in Specific Directory
```bash
npx tsc --noEmit --noUnusedLocals --noUnusedParameters --project [DIRECTORY]/tsconfig.json 2>&1 | grep "error TS6133"
```
**Example**:
```bash
npx tsc --noEmit --noUnusedLocals --noUnusedParameters --project src/components/tsconfig.json 2>&1 | grep "error TS6133"
```

## Pattern 1: Unused Icon Imports

### Before Template
```typescript
import { [ICON1], [ICON2], [ICON3], [USED_ICON] } from "lucide-react";

function [COMPONENT_NAME]() {
  return (
    <div>
      <[USED_ICON] className="icon" />
    </div>
  );
}
```

### After Template
```typescript
import { [USED_ICON] } from "lucide-react";

function [COMPONENT_NAME]() {
  return (
    <div>
      <[USED_ICON] className="icon" />
    </div>
  );
}
```

### Search Command
```bash
# Find which icons are actually used
grep -o "<[A-Z][a-zA-Z]*" [FILE].tsx | sort | uniq
```

## Pattern 2: React Query Error Callbacks

### Before Template
```typescript
const [MUTATION_NAME] = useMutation({
  mutationFn: [MUTATION_FN],
  onError: (err, { [UNUSED_PARAM] }, context: any) => {
    logger.error('[ERROR_MESSAGE]:', err);
    // [UNUSED_PARAM] never used
  }
});
```

### After Template
```typescript
const [MUTATION_NAME] = useMutation({
  mutationFn: [MUTATION_FN],
  onError: (err, _, context: any) => {
    logger.error('[ERROR_MESSAGE]:', err);
  }
});
```

**Shortcut**: Replace destructured unused param with `_`

## Pattern 3: Debug Snapshot Variables

### Before Template
```typescript
const [HANDLER_NAME] = (payload: [PAYLOAD_TYPE]) => {
  const beforeCache = queryClient.getQueryData(['[KEY]']);

  queryClient.setQueryData(['[KEY]'], (old: any) => {
    return [UPDATE_FUNCTION](old, payload);
  });

  const afterCache = queryClient.getQueryData(['[KEY]']);
};
```

### After Template
```typescript
const [HANDLER_NAME] = (payload: [PAYLOAD_TYPE]) => {
  queryClient.setQueryData(['[KEY]'], (old: any) => {
    return [UPDATE_FUNCTION](old, payload);
  });
};
```

**Shortcut**: Delete lines with `beforeCache` and `afterCache`

## Pattern 4: Unused Component Props

### Before Template
```typescript
interface [COMPONENT_NAME]Props {
  [PROP1]: [TYPE1];
  [UNUSED_PROP]: [TYPE2];  // Remove this
  [PROP2]: [TYPE3];
}

function [COMPONENT_NAME]({
  [PROP1],
  [UNUSED_PROP],  // Remove this
  [PROP2]
}: [COMPONENT_NAME]Props) {
  // [UNUSED_PROP] never used
}
```

### After Template
```typescript
interface [COMPONENT_NAME]Props {
  [PROP1]: [TYPE1];
  [PROP2]: [TYPE3];
}

function [COMPONENT_NAME]({ [PROP1], [PROP2] }: [COMPONENT_NAME]Props) {
  // Clean
}
```

**Search Command**:
```bash
# Verify prop is truly unused
grep "[UNUSED_PROP]" [FILE].tsx
```

## Pattern 5: Unused Arrow Function Parameters

### Before Template
```typescript
<[COMPONENT]
  [PROP_NAME]={([UNUSED_PARAM]) => {
    [FUNCTION_BODY]
  }}
/>
```

### After Template
```typescript
<[COMPONENT]
  [PROP_NAME]={() => {
    [FUNCTION_BODY]
  }}
/>
```

**Shortcut**: Remove parameter from arrow function if not used in body

## Pattern 6: Unused Hook Call

### Before Template
```typescript
import { [HOOK_NAME] } from '[HOOK_PACKAGE]';

function [COMPONENT_NAME]() {
  const [HOOK_RETURN] = [HOOK_NAME]();
  // [HOOK_RETURN] never used

  return (
    <div>[CONTENT]</div>
  );
}
```

### After Template
```typescript
// Remove import if no other usage in file
// import { [HOOK_NAME] } from '[HOOK_PACKAGE]';

function [COMPONENT_NAME]() {
  // Removed unused hook call

  return (
    <div>[CONTENT]</div>
  );
}
```

**Search Command**:
```bash
# Check if import is used elsewhere
grep "[HOOK_NAME]" [FILE].tsx | wc -l
# If count is 1, safe to remove import
```

## Pattern 7: Unused Validation Variables

### Before Template
```typescript
if (![VALIDATION_FUNCTION](data)) {
  const [UNUSED_VAR] = data as any;
  logger.warn('[WARNING_MESSAGE]');
  return;
}
```

### After Template
```typescript
if (![VALIDATION_FUNCTION](data)) {
  logger.warn('[WARNING_MESSAGE]');
  return;
}
```

## Pattern 8: Unused API Imports

### Before Template
```typescript
import { [TYPE1], [UNUSED_TYPE], [TYPE2] } from './[API_FILE]';
import { [API1], [UNUSED_API], [API2] } from './services/[API_SERVICE]';
```

### After Template
```typescript
import { [TYPE1], [TYPE2] } from './[API_FILE]';
import { [API1], [API2] } from './services/[API_SERVICE]';
```

**Search Command**:
```bash
# Verify each import is used
grep "[UNUSED_TYPE]" [FILE].tsx
grep "[UNUSED_API]" [FILE].tsx
```

## Cleanup Workflow Templates

### Single File Cleanup
```bash
# 1. Detect warnings in file
npx tsc --noEmit --noUnusedLocals --noUnusedParameters 2>&1 | grep "[FILENAME]"

# 2. Edit file to remove unused items
# [PERFORM EDITS]

# 3. Verify warnings gone
npx tsc --noEmit --noUnusedLocals --noUnusedParameters 2>&1 | grep "[FILENAME]"
# Should: No output

# 4. Verify build works
npm run build

# 5. Verify tests pass
npm test
```

### High-Impact File Workflow
```bash
# 1. Find top 10 files with most warnings
npx tsc --noEmit --noUnusedLocals --noUnusedParameters 2>&1 | grep "error TS6133" | \
  sed 's/([0-9]*,[0-9]*).*//' | sort | uniq -c | sort -rn | head -10

# 2. Start with highest (most warnings)
# Example output: "22 src/components/ComponentName.tsx"

# 3. Get specific warnings for that file
npx tsc --noEmit --noUnusedLocals --noUnusedParameters 2>&1 | grep "ComponentName.tsx"

# 4. Clean file
# [PERFORM EDITS]

# 5. Verify count decreased
npx tsc --noEmit --noUnusedLocals --noUnusedParameters 2>&1 | grep "error TS6133" | wc -l

# 6. Repeat for next highest
```

### Progressive Cleanup Workflow
```bash
# 1. Baseline count
INITIAL=$(npx tsc --noEmit --noUnusedLocals --noUnusedParameters 2>&1 | grep "error TS6133" | wc -l)
echo "Initial warnings: $INITIAL"

# 2. Clean [N] files
# [PERFORM EDITS]

# 3. Check progress
CURRENT=$(npx tsc --noEmit --noUnusedLocals --noUnusedParameters 2>&1 | grep "error TS6133" | wc -l)
REMOVED=$((INITIAL - CURRENT))
PERCENT=$((REMOVED * 100 / INITIAL))
echo "Progress: $INITIAL → $CURRENT ($REMOVED removed, $PERCENT% reduction)"

# 4. Verify build
npm run build
```

### Batch Import Cleanup
```bash
# For files with only unused import warnings

# 1. Find files with only import warnings
npx tsc --noEmit --noUnusedLocals --noUnusedParameters 2>&1 | grep "error TS6133" | grep "import"

# 2. For each file, clean imports
# [EDIT FILE - REMOVE UNUSED IMPORTS]

# 3. Quick verification
npm run build
```

## Verification Templates

### Pre-Cleanup Checklist
```bash
# Count current warnings
npx tsc --noEmit --noUnusedLocals --noUnusedParameters 2>&1 | grep "error TS6133" | wc -l

# Identify high-impact files
npx tsc --noEmit --noUnusedLocals --noUnusedParameters 2>&1 | grep "error TS6133" | \
  sed 's/([0-9]*,[0-9]*).*//' | sort | uniq -c | sort -rn | head -5

# Ensure build works before changes
npm run build
```

### Post-Cleanup Checklist
```bash
# Verify TypeScript compiles
npx tsc --noEmit

# Count remaining warnings
npx tsc --noEmit --noUnusedLocals --noUnusedParameters 2>&1 | grep "error TS6133" | wc -l

# Verify build works
npm run build

# Verify tests pass
npm test

# Check bundle size (should be smaller)
npm run build && du -sh dist/
```

## Search Templates

### Find Usage of Variable
```bash
grep -n "[VARIABLE_NAME]" [FILE].tsx
```

### Find All Imports of Package
```bash
grep -r "from '[PACKAGE_NAME]'" [DIRECTORY]/
```

### Find Function Calls
```bash
grep -n "[FUNCTION_NAME](" [FILE].tsx
```

### Find Component Usage
```bash
grep -r "<[COMPONENT_NAME]" [DIRECTORY]/
```

### Find Prop Usage
```bash
grep -n "[PROP_NAME]" [FILE].tsx | grep -v "interface\|type\|:"
```

## ESLint Configuration Template

### Add to .eslintrc.json
```json
{
  "rules": {
    "@typescript-eslint/no-unused-vars": ["error", {
      "argsIgnorePattern": "^_",
      "varsIgnorePattern": "^_",
      "caughtErrorsIgnorePattern": "^_"
    }]
  }
}
```

### Run ESLint
```bash
npx eslint [DIRECTORY]/ --ext .ts,.tsx
```

## Git Workflow Template

### Before Cleanup Commit
```bash
# Create cleanup branch
git checkout -b cleanup/unused-code-[DATE]

# Baseline count
npx tsc --noEmit --noUnusedLocals --noUnusedParameters 2>&1 | grep "error TS6133" | wc -l > baseline.txt

# Perform cleanup
# [EDIT FILES]

# Verify changes
npm run build && npm test

# Commit
git add .
git commit -m "chore: remove unused code

- Removed [N] unused imports/variables/parameters
- Cleaned [FILE_LIST]
- Warnings: [BEFORE] → [AFTER] ([PERCENT]% reduction)
- Build verified: [BUILD_TIME]s
- Tests passing: [TEST_COUNT]/[TEST_COUNT]
"

# Cleanup baseline file
rm baseline.txt
```

## Quick Fill Guide

| Placeholder | What to Fill | Example |
|-------------|--------------|---------|
| `[COMPONENT_NAME]` | React component name | `TaskRow`, `BranchDialog` |
| `[FILE]` | Filename without extension | `BranchContextDialog` |
| `[DIRECTORY]` | Path to directory | `src/components` |
| `[ICON1]` | Icon import name | `Save`, `Edit`, `X` |
| `[MUTATION_NAME]` | Mutation variable | `createMutation`, `updateMutation` |
| `[UNUSED_PARAM]` | Parameter name to remove | `taskId`, `dialog` |
| `[PROP_NAME]` | Component prop name | `onDetailsDialogChange` |
| `[HOOK_NAME]` | React hook name | `useQueryClient`, `useState` |
| `[TYPE1]` | TypeScript type | `Project`, `Task`, `Subtask` |
| `[API_FILE]` | API file name | `api`, `types`, `interfaces` |
| `[VALIDATION_FUNCTION]` | Validation function | `isValidPayload`, `isValidTask` |
| `[N]` | Number/count | `22`, `12`, `148` |
| `[BEFORE]` `[AFTER]` | Warning counts | `148 → 101` |
| `[PERCENT]` | Percentage | `32`, `55.7` |

## Command Shortcuts

### Frequently Used
```bash
# Quick count
alias tsc-unused='npx tsc --noEmit --noUnusedLocals --noUnusedParameters 2>&1 | grep "error TS6133" | wc -l'

# Quick list
alias tsc-list='npx tsc --noEmit --noUnusedLocals --noUnusedParameters 2>&1 | grep "error TS6133"'

# High-impact files
alias tsc-impact='npx tsc --noEmit --noUnusedLocals --noUnusedParameters 2>&1 | grep "error TS6133" | sed "s/([0-9]*,[0-9]*).*//" | sort | uniq -c | sort -rn | head -10'

# Usage:
tsc-unused  # Get count
tsc-impact  # Find files to clean first
```

## Progress Tracking Template

```bash
#!/bin/bash
# track_cleanup_progress.sh

echo "=== Unused Code Cleanup Progress ==="
echo "Date: $(date +%Y-%m-%d)"

CURRENT=$(npx tsc --noEmit --noUnusedLocals --noUnusedParameters 2>&1 | grep "error TS6133" | wc -l)

if [ -f .cleanup_baseline ]; then
  BASELINE=$(cat .cleanup_baseline)
  REMOVED=$((BASELINE - CURRENT))
  PERCENT=$((REMOVED * 100 / BASELINE))
  echo "Baseline: $BASELINE"
  echo "Current: $CURRENT"
  echo "Removed: $REMOVED ($PERCENT%)"
else
  echo "Current: $CURRENT"
  echo $CURRENT > .cleanup_baseline
  echo "Baseline saved"
fi

echo ""
echo "Top 5 files:"
npx tsc --noEmit --noUnusedLocals --noUnusedParameters 2>&1 | grep "error TS6133" | \
  sed 's/([0-9]*,[0-9]*).*//' | sort | uniq -c | sort -rn | head -5
```
