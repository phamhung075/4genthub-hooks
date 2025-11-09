# Safe File Removal Validation

Quality checks and validation rules for safe file removal operations.

## Quick Checklist

### Before Removal
- [ ] **Search usage**: `grep -r "[NAME]" [DIRECTORY]` shows no results
- [ ] **Check imports**: No other files depend on this file
- [ ] **Verify obsolete**: File truly not needed anymore
- [ ] **Know location**: Can reverse with `mv [FILE].obsolete [FILE]`

### After Removal
- [ ] **Tests pass**: `npm test` succeeds
- [ ] **Build works**: `npm run build` succeeds
- [ ] **App runs**: `npm run dev` works correctly
- [ ] **No errors**: Browser console has no new errors
- [ ] **Listed**: `find . -name "*.obsolete"` shows removed files

### Before Permanent Deletion
- [ ] **Time passed**: Waited review period (1-7 days)
- [ ] **System stable**: No issues discovered
- [ ] **Confirmed unused**: Double-checked not needed
- [ ] **Listed files**: `find . -name "*.obsolete" -mtime +[DAYS]`

## Validation Commands

### Pre-Removal Checks

#### Check for Usage
```bash
# Search for file references
grep -r "[FILENAME_WITHOUT_EXT]" [DIRECTORY]

# Examples:
grep -r "OldComponent" src/
grep -r "helper_function" .
grep -r "unused_util" src/ tests/
```

**Expected**: No results = safe to remove

#### Check for Imports
```bash
# TypeScript/JavaScript
grep -r "from.*[FILENAME]" src/
grep -r "import.*[FILENAME]" src/

# Python
grep -r "from.*[MODULE_NAME]" .
grep -r "import [MODULE_NAME]" .
```

**Expected**: No import statements

#### Verify File Exists
```bash
ls -la [PATH_TO_FILE]
```

**Expected**: File exists before removal

### Post-Removal Verification

#### Verify File Renamed
```bash
# Check original is gone
ls -la [ORIGINAL_FILE]
# Should: cannot access: No such file

# Check .obsolete exists
ls -la [ORIGINAL_FILE].obsolete
# Should: show file details
```

#### Run Tests
```bash
# Frontend (React/TypeScript)
npm test

# Backend (Python)
pytest
python -m pytest

# Both
npm test && pytest
```

**Expected**: All tests pass

#### Run Build
```bash
# Frontend
npm run build

# TypeScript check
npx tsc --noEmit

# Both
npm run build && npx tsc --noEmit
```

**Expected**: Build succeeds, no errors

#### Start Development Server
```bash
# Frontend
npm run dev

# Backend
python main.py

# Full stack
npm run dev & python main.py
```

**Expected**: Server starts, no crashes

#### Check for Broken References
```bash
# Search for 404s or missing file errors
# After starting dev server, check browser console

# Or grep for potential issues
grep -r "[REMOVED_FILENAME]" [DIRECTORY]
```

**Expected**: No broken references

### Recovery Validation

#### Restore File
```bash
# Restore
mv [FILE].obsolete [FILE]

# Verify restored
ls -la [FILE]

# Test still works
npm test && npm run build
```

**Expected**: File restored, system works

#### Restore Multiple Files
```bash
# Find all obsolete
find . -name "*.obsolete" -type f

# Restore specific ones
mv [FILE1].obsolete [FILE1]
mv [FILE2].obsolete [FILE2]

# Verify all restored
ls -la [FILE1] [FILE2]
```

**Expected**: All files restored correctly

### Cleanup Validation

#### List Obsolete Files
```bash
# All obsolete files
find . -name "*.obsolete" -type f

# Count
find . -name "*.obsolete" -type f | wc -l

# With details
find . -name "*.obsolete" -type f -ls
```

**Expected**: Shows all .obsolete files

#### Find Old Obsolete Files
```bash
# Older than 7 days
find . -name "*.obsolete" -type f -mtime +7

# Older than 30 days
find . -name "*.obsolete" -type f -mtime +30
```

**Expected**: Shows candidates for permanent deletion

#### Disk Space Check
```bash
# Space used by obsolete files
du -sh $(find . -name "*.obsolete" -type f 2>/dev/null)

# Detailed breakdown
du -h $(find . -name "*.obsolete" -type f 2>/dev/null)
```

**Expected**: Understand space impact

## Safety Requirements

### Critical Files

**Never use rmmm on**:
| File/Directory | Reason | Alternative |
|----------------|--------|-------------|
| `.git/` | Lose entire history | Use git commands |
| `.env*` | Contains secrets | Secure deletion + git history rewrite |
| `node_modules/` | Safe to delete | Just `rm -rf node_modules` |
| `package.json` | Critical config | Version control instead |
| `database/` | Data loss | Backup + migration |

### Required Checks

| Scenario | Required Validation |
|----------|---------------------|
| **Removing component** | `grep -r "[COMPONENT_NAME]" src/` → No results |
| **Removing utility** | `grep -r "[UTIL_NAME]" .` → No imports |
| **Removing asset** | Check UI for broken images |
| **Removing test** | `npm test` → All pass |
| **Removing config** | App starts correctly |

## Quality Checklist by Type

### For Source Code
- [ ] Searched all source directories for usage
- [ ] Checked import statements
- [ ] Verified no dynamic imports/requires
- [ ] Tests pass after removal
- [ ] Build succeeds
- [ ] TypeScript check passes

### For Assets
- [ ] Checked for references in code
- [ ] Verified UI loads correctly
- [ ] No 404 errors in browser console
- [ ] No missing image placeholders
- [ ] CSS/styles still apply

### For Tests
- [ ] Remaining tests still pass
- [ ] Coverage hasn't dropped unexpectedly
- [ ] No test utilities removed that other tests use
- [ ] Test organization still makes sense

### For Documentation
- [ ] No broken links from other docs
- [ ] Navigation still works
- [ ] Documentation site builds
- [ ] README references updated

## Common Pitfalls

| Pitfall | Detection | Prevention |
|---------|-----------|------------|
| **File still imported** | `grep -r "import.*[FILE]"` finds results | Check before removal |
| **Dynamic reference** | `grep -r "[FILENAME]"` shows string refs | Search for string usage |
| **Test dependency** | Tests fail after removal | Run tests immediately |
| **Build breaks** | Build errors appear | Run build immediately |
| **Runtime error** | App crashes on specific feature | Manual testing |

## Validation Script Template

```bash
#!/bin/bash
# validate_removal.sh [FILE_TO_REMOVE]

FILE="$1"

if [ -z "$FILE" ]; then
  echo "Usage: $0 [FILE_TO_REMOVE]"
  exit 1
fi

echo "=== Pre-Removal Validation ==="

# Check file exists
if [ ! -e "$FILE" ]; then
  echo "✗ File not found: $FILE"
  exit 1
fi
echo "✓ File exists"

# Check for usage
FILENAME=$(basename "$FILE" | sed 's/\.[^.]*$//')
USAGE=$(grep -r "$FILENAME" src/ 2>/dev/null | wc -l)

if [ $USAGE -gt 1 ]; then
  echo "⚠ Warning: Found $USAGE potential references"
  grep -r "$FILENAME" src/ | head -10
  read -p "Continue anyway? (y/N) " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
  fi
else
  echo "✓ No usage found"
fi

# Remove file
echo ""
echo "=== Removing File ==="
./.claude/bin/rmmm "$FILE"

if [ $? -ne 0 ]; then
  echo "✗ Removal failed"
  exit 1
fi
echo "✓ File removed"

# Post-removal validation
echo ""
echo "=== Post-Removal Validation ==="

# Verify .obsolete exists
if [ ! -e "$FILE.obsolete" ]; then
  echo "✗ .obsolete file not found"
  exit 1
fi
echo "✓ .obsolete file exists"

# Run tests
echo ""
echo "Running tests..."
npm test > /dev/null 2>&1

if [ $? -ne 0 ]; then
  echo "✗ Tests failed - recovering file"
  mv "$FILE.obsolete" "$FILE"
  exit 1
fi
echo "✓ Tests pass"

# Run build
echo ""
echo "Running build..."
npm run build > /dev/null 2>&1

if [ $? -ne 0 ]; then
  echo "✗ Build failed - recovering file"
  mv "$FILE.obsolete" "$FILE"
  exit 1
fi
echo "✓ Build succeeds"

echo ""
echo "=== Validation Complete ==="
echo "✓ File safely removed: $FILE → $FILE.obsolete"
echo "⚠ Review and permanently delete later: /bin/rm $FILE.obsolete"
```

## Pre-Commit Final Check

Before permanent deletion:

1. **Time check** - Waited at least review period?
2. **Stability check** - No issues discovered?
3. **List files** - `find . -name "*.obsolete"`
4. **Age verification** - `find . -name "*.obsolete" -mtime +[DAYS]`
5. **Confirm delete** - Read list, confirm not needed
6. **Permanent delete** - `/bin/rm [FILE].obsolete`

## Recovery Testing

### Test Recovery Process
```bash
# 1. Remove test file
echo "test content" > test_file.txt
./.claude/bin/rmmm test_file.txt

# 2. Verify removed
ls test_file.txt 2>&1 | grep "No such file"

# 3. Verify .obsolete exists
ls test_file.txt.obsolete

# 4. Recover
mv test_file.txt.obsolete test_file.txt

# 5. Verify recovered
cat test_file.txt | grep "test content"

# 6. Cleanup
/bin/rm test_file.txt
```

**Expected**: Each step succeeds

### Test Collision Handling
```bash
# 1. Create and remove file
echo "v1" > test.txt
./.claude/bin/rmmm test.txt

# 2. Restore and modify
mv test.txt.obsolete test.txt
echo "v2" > test.txt

# 3. Remove again (collision)
./.claude/bin/rmmm test.txt

# 4. Verify timestamp version
ls -la test.txt.obsolete.*

# 5. Cleanup
/bin/rm test.txt.obsolete*
```

**Expected**: Timestamp fallback works

## Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| **Not found** | File doesn't exist | Check path, use `ls` to verify |
| **Permission denied** | No write access | Use `chmod` or run with sudo |
| **Already exists** | .obsolete file present | Handled by timestamp fallback |
| **Failed to rename** | System error | Check permissions, disk space |

## Monitoring Commands

### Track Obsolete Files Over Time
```bash
# Daily log
echo "$(date): $(find . -name '*.obsolete' | wc -l) obsolete files" >> .obsolete_log

# Weekly cleanup check
find . -name "*.obsolete" -type f -mtime +7 | wc -l
```

### Space Monitoring
```bash
# Before removal
du -sh [DIRECTORY]

# After removal
du -sh [DIRECTORY]
du -sh $(find . -name "*.obsolete" 2>/dev/null)

# Space saved
# Original - Current = Space potentially saved
```

## Best Practices Verification

- [ ] **Used rmmm** - Not `rm` directly
- [ ] **Searched first** - Checked for dependencies
- [ ] **Tested after** - Verified system works
- [ ] **Kept review period** - Waited before permanent delete
- [ ] **Listed periodically** - Reviewed obsolete files
- [ ] **Documented** - Noted what was removed and why

## Integration Check

### Pre-Tool Hook Integration
```bash
# Verify rm is blocked
rm test.txt 2>&1 | grep "BLOCKED"
# Should: Show block message

# Verify rmmm works
./.claude/bin/rmmm test.txt
# Should: Success message
```

**Expected**: Hook blocks rm, allows rmmm

### Settings Verification
```bash
# Check RM_BASH_BLOCK setting
grep "RM_BASH_BLOCK" .claude/settings.json
# Should: "RM_BASH_BLOCK": "true"
```

**Expected**: Setting enabled
