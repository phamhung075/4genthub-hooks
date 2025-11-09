# Safe File Removal Templates

Copy-paste commands. Replace `[PLACEHOLDERS]` with actual values.

## Basic Operations

| Operation | Template |
|-----------|----------|
| **Single file** | `safe-rm [PATH_TO_FILE]` |
| **Multiple** | `safe-rm [FILE1] [FILE2] [FILE3]` |
| **Directory** | `safe-rm [PATH_TO_DIR]/` |
| **Mixed** | `safe-rm [FILE1] [DIR1]/ [FILE2]` |

**Example**:
```bash
safe-rm src/components/OldComponent.tsx
safe-rm old_file.txt legacy.js unused.css
safe-rm dist/ build/ .cache/
```

## Recovery

| Operation | Template |
|-----------|----------|
| **Single** | `mv [FILENAME].obsolete [FILENAME]` |
| **Timestamp** | `mv [FILENAME].obsolete.[TIMESTAMP] [FILENAME]` |
| **Multiple** | `mv [F1].obsolete [F1]; mv [F2].obsolete [F2]` |
| **All in dir** | `find [DIR] -name "*.obsolete" \| while read f; do mv "$f" "${f%.obsolete}"; done` |

**Example**:
```bash
mv important.txt.obsolete important.txt
mv config.json.obsolete.20251109_110500 config.json
```

## Search & List

| Operation | Template |
|-----------|----------|
| **List all** | `find . -name "*.obsolete"` |
| **In directory** | `find [DIR] -name "*.obsolete"` |
| **Count** | `find . -name "*.obsolete" \| wc -l` |
| **With details** | `find . -name "*.obsolete" -ls` |
| **Disk space** | `du -sh $(find . -name "*.obsolete")` |
| **Recent (7 days)** | `find . -name "*.obsolete" -mtime -7` |
| **Old (30+ days)** | `find . -name "*.obsolete" -mtime +30` |

## Batch Operations

| Operation | Template |
|-----------|----------|
| **All .log files** | `find . -name "*.log" -exec safe-rm {} \;` |
| **Empty directories** | `find . -type d -empty -exec safe-rm {} \;` |
| **Old files** | `find [DIR] -type f -mtime +30 -exec safe-rm {} \;` |
| **Pattern match** | `find [DIR] -name "[PATTERN]" -exec safe-rm {} \;` |
| **All in directory** | `find [DIR] -type f -exec safe-rm {} \;` |

**Example**:
```bash
find temp/ -name "*.tmp" -exec safe-rm {} \;
find logs/ -type f -mtime +30 -exec safe-rm {} \;
```

## Cleanup

| Operation | Template |
|-----------|----------|
| **Delete all .obsolete** | `find . -name "*.obsolete" -exec /bin/rm -r {} \;` |
| **Delete old (7+ days)** | `find . -name "*.obsolete" -mtime +7 -exec /bin/rm {} \;` |
| **Delete specific** | `/bin/rm [FILENAME].obsolete` |

## Scripting

### Cleanup Script
```bash
#!/bin/bash
# cleanup_[NAME].sh

echo "Cleaning [DESCRIPTION]..."
safe-rm [FILES_OR_DIRS]

echo "Verifying..."
[VERIFICATION_COMMAND]

if [ $? -eq 0 ]; then
  echo "✓ Success"
  find . -name "*.obsolete" -mtime +0 -exec /bin/rm -r {} \;
else
  echo "✗ Failed - recovering"
  find . -name "*.obsolete" | while read f; do mv "$f" "${f%.obsolete}"; done
  exit 1
fi
```

### Git Untrack
```bash
git rm --cached [FILENAME]
safe-rm [FILENAME]
git commit -m "[MESSAGE]"
# File available as [FILENAME].obsolete
```

### Conditional Removal
```bash
if [ -e [FILENAME] ]; then
  safe-rm [FILENAME]
else
  echo "File not found: [FILENAME]"
fi
```

## Verification

### Before Removal
```bash
# Check usage
grep -r "[SEARCH_TERM]" [DIRECTORY]

# If no results, safe to remove
safe-rm [FILE_TO_REMOVE]
```

### After Removal
```bash
safe-rm [FILES]

# Verify
npm run build
npm test

# If issues
# mv [FILE].obsolete [FILE]
```

## Workflows

### Refactoring
```bash
# 1. Create new
[CREATE_NEW_FILE]

# 2. Update references
grep -r "[OLD_NAME]" src/
[UPDATE_IMPORTS]

# 3. Remove old
safe-rm [OLD_FILE]

# 4. Verify
npm test && npm run build

# 5. If issues → mv [OLD_FILE].obsolete [OLD_FILE]
# 6. After confidence → /bin/rm [OLD_FILE].obsolete
```

### Asset Cleanup
```bash
# 1. Remove
safe-rm [ASSET_FILES]

# 2. Check references
grep -r "[ASSET_NAME]" src/

# 3. Verify UI
npm run dev

# 4. Check browser console for 404s
# 5. If issues → mv [ASSET].obsolete [ASSET]
```

## Quick Reference

| Placeholder | Example |
|-------------|---------|
| `[PATH_TO_FILE]` | `src/components/Old.tsx` |
| `[PATH_TO_DIR]` | `dist` or `build` |
| `[FILENAME]` | `config.json` |
| `[FILE1]` `[FILE2]` | `old.js` `legacy.css` |
| `[DIRECTORY]` | `src/` or `.` |
| `[PATTERN]` | `*.log` or `temp_*` |
| `[TIMESTAMP]` | `20251109_110500` |
| `[DESCRIPTION]` | `old build artifacts` |
| `[VERIFICATION_COMMAND]` | `npm run build` |
| `[MESSAGE]` | `chore: remove old config` |

## Safety Checklist

### Before
```
- [ ] grep -r "[NAME]" [DIR]
- [ ] Know recovery: mv [FILE].obsolete [FILE]
```

### After
```
- [ ] npm test
- [ ] npm run build
- [ ] npm run dev (manual test)
- [ ] find . -name "*.obsolete"
```
