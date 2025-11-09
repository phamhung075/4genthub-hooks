---
name: safe-file-removal
description: Use rmmm command to safely 'remove' files by renaming them to .obsolete instead of permanent deletion. Reversible, collision-safe, hook-compliant.
allowed-tools: Bash, Read, Grep
---

# Safe File Removal

Safely "remove" files using `rmmm` command which renames to `.obsolete` instead of permanently deleting.

## When to Use

- Removing temporary files or build artifacts
- Cleaning up after refactoring (keep backup during testing)
- Removing old/deprecated code
- Any situation where `rm` would be blocked by pre-tool hooks
- When you want reversible "deletion"

## Why Not `rm`

**Project setting**: `.claude/settings.json:132` → `"RM_BASH_BLOCK": "true"`

**Issue**:
- `rm` permanently deletes files
- Blocked by pre-tool hooks to prevent accidental data loss
- No recovery mechanism

**Solution**:
- `rmmm` renames files to `.obsolete` (reversible)
- Works within project safety constraints
- Collision-safe with timestamp fallback

## Command Location

```bash
./.claude/bin/rmmm
```

**Path**: `.claude/bin/rmmm:1-72`

## Basic Usage

### Single File
```bash
./.claude/bin/rmmm unwanted_file.txt
# Result: unwanted_file.txt → unwanted_file.txt.obsolete
```

### Multiple Files
```bash
./.claude/bin/rmmm old_file.txt legacy_dir/ another.js
# Result: All three items renamed with .obsolete suffix
```

### From Anywhere (if PATH configured)
```bash
rmmm file_to_remove.txt
```

## Features

| Feature | Benefit |
|---------|---------|
| **Reversible** | `mv file.txt.obsolete file.txt` recovers file |
| **Multi-file** | Handle multiple arguments in one command |
| **Collision safe** | Adds timestamp if .obsolete exists (file.txt.obsolete.20251109_110500) |
| **Color output** | Green (success), Yellow (warning), Red (error) |
| **Statistics** | Reports renamed/failed count |
| **Error handling** | Validates existence, clear error messages |

## Recovery Process

### Restore Single File
```bash
mv important.txt.obsolete important.txt
```

### Restore with Timestamp
```bash
mv config.json.obsolete.20251109_110500 config.json
```

### Find All Obsolete Files
```bash
find . -name "*.obsolete" -type f
```

## Workflow

1. **Mark as obsolete** - Use rmmm instead of rm
2. **Verify system works** - Run tests, build, manual testing
3. **Review periodically** - `find . -name "*.obsolete"`
4. **Permanent delete** (when confident) - After verification period

## Common Patterns

See **[EXAMPLES.md](EXAMPLES.md)** for real-world scenarios:
- Removing temporary files
- Cleaning up after refactoring
- Removing test files
- Collision handling
- Asset cleanup
- Documentation cleanup

## Templates

See **[TEMPLATES.md](TEMPLATES.md)** for copy-paste commands:
- Single file removal
- Multiple files removal
- Directory removal
- Batch operations with find
- Recovery commands

## Validation

See **[VALIDATION.md](VALIDATION.md)** for safety checks:
- Pre-removal verification
- Post-removal testing
- Recovery testing
- Cleanup validation

## When NOT to Use

| Scenario | Use rmmm? | Reason |
|----------|-----------|--------|
| Sensitive files (secrets, keys) | ❌ No | Needs secure deletion + git history rewrite |
| .git folder | ❌ No | Too risky |
| node_modules | ⚠️ Maybe | Usually safe to delete, but rmmm works |
| Temp/build artifacts | ✅ Yes | Safe, reversible |

## Key Insights

**Safety by Design**:
- No permanent deletion - every operation reversible
- Collision protection - timestamp fallback prevents overwrites
- Hook compliance - works within project safety constraints
- Audit trail - obsolete files remain visible for review

**Development Workflow**:
1. Refactor code
2. Use rmmm on old files
3. Test thoroughly
4. Keep .obsolete for review period
5. Permanently delete after confidence

## Quick Reference

| Task | Command |
|------|---------|
| Remove single | `./.claude/bin/rmmm file.txt` |
| Remove multiple | `./.claude/bin/rmmm file1 file2 dir/` |
| Restore | `mv file.txt.obsolete file.txt` |
| List obsolete | `find . -name "*.obsolete"` |
| Count obsolete | `find . -name "*.obsolete" \| wc -l` |

## Supporting Files

- **[EXAMPLES.md](EXAMPLES.md)** - Real-world patterns and scenarios
- **[TEMPLATES.md](TEMPLATES.md)** - Copy-paste commands for common tasks
- **[VALIDATION.md](VALIDATION.md)** - Safety checks and quality verification
