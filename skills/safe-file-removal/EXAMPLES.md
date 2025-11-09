# Safe File Removal Examples

Real-world patterns for using `rmmm` in different scenarios for replace `rm` bash command

## Example Patterns

| Pattern | Command | Result |
|---------|---------|--------|
| **Temp files** | `./.claude/bin/rmmm dist/ build/` | Directories become dist.obsolete/ build.obsolete/ |
| **Old code** | `./.claude/bin/rmmm src/old_component.tsx` | src/old_component.tsx.obsolete |
| **Multiple files** | `./.claude/bin/rmmm file1 file2 file3` | All three get .obsolete suffix |
| **Collision** | `./.claude/bin/rmmm file.txt` (twice) | file.txt.obsolete.20251109_110559 |
| **Recovery** | `mv file.txt.obsolete file.txt` | Restored to original |

## Scenario 1: Removing Temporary Files

**Context**: Development artifacts that can be regenerated

```bash
# ❌ WRONG - Blocked by hooks
rm -rf dist/ build/ .cache/

# ✅ CORRECT - Safe removal
./.claude/bin/rmmm dist/ build/ .cache/
```

**Output**:
```
✓ Renamed: dist/ → dist/.obsolete
✓ Renamed: build/ → build/.obsolete
✓ Renamed: .cache/ → .cache/.obsolete

─────────────────────────────────────
Renamed: 3
─────────────────────────────────────
```

**Recovery** (if needed):
```bash
mv dist/.obsolete dist/
npm run build  # Regenerate if recovery not needed
```

## Scenario 2: Cleaning Up After Refactoring

**Context**: Replaced ComponentOld.tsx with ComponentNew.tsx

```bash
# Step 1: Create new component
# (implement ComponentNew.tsx)

# Step 2: Update imports to use new component
# (update all references)

# Step 3: Remove old component (safely)
./.claude/bin/rmmm src/components/ComponentOld.tsx

# Step 4: Verify new component works
npm test
npm run build

# Step 5: If issues, recover old component
# mv src/components/ComponentOld.tsx.obsolete src/components/ComponentOld.tsx

# Step 6: After confidence (e.g., 1 week), permanently delete
# /bin/rm src/components/ComponentOld.tsx.obsolete
```

**Benefit**: Old implementation available during testing period

## Scenario 3: Removing Multiple Test Files

**Context**: Deprecated test files after test reorganization

```bash
# Remove multiple test files at once
./.claude/bin/rmmm \
  src/tests/old_test_1.spec.ts \
  src/tests/old_test_2.spec.ts \
  src/tests/deprecated/

# Verify tests still pass
npm test

# Find what was removed
find src/tests -name "*.obsolete"
```

**Output**:
```
✓ Renamed: src/tests/old_test_1.spec.ts → src/tests/old_test_1.spec.ts.obsolete
✓ Renamed: src/tests/old_test_2.spec.ts → src/tests/old_test_2.spec.ts.obsolete
✓ Renamed: src/tests/deprecated/ → src/tests/deprecated/.obsolete

─────────────────────────────────────
Renamed: 3
─────────────────────────────────────
```

## Scenario 4: Collision Handling

**Context**: Running rmmm on same file multiple times

```bash
# First run
./.claude/bin/rmmm config.old.json
# Result: config.old.json.obsolete

# File restored for some reason
mv config.old.json.obsolete config.old.json

# Second run (collision)
./.claude/bin/rmmm config.old.json
# Result: config.old.json.obsolete.20251109_110500
```

**Output**:
```
⚠ Already exists: config.old.json.obsolete
  Using: config.old.json.obsolete.20251109_110500
✓ Renamed: config.old.json → config.old.json.obsolete.20251109_110500

─────────────────────────────────────
Renamed: 1
─────────────────────────────────────
```

**Benefit**: Never overwrites existing .obsolete files

## Scenario 5: Asset Cleanup

**Context**: Removing unused images and icons

```bash
# Remove unused assets
./.claude/bin/rmmm \
  public/images/old_logo.png \
  public/icons/deprecated/ \
  assets/unused_banner.svg

# Verify app still loads
npm run dev
# Check for broken images in UI

# If no issues after testing, permanently delete
# find public/ assets/ -name "*.obsolete" -exec /bin/rm -r {} \;
```

## Scenario 6: Documentation Cleanup

**Context**: Removing outdated documentation

```bash
# Move outdated docs to obsolete status
./.claude/bin/rmmm \
  docs/OLD_README.md \
  docs/deprecated/api-v1-guide.md

# Update links in other docs
grep -r "OLD_README\|api-v1-guide" docs/

# Verify documentation site builds
npm run docs:build
```

## Scenario 7: Batch Operations with Find

**Context**: Find and remove all files matching pattern

```bash
# Find all .log files and remove them
find . -name "*.log" -type f -exec ./.claude/bin/rmmm {} \;

# Find and remove empty directories
find . -type d -empty -exec ./.claude/bin/rmmm {} \;

# Find files older than 30 days and remove
find . -type f -mtime +30 -exec ./.claude/bin/rmmm {} \;
```

**Benefit**: Automated cleanup with safety net

## Scenario 8: Scripting with rmmm

**Context**: Cleanup script for CI/CD pipeline

```bash
#!/bin/bash
# cleanup_old_builds.sh

echo "Cleaning up old build artifacts..."
./.claude/bin/rmmm dist/ build/ .cache/

echo "Verifying build still works..."
npm run build

if [ $? -eq 0 ]; then
  echo "✓ Build successful - old artifacts safely removed"

  # Permanently delete after successful build
  find . -name "*.obsolete" -mtime +0 -exec /bin/rm -r {} \;
  echo "✓ Cleanup complete"
else
  echo "✗ Build failed - recovering old artifacts"
  find . -name "*.obsolete" | while read file; do
    mv "$file" "${file%.obsolete}"
  done
  exit 1
fi
```

## Scenario 9: Combined with Git

**Context**: Remove from git but keep locally as backup

```bash
# Remove file from git tracking
git rm --cached sensitive_config.json

# Keep local copy as .obsolete
./.claude/bin/rmmm sensitive_config.json

# Commit removal
git commit -m "chore: remove sensitive config from repo"

# File still available locally as sensitive_config.json.obsolete
# Can recover if needed: mv sensitive_config.json.obsolete sensitive_config.json
```

## Scenario 10: Preventing Accidental Deletion

**Context**: Agent blocked by rm hook

```bash
# Agent attempts rm
rm old_file.txt
# Error: "BLOCKED: Dangerous rm command that could delete critical files"

# Agent uses rmmm instead
./.claude/bin/rmmm old_file.txt
# Success: "✓ Renamed: old_file.txt → old_file.txt.obsolete"

# User can review and decide
ls -la *.obsolete
# If truly unwanted:
# /bin/rm old_file.txt.obsolete
# If needed:
# mv old_file.txt.obsolete old_file.txt
```

## Output Examples

### Success Case
```
✓ Renamed: old_file.txt → old_file.txt.obsolete
✓ Renamed: legacy_dir/ → legacy_dir/.obsolete
✓ Renamed: unused.js → unused.js.obsolete

─────────────────────────────────────
Renamed: 3
─────────────────────────────────────
```

### Error Case
```
✗ Not found: nonexistent_file.txt
✓ Renamed: real_file.txt → real_file.txt.obsolete

─────────────────────────────────────
Renamed: 1
Failed: 1
─────────────────────────────────────
```

### Collision with Timestamp
```
⚠ Already exists: config.json.obsolete
  Using: config.json.obsolete.20251109_110559
✓ Renamed: config.json → config.json.obsolete.20251109_110559

─────────────────────────────────────
Renamed: 1
─────────────────────────────────────
```

## Common Mistake Patterns

### ❌ WRONG: Using rmmm Repeatedly on .obsolete Files
```bash
./.claude/bin/rmmm file.txt.obsolete
./.claude/bin/rmmm file.txt.obsolete.obsolete
./.claude/bin/rmmm file.txt.obsolete.obsolete.obsolete
# Results in: file.txt.obsolete.obsolete.obsolete.obsolete
```

### ✅ RIGHT: Restore or Permanently Delete
```bash
# Either restore
mv file.txt.obsolete file.txt

# Or permanently delete
/bin/rm file.txt.obsolete
```

### ❌ WRONG: Not Checking Dependencies
```bash
# Remove without checking usage
./.claude/bin/rmmm src/utils/important_helper.js
# Other files still import it - breaks build
```

### ✅ RIGHT: Search First, Then Remove
```bash
# Search for usage
grep -r "important_helper" src/

# If no results, safe to remove
./.claude/bin/rmmm src/utils/important_helper.js
```

## Recovery Examples

### Recover Single File
```bash
# File was: important.txt → important.txt.obsolete
mv important.txt.obsolete important.txt
```

### Recover Multiple Files
```bash
# Find all obsolete files
find . -name "*.obsolete" -type f

# Restore specific ones
mv src/utils/helper.js.obsolete src/utils/helper.js
mv tests/integration.spec.ts.obsolete tests/integration.spec.ts
```

### Recover All Files in Directory
```bash
# Restore all .obsolete files (USE WITH CAUTION)
find . -name "*.obsolete" -type f | while read file; do
  mv "$file" "${file%.obsolete}"
done
```

## Integration with Project Hooks

**Setting**: `.claude/settings.json:132` → `"RM_BASH_BLOCK": "true"`

**Workflow**:
```bash
# 1. Agent attempts rm (blocked)
rm old_file.txt
# Error: BLOCKED by pre-tool hook

# 2. Agent uses rmmm (allowed)
./.claude/bin/rmmm old_file.txt
# Success: ✓ Renamed

# 3. User reviews
ls -la *.obsolete

# 4. User decides: restore or permanent delete
```

**Benefit**: Safety net prevents accidental data loss during AI operations

## When to Use vs. When to Skip

| Scenario | Use rmmm? | Alternative |
|----------|-----------|-------------|
| Temp build artifacts | ✅ Yes | Can regenerate anyway |
| Old implementation | ✅ Yes | Keep backup during testing |
| Test files | ✅ Yes | Easy to recover if mistake |
| Unused assets | ✅ Yes | Verify UI before permanent delete |
| node_modules | ⚠️ Maybe | `npm install` regenerates, but rmmm works |
| .env files | ❌ No | Contains secrets - needs secure deletion |
| .git folder | ❌ No | Too risky - lose entire history |

## Best Practices

1. **Use rmmm for first-pass cleanup** - Mark files as obsolete
2. **Verify system works** - Run tests, build, manual checks
3. **Keep review period** - 1 day to 1 week depending on risk
4. **List periodically** - `find . -name "*.obsolete"` to review
5. **Permanently delete** - After confidence period with `/bin/rm`

## Metrics Example

**Session 2025-11-09**:
- Created rmmm command (`.claude/bin/rmmm:1-72`)
- Tested with temporary files (successful)
- Demonstrated collision handling (timestamp fallback)
- Integrated with pre-tool hooks (rm blocked, rmmm allowed)
- Used in skill restructuring (removed old skill.md/skill.json)
