# Safe File Removal Templates

Copy-paste commands for common rmmm use cases. Replace [PLACEHOLDERS] with actual values.

## Basic Operations

### Single File Removal
```bash
./.claude/bin/rmmm [PATH_TO_FILE]
```
**Example**:
```bash
./.claude/bin/rmmm src/components/OldComponent.tsx
```

### Multiple Files Removal
```bash
./.claude/bin/rmmm [FILE1] [FILE2] [FILE3]
```
**Example**:
```bash
./.claude/bin/rmmm old_file.txt legacy.js unused.css
```

### Directory Removal
```bash
./.claude/bin/rmmm [PATH_TO_DIR]/
```
**Example**:
```bash
./.claude/bin/rmmm dist/ build/ .cache/
```

### Mixed (Files + Directories)
```bash
./.claude/bin/rmmm [FILE1] [DIR1]/ [FILE2] [DIR2]/
```
**Example**:
```bash
./.claude/bin/rmmm old_config.json deprecated/ unused_helper.js legacy_tests/
```

## Recovery Operations

### Restore Single File
```bash
mv [FILENAME].obsolete [FILENAME]
```
**Example**:
```bash
mv important.txt.obsolete important.txt
```

### Restore with Timestamp
```bash
mv [FILENAME].obsolete.[TIMESTAMP] [FILENAME]
```
**Example**:
```bash
mv config.json.obsolete.20251109_110500 config.json
```

### Restore Multiple Specific Files
```bash
mv [FILE1].obsolete [FILE1]
mv [FILE2].obsolete [FILE2]
mv [FILE3].obsolete [FILE3]
```
**Example**:
```bash
mv src/utils/helper.js.obsolete src/utils/helper.js
mv tests/unit.spec.ts.obsolete tests/unit.spec.ts
```

### Restore All Obsolete Files in Directory (CAUTION)
```bash
find [DIRECTORY] -name "*.obsolete" -type f | while read file; do
  mv "$file" "${file%.obsolete}"
done
```
**Example**:
```bash
find src/ -name "*.obsolete" -type f | while read file; do
  mv "$file" "${file%.obsolete}"
done
```

## Search & List Operations

### List All Obsolete Files
```bash
find . -name "*.obsolete" -type f
```

### List Obsolete Files in Specific Directory
```bash
find [DIRECTORY] -name "*.obsolete" -type f
```
**Example**:
```bash
find src/ -name "*.obsolete" -type f
```

### Count Obsolete Files
```bash
find . -name "*.obsolete" -type f | wc -l
```

### List with Details (size, date)
```bash
find . -name "*.obsolete" -type f -ls
```

### Disk Space Used by Obsolete Files
```bash
du -sh $(find . -name "*.obsolete" -type f)
```

### Find Recent Obsolete Files (last 7 days)
```bash
find . -name "*.obsolete" -type f -mtime -7
```

### Find Old Obsolete Files (older than 30 days)
```bash
find . -name "*.obsolete" -type f -mtime +30
```

## Batch Operations

### Remove All .log Files
```bash
find . -name "*.log" -type f -exec ./.claude/bin/rmmm {} \;
```

### Remove Empty Directories
```bash
find . -type d -empty -exec ./.claude/bin/rmmm {} \;
```

### Remove Files Older Than 30 Days
```bash
find [DIRECTORY] -type f -mtime +30 -exec ./.claude/bin/rmmm {} \;
```
**Example**:
```bash
find logs/ -type f -mtime +30 -exec ./.claude/bin/rmmm {} \;
```

### Remove Files Matching Pattern
```bash
find [DIRECTORY] -name "[PATTERN]" -type f -exec ./.claude/bin/rmmm {} \;
```
**Example**:
```bash
find temp/ -name "*.tmp" -type f -exec ./.claude/bin/rmmm {} \;
```

### Remove All Files in Directory
```bash
find [DIRECTORY] -type f -exec ./.claude/bin/rmmm {} \;
```
**Example**:
```bash
find old_build/ -type f -exec ./.claude/bin/rmmm {} \;
```

## Cleanup Operations

### Permanently Delete All Obsolete Files (CAUTION)
```bash
find . -name "*.obsolete" -exec /bin/rm -r {} \;
```

### Permanently Delete Obsolete Files Older Than 7 Days
```bash
find . -name "*.obsolete" -type f -mtime +7 -exec /bin/rm {} \;
```
**Example**:
```bash
# Safe workflow: mark as obsolete → wait 7 days → permanent delete
find . -name "*.obsolete" -type f -mtime +7 -exec /bin/rm {} \;
```

### Delete Specific Obsolete File
```bash
/bin/rm [FILENAME].obsolete
```
**Example**:
```bash
/bin/rm old_config.json.obsolete
```

## Scripting Templates

### Cleanup Script
```bash
#!/bin/bash
# cleanup_[NAME].sh

echo "Cleaning up [DESCRIPTION]..."
./.claude/bin/rmmm [FILES_OR_DIRS]

echo "Verifying [VERIFICATION]..."
[VERIFICATION_COMMAND]

if [ $? -eq 0 ]; then
  echo "✓ Success - files safely removed"
else
  echo "✗ Failed - recovering files"
  find . -name "*.obsolete" | while read file; do
    mv "$file" "${file%.obsolete}"
  done
  exit 1
fi
```
**Example**:
```bash
#!/bin/bash
# cleanup_build.sh

echo "Cleaning up old build artifacts..."
./.claude/bin/rmmm dist/ build/ .cache/

echo "Verifying build still works..."
npm run build

if [ $? -eq 0 ]; then
  echo "✓ Build successful - old artifacts safely removed"
  find . -name "*.obsolete" -mtime +0 -exec /bin/rm -r {} \;
else
  echo "✗ Build failed - recovering old artifacts"
  find . -name "*.obsolete" | while read file; do
    mv "$file" "${file%.obsolete}"
  done
  exit 1
fi
```

### Git Untrack + Local Backup
```bash
# Remove from git but keep local copy
git rm --cached [FILENAME]
./.claude/bin/rmmm [FILENAME]
git commit -m "[COMMIT_MESSAGE]"
```
**Example**:
```bash
git rm --cached .env.production
./.claude/bin/rmmm .env.production
git commit -m "chore: remove .env.production from git tracking"
# File available as .env.production.obsolete
```

### Conditional Removal
```bash
# Only remove if file exists
if [ -e [FILENAME] ]; then
  ./.claude/bin/rmmm [FILENAME]
else
  echo "File not found: [FILENAME]"
fi
```
**Example**:
```bash
if [ -e old_config.json ]; then
  ./.claude/bin/rmmm old_config.json
else
  echo "File not found: old_config.json"
fi
```

## Verification Templates

### Before Removal - Check Dependencies
```bash
# Search for usage before removing
grep -r "[SEARCH_TERM]" [DIRECTORY]

# If no results, safe to remove
./.claude/bin/rmmm [FILE_TO_REMOVE]
```
**Example**:
```bash
grep -r "OldComponent" src/
# No results found
./.claude/bin/rmmm src/components/OldComponent.tsx
```

### After Removal - Verify Build
```bash
./.claude/bin/rmmm [FILES]

# Verify build works
npm run build

# Verify tests pass
npm test

# If issues, recover
# mv [FILE].obsolete [FILE]
```

### After Removal - Verify App Runs
```bash
./.claude/bin/rmmm [FILES]

# Start dev server
npm run dev

# Test functionality manually

# If issues:
# mv [FILE].obsolete [FILE]
# npm run dev
```

## Common Workflows

### Refactoring Workflow
```bash
# 1. Create new implementation
[CREATE_NEW_FILE]

# 2. Update all references
grep -r "[OLD_NAME]" src/
[UPDATE_IMPORTS]

# 3. Remove old file (safely)
./.claude/bin/rmmm [OLD_FILE]

# 4. Verify
npm test && npm run build

# 5. If issues, recover
# mv [OLD_FILE].obsolete [OLD_FILE]

# 6. After confidence (e.g., 1 week), permanent delete
# /bin/rm [OLD_FILE].obsolete
```

### Asset Cleanup Workflow
```bash
# 1. Remove unused assets
./.claude/bin/rmmm [ASSET_FILES]

# 2. Check for broken references
grep -r "[ASSET_NAME]" src/

# 3. Verify UI loads correctly
npm run dev

# 4. Check browser console for 404s

# 5. If issues, recover
# mv [ASSET].obsolete [ASSET]
```

### Test Reorganization Workflow
```bash
# 1. Move/rename tests to new structure
[REORGANIZE_TESTS]

# 2. Remove old test files
./.claude/bin/rmmm [OLD_TEST_FILES]

# 3. Verify tests still pass
npm test

# 4. If issues, recover
# mv [TEST].obsolete [TEST]
```

## Quick Fill Guide

| Placeholder | What to Fill | Example |
|-------------|--------------|---------|
| `[PATH_TO_FILE]` | Relative path to file | `src/components/Old.tsx` |
| `[PATH_TO_DIR]` | Relative path to directory | `dist` or `build` |
| `[FILENAME]` | Just the filename | `config.json` |
| `[FILE1]` `[FILE2]` | Multiple file paths | `old.js` `legacy.css` |
| `[DIRECTORY]` | Directory to search in | `src/` or `.` |
| `[PATTERN]` | Glob pattern | `*.log` or `temp_*` |
| `[SEARCH_TERM]` | Text to search for | `OldComponent` |
| `[TIMESTAMP]` | Date timestamp | `20251109_110500` |
| `[DESCRIPTION]` | Human-readable description | `old build artifacts` |
| `[VERIFICATION_COMMAND]` | Command to verify | `npm run build` |
| `[COMMIT_MESSAGE]` | Git commit message | `chore: remove old config` |

## Safety Checklist Template

Before using rmmm:
```
- [ ] Searched for dependencies: `grep -r "[NAME]" [DIRECTORY]`
- [ ] Backed up important data: [BACKUP_LOCATION]
- [ ] Verified file is truly unused: [VERIFICATION]
- [ ] Know how to recover: `mv [FILE].obsolete [FILE]`
```

After using rmmm:
```
- [ ] Tests pass: `npm test`
- [ ] Build works: `npm run build`
- [ ] App runs: `npm run dev`
- [ ] No console errors: [CHECK_BROWSER]
- [ ] Listed obsolete files: `find . -name "*.obsolete"`
```

## Command Syntax Reference

```bash
# Basic syntax
./.claude/bin/rmmm [TARGET] [TARGET] ...

# TARGET can be:
# - Single file: file.txt
# - Multiple files: file1.txt file2.txt
# - Directory: dirname/
# - Mixed: file1.txt dir1/ file2.txt

# Options: None (simple command)

# Exit codes:
# 0 = Success (all files renamed)
# 1 = Failure (one or more files failed)
```
