# Safe File Removal Validation

Quality checks for safe file removal operations.

## Quick Checklists

### Before Removal
- [ ] `grep -r "[NAME]" [DIR]` → No results
- [ ] No imports depending on file
- [ ] Know recovery: `mv [FILE].obsolete [FILE]`

### After Removal
- [ ] `npm test` → Pass
- [ ] `npm run build` → Success
- [ ] `npm run dev` → Works
- [ ] No browser console errors
- [ ] `find . -name "*.obsolete"` → Listed

### Before Permanent Delete
- [ ] Time passed (1-7 days review period)
- [ ] System stable (no issues discovered)
- [ ] `find . -name "*.obsolete" -mtime +[DAYS]` → Old enough

## Validation Commands

| Check | Command |
|-------|---------|
| **Check usage** | `grep -r "[FILENAME_WITHOUT_EXT]" [DIR]` |
| **Check imports** | `grep -r "from.*[FILENAME]" src/` |
| **File exists** | `ls -la [PATH_TO_FILE]` |
| **Verify renamed** | `ls -la [FILE].obsolete` |
| **Run tests** | `npm test` |
| **Run build** | `npm run build` |
| **TypeScript check** | `npx tsc --noEmit` |
| **List obsolete** | `find . -name "*.obsolete"` |
| **Count obsolete** | `find . -name "*.obsolete" \| wc -l` |
| **Find old (7+ days)** | `find . -name "*.obsolete" -mtime +7` |
| **Disk space** | `du -sh $(find . -name "*.obsolete")` |

## Critical Files - Never Use safe-rm

| File/Directory | Why | Alternative |
|----------------|-----|-------------|
| `.git/` | Lose entire history | Use git commands |
| `.env*` | Contains secrets | Secure deletion + git history rewrite |
| `package.json` | Critical config | Version control |
| `database/` | Data loss | Backup + migration |

## Quality Checks by Type

| Type | Required Checks |
|------|-----------------|
| **Source code** | `grep -r "[NAME]" src/` → No imports → `npm test && npm run build` |
| **Assets** | Check references → Verify UI → No 404s in console |
| **Tests** | Remaining tests pass → Coverage maintained |
| **Documentation** | No broken links → Docs site builds |

## Common Pitfalls

| Pitfall | Detection | Prevention |
|---------|-----------|------------|
| **Still imported** | `grep -r "import.*[FILE]"` finds results | Check before removal |
| **Dynamic reference** | `grep -r "[FILENAME]"` shows string refs | Search for string usage |
| **Test dependency** | Tests fail after removal | Run tests immediately |
| **Build breaks** | Build errors appear | Run build immediately |

## Validation Script

```bash
#!/bin/bash
# validate_removal.sh [FILE]

FILE="$1"
[ -z "$FILE" ] && echo "Usage: $0 [FILE]" && exit 1

echo "=== Pre-Removal ==="
[ ! -e "$FILE" ] && echo "✗ Not found: $FILE" && exit 1
echo "✓ File exists"

FILENAME=$(basename "$FILE" | sed 's/\.[^.]*$//')
USAGE=$(grep -r "$FILENAME" src/ 2>/dev/null | wc -l)

if [ $USAGE -gt 1 ]; then
  echo "⚠ Found $USAGE references"
  grep -r "$FILENAME" src/ | head -10
  read -p "Continue? (y/N) " -r
  [[ ! $REPLY =~ ^[Yy]$ ]] && exit 1
fi
echo "✓ No usage"

echo -e "\n=== Removing ==="
safe-rm "$FILE" || (echo "✗ Failed" && exit 1)
echo "✓ Removed"

echo -e "\n=== Post-Removal ==="
[ ! -e "$FILE.obsolete" ] && echo "✗ .obsolete not found" && exit 1
echo "✓ .obsolete exists"

echo -e "\nRunning tests..."
npm test > /dev/null 2>&1 || (echo "✗ Tests failed - recovering" && mv "$FILE.obsolete" "$FILE" && exit 1)
echo "✓ Tests pass"

echo -e "\nRunning build..."
npm run build > /dev/null 2>&1 || (echo "✗ Build failed - recovering" && mv "$FILE.obsolete" "$FILE" && exit 1)
echo "✓ Build succeeds"

echo -e "\n=== Complete ==="
echo "✓ Safely removed: $FILE → $FILE.obsolete"
echo "⚠ Review and delete later: /bin/rm $FILE.obsolete"
```

## Recovery Testing

```bash
# 1. Remove test file
echo "test" > test_file.txt
safe-rm test_file.txt

# 2. Verify removed
ls test_file.txt 2>&1 | grep "No such file"

# 3. Verify .obsolete exists
ls test_file.txt.obsolete

# 4. Recover
mv test_file.txt.obsolete test_file.txt

# 5. Verify recovered
cat test_file.txt | grep "test"

# 6. Cleanup
/bin/rm test_file.txt
```

## Collision Testing

```bash
# 1. Create and remove
echo "v1" > test.txt
safe-rm test.txt

# 2. Restore and modify
mv test.txt.obsolete test.txt
echo "v2" > test.txt

# 3. Remove again (collision)
safe-rm test.txt

# 4. Verify timestamp version
ls -la test.txt.obsolete.*

# 5. Cleanup
/bin/rm test.txt.obsolete*
```

## Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| **Not found** | File doesn't exist | Check path with `ls` |
| **Permission denied** | No write access | `chmod` or sudo |
| **Already exists** | .obsolete file present | Handled by timestamp fallback |

## Monitoring

```bash
# Daily log
echo "$(date): $(find . -name '*.obsolete' | wc -l) files" >> .obsolete_log

# Weekly cleanup check
find . -name "*.obsolete" -mtime +7 | wc -l

# Space monitoring
du -sh $(find . -name "*.obsolete" 2>/dev/null)
```

## Integration Check

### Pre-Tool Hook
```bash
# Verify rm blocked
rm test.txt 2>&1 | grep "BLOCKED"  # Should show block message

# Verify safe-rm works
safe-rm test.txt  # Should succeed
```

### Settings Verification
```bash
grep "RM_BASH_BLOCK" .claude/settings.json  # Should be "true"
```

## Best Practices Verification

- [ ] Used safe-rm (not `rm`)
- [ ] Searched first (`grep -r`)
- [ ] Tested after (`npm test && npm run build`)
- [ ] Kept review period (1-7 days)
- [ ] Listed periodically (`find . -name "*.obsolete"`)

## Quick Reference

| Check | Command |
|-------|---------|
| **Pre-removal** | `grep -r "[NAME]" src/` |
| **Post-removal** | `npm test && npm run build` |
| **List obsolete** | `find . -name "*.obsolete"` |
| **Find old** | `find . -name "*.obsolete" -mtime +7` |
| **Verify hook** | `grep "RM_BASH_BLOCK" .claude/settings.json` |
