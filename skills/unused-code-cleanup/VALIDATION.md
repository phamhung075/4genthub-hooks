# Unused Code Cleanup Validation

Quality checks and validation rules for unused code cleanup operations.

## Quick Checklist

### Before Cleanup
- [ ] **Baseline count**: Record initial warning count
- [ ] **Build works**: `npm run build` succeeds
- [ ] **Tests pass**: `npm test` succeeds
- [ ] **High-impact identified**: Know which files to clean first
- [ ] **Git branch**: Created cleanup branch

### During Cleanup (Per File)
- [ ] **Search usage**: Verified item truly unused
- [ ] **Check dynamic refs**: No string references or reflection
- [ ] **Edit carefully**: Only remove confirmed unused items
- [ ] **Build after**: `npm run build` succeeds
- [ ] **Progress tracked**: Warning count decreased

### After Cleanup
- [ ] **TypeScript compiles**: `npx tsc --noEmit` succeeds
- [ ] **Build works**: `npm run build` succeeds
- [ ] **Tests pass**: `npm test` succeeds
- [ ] **Bundle smaller**: Check `dist/` size decreased
- [ ] **Progress documented**: Track warnings removed
- [ ] **Commit clean**: Clear commit message with metrics

## Pre-Cleanup Validation

### Baseline Metrics
```bash
# Count total warnings
BASELINE=$(npx tsc --noEmit --noUnusedLocals --noUnusedParameters 2>&1 | grep "error TS6133" | wc -l)
echo "Baseline warnings: $BASELINE"

# Save for later comparison
echo $BASELINE > .cleanup_baseline

# Identify distribution
npx tsc --noEmit --noUnusedLocals --noUnusedParameters 2>&1 | grep "error TS6133" | \
  sed 's/([0-9]*,[0-9]*).*//' | sort | uniq -c | sort -rn | head -10
```

**Expected**: Clear count and list of high-impact files

### Build Health Check
```bash
# Ensure build works before any changes
npm run build

# Record build time
time npm run build
```

**Expected**: Build succeeds, time recorded for comparison

### Test Health Check
```bash
# Ensure tests pass before changes
npm test

# Count passing tests
npm test 2>&1 | grep -E "passed|failed"
```

**Expected**: All tests pass

### Bundle Size Baseline
```bash
# Record initial bundle size
npm run build
du -sh dist/ > .bundle_baseline
```

**Expected**: Baseline saved for comparison

## During Cleanup Validation

### Verify Usage Before Removal

#### For Variables
```bash
# Search all occurrences
grep -n "[VARIABLE_NAME]" [FILE].tsx

# If count is 1 (just declaration), safe to remove
```

**Expected**: Only the declaration line found

#### For Functions
```bash
# Search for function name
grep -r "[FUNCTION_NAME]" [DIRECTORY]/

# Check for string references
grep -r '"[FUNCTION_NAME]"' [DIRECTORY]/
grep -r "'[FUNCTION_NAME]'" [DIRECTORY]/
```

**Expected**: No usage found

#### For Imports
```bash
# Check if import is used
grep "[IMPORT_NAME]" [FILE].tsx | grep -v "^import"

# If no output, safe to remove from imports
```

**Expected**: No usage outside import statement

### After Each File Edit

#### TypeScript Check
```bash
# Verify no TypeScript errors introduced
npx tsc --noEmit

# If errors appear, undo changes
```

**Expected**: No errors

#### Build Check
```bash
# Ensure build still works
npm run build
```

**Expected**: Build succeeds

#### Warning Count
```bash
# Check warnings decreased
npx tsc --noEmit --noUnusedLocals --noUnusedParameters 2>&1 | grep "error TS6133" | wc -l
```

**Expected**: Count is lower than before

### Progress Tracking

```bash
# After each file or session
CURRENT=$(npx tsc --noEmit --noUnusedLocals --noUnusedParameters 2>&1 | grep "error TS6133" | wc -l)
BASELINE=$(cat .cleanup_baseline)
REMOVED=$((BASELINE - CURRENT))
PERCENT=$((REMOVED * 100 / BASELINE))

echo "Progress: $BASELINE → $CURRENT ($REMOVED removed, $PERCENT%)"
```

**Expected**: Steady progress toward zero warnings

## Post-Cleanup Validation

### TypeScript Compilation
```bash
# Full TypeScript check
npx tsc --noEmit

# Should complete with no errors
echo $?  # Should output: 0
```

**Expected**: Exit code 0, no errors

### Build Verification
```bash
# Build with timing
time npm run build

# Compare with baseline
cat .build_time_baseline
```

**Expected**: Build succeeds, similar or faster time

### Test Verification
```bash
# Run full test suite
npm test

# Check all pass
npm test 2>&1 | grep -E "passed|failed"
```

**Expected**: Same number of tests pass as baseline

### Bundle Size Comparison
```bash
# Build and check size
npm run build
du -sh dist/

# Compare with baseline
cat .bundle_baseline
```

**Expected**: Bundle size same or smaller

### Warning Count Final Check
```bash
# Count remaining warnings
FINAL=$(npx tsc --noEmit --noUnusedLocals --noUnusedParameters 2>&1 | grep "error TS6133" | wc -l)
BASELINE=$(cat .cleanup_baseline)
REMOVED=$((BASELINE - FINAL))
PERCENT=$((REMOVED * 100 / BASELINE))

echo "=== Cleanup Results ==="
echo "Baseline: $BASELINE"
echo "Final: $FINAL"
echo "Removed: $REMOVED"
echo "Reduction: $PERCENT%"
```

**Expected**: Clear improvement metrics

## Quality Checks by Pattern

### For Import Removals
- [ ] Import removed from import statement
- [ ] No usage found in file: `grep "[IMPORT]" [FILE] | grep -v "^import"`
- [ ] Build succeeds
- [ ] File size decreased

### For Parameter Removals
- [ ] Parameter replaced with `_` if required by signature
- [ ] Or parameter removed entirely if optional
- [ ] Function signature still matches calling convention
- [ ] No TypeScript errors

### For Variable Removals
- [ ] Variable declaration removed
- [ ] No references found: `grep -n "[VAR_NAME]" [FILE]`
- [ ] Related setters/getters removed if applicable
- [ ] Build succeeds

### For Hook Removals
- [ ] Hook call removed
- [ ] Import removed if no other usage
- [ ] Component still functions correctly
- [ ] No runtime errors

## Common Pitfalls Detection

### Pitfall 1: Used in JSX
```bash
# Check if "unused" variable is in JSX
grep "<.*{.*[VARIABLE_NAME]" [FILE].tsx

# If found, DO NOT remove
```

**Expected**: If found, keep variable

### Pitfall 2: Dynamic String Reference
```bash
# Check for string references
grep '"[FUNCTION_NAME]"' [FILE].tsx
grep "'[FUNCTION_NAME]'" [FILE].tsx

# If found, DO NOT remove
```

**Expected**: No string references

### Pitfall 3: Used in Template Literal
```bash
# Check for template literal usage
grep '`.*${[VARIABLE_NAME]}' [FILE].tsx

# If found, DO NOT remove
```

**Expected**: No template literal usage

### Pitfall 4: Required by API Signature
```bash
# For callback parameters, check if signature matches API
# TypeScript will error if signature wrong after change

npx tsc --noEmit
```

**Expected**: No signature mismatch errors

## Validation Script

```bash
#!/bin/bash
# validate_cleanup.sh

echo "=== Unused Code Cleanup Validation ==="

# 1. TypeScript check
echo "1. Checking TypeScript compilation..."
if npx tsc --noEmit > /dev/null 2>&1; then
  echo "   ✓ TypeScript compiles"
else
  echo "   ✗ TypeScript errors found"
  exit 1
fi

# 2. Build check
echo "2. Checking build..."
if npm run build > /dev/null 2>&1; then
  echo "   ✓ Build succeeds"
else
  echo "   ✗ Build failed"
  exit 1
fi

# 3. Test check
echo "3. Running tests..."
if npm test > /dev/null 2>&1; then
  echo "   ✓ Tests pass"
else
  echo "   ✗ Tests failed"
  exit 1
fi

# 4. Warning count
echo "4. Checking warnings..."
CURRENT=$(npx tsc --noEmit --noUnusedLocals --noUnusedParameters 2>&1 | grep "error TS6133" | wc -l)
echo "   Current warnings: $CURRENT"

if [ -f .cleanup_baseline ]; then
  BASELINE=$(cat .cleanup_baseline)
  REMOVED=$((BASELINE - CURRENT))
  PERCENT=$((REMOVED * 100 / BASELINE))
  echo "   Progress: $BASELINE → $CURRENT ($REMOVED removed, $PERCENT%)"
fi

# 5. Bundle size
echo "5. Checking bundle size..."
BUNDLE_SIZE=$(du -sh dist/ | cut -f1)
echo "   Bundle size: $BUNDLE_SIZE"

if [ -f .bundle_baseline ]; then
  BASELINE_SIZE=$(cat .bundle_baseline | cut -f1)
  echo "   Baseline: $BASELINE_SIZE"
fi

echo ""
echo "=== Validation Complete ==="
```

## Regression Detection

### After Cleanup Smoke Tests
```bash
# 1. Start dev server
npm run dev &
DEV_PID=$!

# 2. Wait for startup
sleep 5

# 3. Check if server running
if curl -s http://localhost:3000 > /dev/null; then
  echo "✓ Dev server running"
else
  echo "✗ Dev server failed"
fi

# 4. Cleanup
kill $DEV_PID
```

### Runtime Error Check
```bash
# Check browser console logs during manual testing
# Look for:
# - "X is not defined" errors
# - "Cannot read property" errors
# - Component render errors
```

## Metrics Collection

### Session Metrics Template
```markdown
## Cleanup Session [DATE]

**Initial State**:
- Warnings: [BASELINE_COUNT]
- Build time: [BASELINE_TIME]s
- Bundle size: [BASELINE_SIZE]
- Tests: [BASELINE_TEST_COUNT]/[TOTAL] passing

**Files Cleaned**:
| File | Warnings | Items Removed | Type |
|------|----------|---------------|------|
| [FILE1] | [N1] | [ITEMS1] | [TYPE1] |
| [FILE2] | [N2] | [ITEMS2] | [TYPE2] |

**Final State**:
- Warnings: [FINAL_COUNT]
- Build time: [FINAL_TIME]s
- Bundle size: [FINAL_SIZE]
- Tests: [FINAL_TEST_COUNT]/[TOTAL] passing

**Results**:
- Warnings removed: [REMOVED] ([PERCENT]% reduction)
- Build time: [BEFORE] → [AFTER]
- Bundle size: [BEFORE] → [AFTER]
```

### Progress Tracking Log
```bash
# Create log entry
echo "$(date +%Y-%m-%d): $(npx tsc --noEmit --noUnusedLocals --noUnusedParameters 2>&1 | grep 'error TS6133' | wc -l) warnings" >> .cleanup_progress.log

# View progress over time
cat .cleanup_progress.log
```

## Best Practices Verification

- [ ] **Cleaned high-impact first** - Files with 10+ warnings prioritized
- [ ] **Verified after each file** - Build and tests checked per file
- [ ] **Tracked progress** - Baseline → current count tracked
- [ ] **Looked for patterns** - Similar warnings handled similarly
- [ ] **Followed dependencies** - Unused state → unused functions chain
- [ ] **Preserved contracts** - Used `_` for required unused params
- [ ] **Documented session** - Metrics and files cleaned recorded

## Automation Validation

### ESLint Configuration Check
```bash
# Verify ESLint is configured
cat .eslintrc.json | grep "no-unused-vars"

# Run ESLint
npx eslint src/ --ext .ts,.tsx 2>&1 | grep "no-unused-vars" | wc -l
```

**Expected**: ESLint catches unused code

### Pre-commit Hook Test
```bash
# Test pre-commit hook
git add .
git commit -m "test: verify pre-commit hook"

# Should show warning count if hook installed
```

**Expected**: Hook runs and shows warning count

## Final Checklist

Before marking cleanup complete:

1. **All validations pass** - TypeScript, build, tests
2. **Progress documented** - Metrics recorded
3. **Commit clean** - Clear message with numbers
4. **Baseline updated** - If continuing later
5. **No regressions** - Manual smoke test passed
6. **Bundle optimized** - Size same or smaller
7. **Code cleaner** - Only necessary code remains

## Cleanup Completion Criteria

| Criteria | Target | Status |
|----------|--------|--------|
| TypeScript compiles | ✓ No errors | [ ] |
| Build succeeds | ✓ Successful | [ ] |
| Tests pass | ✓ 100% passing | [ ] |
| Warnings reduced | ≥20% reduction | [ ] |
| Bundle size | ≤ baseline | [ ] |
| No regressions | ✓ Smoke test pass | [ ] |
| Documented | ✓ Metrics recorded | [ ] |

## Validation Commands Quick Reference

| Check | Command |
|-------|---------|
| **Count warnings** | `npx tsc --noEmit --noUnusedLocals --noUnusedParameters 2>&1 \| grep "error TS6133" \| wc -l` |
| **TypeScript check** | `npx tsc --noEmit` |
| **Build** | `npm run build` |
| **Tests** | `npm test` |
| **Bundle size** | `du -sh dist/` |
| **High-impact files** | `... \| sed 's/([0-9]*,[0-9]*).*//' \| sort \| uniq -c \| sort -rn` |
| **Progress** | `echo "$BASELINE → $CURRENT ($REMOVED removed, $PERCENT%)"` |
| **Search usage** | `grep -rn "[NAME]" src/` |
