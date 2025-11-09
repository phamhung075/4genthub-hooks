# Safe File Removal Examples

Real-world patterns for using `safe-rm` in different scenarios for replace `rm` bash command

## Pattern Summary

| # | Pattern | Command | When |
|---|---------|---------|------|
| 1 | Temp files | `safe-rm dist/ build/ .cache/` | After build, before commit |
| 2 | Refactoring | `safe-rm src/OldComponent.tsx` | During component replacement |
| 3 | Multiple tests | `safe-rm test1.spec.ts test2.spec.ts deprecated/` | Test reorganization |
| 4 | Collision | `safe-rm file.txt` (twice) | Adds timestamp automatically |
| 5 | Assets | `safe-rm public/old_logo.png icons/deprecated/` | Unused images/icons |
| 6 | Documentation | `safe-rm docs/OLD_README.md` | Outdated docs |
| 7 | Batch ops | `find . -name "*.log" -exec safe-rm {} \;` | Pattern-based cleanup |
| 8 | Scripting | See cleanup_build.sh template | Automated workflows |
| 9 | Git untrack | `git rm --cached file; safe-rm file` | Remove from git, keep local |
| 10 | Hook prevention | Agent blocked by rm → uses safe-rm | Safety enforcement |

## Scenario 1: Temp Files

**Before** (blocked):
```bash
rm -rf dist/ build/ .cache/  # ❌ BLOCKED by hooks
```

**After**:
```bash
safe-rm dist/ build/ .cache/  # ✅ Works

# Output:
# ✓ Renamed: dist/ → dist/.obsolete
# ✓ Renamed: build/ → build/.obsolete
# ✓ Renamed: .cache/ → .cache/.obsolete
```

**Recovery** (if needed): `mv dist/.obsolete dist/` or `npm run build` to regenerate

## Scenario 2: Refactoring Workflow

```bash
# 1. Create new
# [implement ComponentNew.tsx]

# 2. Update imports
# [change references]

# 3. Remove old (safely)
safe-rm src/components/ComponentOld.tsx

# 4. Verify
npm test && npm run build

# 5. If issues → mv ComponentOld.tsx.obsolete ComponentOld.tsx
# 6. After 1 week → /bin/rm ComponentOld.tsx.obsolete
```

## Scenario 3: Multiple Test Files

```bash
safe-rm src/tests/old_test_1.spec.ts \
     src/tests/old_test_2.spec.ts \
     src/tests/deprecated/

npm test  # Verify

find src/tests -name "*.obsolete"  # Review what was removed
```

## Scenario 4: Collision Handling

```bash
# First run
safe-rm config.old.json
# Result: config.old.json.obsolete

# Restore file
mv config.old.json.obsolete config.old.json

# Second run (collision)
safe-rm config.old.json
# Output: ⚠ Already exists: config.old.json.obsolete
#         Using: config.old.json.obsolete.20251109_110500
# Result: config.old.json.obsolete.20251109_110500
```

**Benefit**: Never overwrites existing .obsolete files

## Scenario 5: Asset Cleanup

```bash
safe-rm public/images/old_logo.png \
     public/icons/deprecated/ \
     assets/unused_banner.svg

npm run dev  # Verify UI loads, check for 404s
```

## Scenario 6: Documentation Cleanup

```bash
safe-rm docs/OLD_README.md \
     docs/deprecated/api-v1-guide.md

grep -r "OLD_README\|api-v1-guide" docs/  # Check for broken links
npm run docs:build  # Verify docs site builds
```

## Scenario 7: Batch Operations

```bash
# All .log files
find . -name "*.log" -exec safe-rm {} \;

# Empty directories
find . -type d -empty -exec safe-rm {} \;

# Files older than 30 days
find logs/ -type f -mtime +30 -exec safe-rm {} \;
```

## Scenario 8: Scripting Example

```bash
#!/bin/bash
# cleanup_build.sh

echo "Cleaning build artifacts..."
safe-rm dist/ build/ .cache/

echo "Verifying build..."
npm run build

if [ $? -eq 0 ]; then
  echo "✓ Build successful"
  find . -name "*.obsolete" -mtime +0 -exec /bin/rm -r {} \;
else
  echo "✗ Build failed - recovering"
  find . -name "*.obsolete" | while read f; do mv "$f" "${f%.obsolete}"; done
  exit 1
fi
```

## Scenario 9: Git Untrack + Local Backup

```bash
# Remove from git, keep local copy
git rm --cached sensitive_config.json
safe-rm sensitive_config.json
git commit -m "chore: remove sensitive config from repo"

# File available as sensitive_config.json.obsolete
# Recover: mv sensitive_config.json.obsolete sensitive_config.json
```

## Scenario 10: Hook Prevention

```bash
# Agent attempts rm → BLOCKED
rm old_file.txt
# Error: "BLOCKED: Dangerous rm command"

# Agent uses safe-rm → SUCCESS
safe-rm old_file.txt
# ✓ Renamed: old_file.txt → old_file.txt.obsolete

# User reviews → decides restore or delete
```

## Recovery Examples

| Scenario | Command |
|----------|---------|
| Single file | `mv file.txt.obsolete file.txt` |
| Multiple | `mv f1.obsolete f1; mv f2.obsolete f2` |
| With timestamp | `mv config.json.obsolete.20251109_110500 config.json` |
| All in dir | `find . -name "*.obsolete" \| while read f; do mv "$f" "${f%.obsolete}"; done` |

## Common Mistakes

| Mistake | Issue | Fix |
|---------|-------|-----|
| **safe-rm on .obsolete repeatedly** | file.obsolete.obsolete.obsolete | `mv file.obsolete file` or `/bin/rm file.obsolete` |
| **No dependency check** | Breaks build | `grep -r "filename" src/` before safe-rm |
| **Never clean up** | Clutter accumulates | Weekly `find . -name "*.obsolete" -mtime +7` |
| **Sensitive files** | Still visible in filesystem | Use secure deletion for secrets |

## Output Patterns

| Result | Output |
|--------|--------|
| **Success** | `✓ Renamed: 3` |
| **Collision** | `⚠ Already exists` + timestamp fallback |
| **Error** | `✗ Not found` + `Failed: 1` |
| **Mixed** | `Renamed: 2` + `Failed: 1` |

## Best Practices

1. **Mark obsolete first** → Don't delete immediately
2. **Verify system works** → `npm test && npm run build`
3. **Keep review period** → 1 day to 1 week depending on risk
4. **List periodically** → `find . -name "*.obsolete"`
5. **Permanent delete** → After confidence with `/bin/rm`

## Integration with Hooks

**Setting**: `.claude/settings.json:132` → `"RM_BASH_BLOCK": "true"`

**Flow**: Agent tries rm → Blocked → Uses safe-rm → User reviews → Decides

**Benefit**: Prevents accidental data loss during AI operations

## Session Example (2025-11-09)

- Created safe-rm command (`.claude/bin/safe-rm:1-72`)
- Tested with temporary files
- Demonstrated collision handling (timestamp fallback)
- Used in skill restructuring (removed old skill.md/skill.json)
- Integrated with pre-tool hooks (rm blocked, safe-rm allowed)
