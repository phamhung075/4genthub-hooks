# Unused Code Cleanup Validation

Quality checks for unused code cleanup.

## Quick Checklists

### Before Cleanup
- [ ] Baseline count recorded
- [ ] `npm run build` succeeds
- [ ] `npm test` passes
- [ ] High-impact files identified

### During (Per File)
- [ ] Usage verified: `grep -n "[NAME]" [FILE]`
- [ ] No dynamic refs: `grep '"[NAME]"'`
- [ ] Edit performed
- [ ] `npm run build` succeeds
- [ ] Warning count decreased

### After Cleanup
- [ ] `npx tsc --noEmit` succeeds
- [ ] `npm run build` succeeds
- [ ] `npm test` passes
- [ ] Bundle size ≤ baseline
- [ ] Progress documented

## Validation Commands

| Check | Command |
|-------|---------|
| **Baseline** | `npx tsc --noEmit --noUnusedLocals --noUnusedParameters 2>&1 \| grep "error TS6133" \| wc -l` |
| **TypeScript** | `npx tsc --noEmit` |
| **Build** | `npm run build` |
| **Tests** | `npm test` |
| **Bundle size** | `du -sh dist/` |
| **High-impact** | `... \| sed 's/([0-9]*,[0-9]*).*//' \| sort \| uniq -c \| sort -rn` |

## Pre-Cleanup

### Baseline Metrics
```bash
# Count + save
BASELINE=$(npx tsc --noEmit --noUnusedLocals --noUnusedParameters 2>&1 | grep "error TS6133" | wc -l)
echo $BASELINE > .cleanup_baseline

# Distribution
... | sed 's/([0-9]*,[0-9]*).*//' | sort | uniq -c | sort -rn | head -10
```

### Build + Test Health
```bash
# Build
npm run build && time npm run build  # Record time

# Tests
npm test && npm test 2>&1 | grep -E "passed|failed"  # Record count
```

### Bundle Baseline
```bash
npm run build && du -sh dist/ > .bundle_baseline
```

## During Cleanup

### Verify Before Removal

| Type | Command |
|------|---------|
| **Variable** | `grep -n "[VAR]" [FILE].tsx` (count = 1 → safe) |
| **Function** | `grep -r "[FUNC]" [DIR]/` + `grep -r '"[FUNC]"'` |
| **Import** | `grep "[IMPORT]" [FILE].tsx \| grep -v "^import"` |

### After Each File

```bash
# TypeScript check
npx tsc --noEmit

# Build
npm run build

# Count
npx tsc --noEmit --noUnusedLocals --noUnusedParameters 2>&1 | grep "error TS6133" | wc -l
```

### Progress Tracking
```bash
CURRENT=$(... | wc -l)
BASELINE=$(cat .cleanup_baseline)
echo "Progress: $BASELINE → $CURRENT ($((BASELINE - CURRENT)) removed, $((((BASELINE - CURRENT) * 100 / BASELINE)))%)"
```

## Post-Cleanup

### Final Verification
```bash
# TypeScript
npx tsc --noEmit && echo $?  # Should be 0

# Build + time
time npm run build

# Tests
npm test

# Bundle size
du -sh dist/
cat .bundle_baseline  # Compare
```

### Metrics Collection
```bash
FINAL=$(npx tsc --noEmit --noUnusedLocals --noUnusedParameters 2>&1 | grep "error TS6133" | wc -l)
BASELINE=$(cat .cleanup_baseline)
REMOVED=$((BASELINE - FINAL))
PERCENT=$((REMOVED * 100 / BASELINE))

echo "=== Results ==="
echo "Baseline: $BASELINE"
echo "Final: $FINAL"
echo "Removed: $REMOVED"
echo "Reduction: $PERCENT%"
```

## Quality Checks by Pattern

| Pattern | Required Checks |
|---------|-----------------|
| **Imports** | Remove from import → Build succeeds → File size decreased |
| **Parameters** | Replace with `_` if required → TypeScript validates signature |
| **Variables** | No references: `grep -n "[VAR]" [FILE]` → Build succeeds |
| **Hooks** | Remove call + import if no other usage → Component functions correctly |

## Common Pitfalls

| Pitfall | Detection | Prevention |
|---------|-----------|------------|
| **Used in JSX** | `grep "<.*{.*[VAR]"` finds usage | Check before removal |
| **Dynamic string ref** | `grep '"[FUNC]"'` finds string | Search string usage |
| **Template literal** | ``grep '\`.*${[VAR]}'`` finds usage | Check templates |
| **API signature** | `npx tsc --noEmit` errors | Verify signature matches |

## Validation Script

```bash
#!/bin/bash
# validate_cleanup.sh

echo "=== Validation ==="

# TypeScript
npx tsc --noEmit > /dev/null 2>&1 && echo "✓ TypeScript" || (echo "✗ TypeScript" && exit 1)

# Build
npm run build > /dev/null 2>&1 && echo "✓ Build" || (echo "✗ Build" && exit 1)

# Tests
npm test > /dev/null 2>&1 && echo "✓ Tests" || (echo "✗ Tests" && exit 1)

# Count
CURRENT=$(npx tsc --noEmit --noUnusedLocals --noUnusedParameters 2>&1 | grep "error TS6133" | wc -l)
echo "Warnings: $CURRENT"

if [ -f .cleanup_baseline ]; then
  BASELINE=$(cat .cleanup_baseline)
  echo "Progress: $BASELINE → $CURRENT ($((BASELINE - CURRENT)) removed, $((((BASELINE - CURRENT) * 100 / BASELINE)))%)"
fi

echo "✓ Complete"
```

## Smoke Tests

```bash
# Dev server
npm run dev &
sleep 5
curl -s http://localhost:3000 > /dev/null && echo "✓ Dev server" || echo "✗ Dev server"
kill %1
```

## Best Practices

- [ ] Cleaned high-impact first (files with 10+ warnings)
- [ ] Verified after each file (build + tests)
- [ ] Tracked progress (baseline → current)
- [ ] Looked for patterns (similar warnings handled similarly)
- [ ] Followed dependencies (unused state → unused functions)
- [ ] Preserved contracts (used `_` for required unused params)

## Quick Reference

| Check | Command |
|-------|---------|
| **Count** | `... \| grep "error TS6133" \| wc -l` |
| **TypeScript** | `npx tsc --noEmit` |
| **Build** | `npm run build` |
| **Tests** | `npm test` |
| **Bundle** | `du -sh dist/` |
| **Progress** | `echo "$BASELINE → $CURRENT ($REMOVED, $PERCENT%)"` |
| **Usage** | `grep -rn "[NAME]" src/` |
