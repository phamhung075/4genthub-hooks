# Changelog Validation

Quality checks and validation rules for changelog entries.

## Quick Checklist

- [ ] **Format**: Correct section (### Added/Changed/Fixed under ## [Unreleased])
- [ ] **Date**: YYYY-MM-DD format (today's date)
- [ ] **Concise**: <10 lines (unless complex table)
- [ ] **Metrics**: Quantifiable impact included
- [ ] **Files**: Specific paths with :line numbers
- [ ] **Optimized**: Tables for multi-item, patterns for summaries
- [ ] **No duplicates**: Single ### Added, ### Changed, ### Fixed
- [ ] **Markdown**: Proper **, -, `` formatting
- [ ] **Grouped**: Related changes combined

## Section Placement

| Change Type | Section | Examples |
|-------------|---------|----------|
| New features/tools/systems | ### Added | Agents, CLI, skills, docs |
| Modifications/optimizations | ### Changed | Refactors, optimizations, migrations |
| Bug fixes/corrections | ### Fixed | Path fixes, database fixes, tests |

**Validation**: `awk '/^## \[Unreleased\]/,/^## \[/' CHANGELOG.md | grep "^###" | sort | uniq -c`
- Should show: 1 ### Added, 1 ### Changed, 1 ### Fixed

## Entry Requirements by Type

| Type | Required Elements | Example |
|------|-------------------|---------|
| **Optimization** | % or metric in title + before→after + impact | **Name - 55.7% Reduction** |
| **Feature** | Scope + key mechanism + location | **Agent System** (33 agents via call_agent) |
| **Fix** | Problem + solution + files:lines + result | **Hooks Paths** (old→new, files, loads correctly) |
| **Cleanup** | Total lines in title + breakdown + prevented bloat | **Dead Code - 2,430 Lines** |

## Common Pitfalls

| Pitfall | Problem | Fix |
|---------|---------|-----|
| **Duplicate sections** | Multiple ### Changed in Unreleased | Consolidate into single section |
| **Wrong section** | Analysis/Optimization in Added | Put in ### Changed |
| **Too verbose** | 50+ lines explaining methodology | 5-10 lines: what, why, impact |
| **No metrics** | "Optimized files" | "31 files: 1,878→832 (55.7%)" |
| **Missing files** | "Updated configs" | `.claude/hooks/config.py:20,78-83` |
| **Vague** | "Much faster, many files" | "2x faster (200→100ms), 31 files" |
| **Scattered** | 3 entries for same work | 1 grouped entry |

## Title Format

| Pattern | When to Use | Example |
|---------|-------------|---------|
| `**Name - % Reduction**` | Optimizations with % | Agent Files - 55.7% Reduction |
| `**Type - Lines Removed**` | Code cleanup | Dead Code - 2,430 Lines |
| `**Feature Name**` | New capabilities | Agent Management System |
| `**Component Fixed**` | Bug fixes | Hooks Path References |
| `**Suite - Metric**` | Multi-component | Token Suite - 21-28k Saved |

## Date Format

**Correct**: `**Title** (2025-11-03)`
**Check**: `date +%Y-%m-%d` for today's date
**Validation**: `grep -oE "\([0-9]{4}-[0-9]{2}-[0-9]{2}\)" CHANGELOG.md`

## Metrics Format

| Metric | Format | Example |
|--------|--------|---------|
| Lines | `X → Y (Z removed, N%)` | 1,878 → 832 (1,046, 55.7%) |
| Tokens | `X-Y per session` | 6,000-8,000 per session |
| Percentage | `N% reduction` | 97.5% reduction |
| Size | `XKB → YKB` | 271KB → 6.8KB |
| Count | `N items` | 33 agents |
| Change | `old → new` | scripts/ → .claude/ |

## Content Length Guidelines

| Entry Type | Target Lines | Justification |
|------------|--------------|---------------|
| Simple feature | 3-5 | Name, description, location |
| Bug fix | 3-5 | Problem, solution, result |
| Standard optimization | 5-8 | Metrics, technique, impact |
| Table optimization | 8-15 | Table needs structure |
| Multi-phase project | 10-15 | Phased breakdown + cumulative |

## Validation Commands

```bash
# Check section structure (should be: Added, Changed, Fixed)
awk '/^## \[Unreleased\]/,/^## \[/' CHANGELOG.md | grep "^###"

# Verify dates are YYYY-MM-DD
grep -oE "\([0-9]{4}-[0-9]{2}-[0-9]{2}\)" CHANGELOG.md | tail -5

# Check for duplicate sections
awk '/^## \[Unreleased\]/,/^## \[/' CHANGELOG.md | grep "^###" | sort | uniq -c

# Verify bullets use "- " not "* " or "+ "
grep "^\*\|^+\|^[0-9]\." CHANGELOG.md
# Should return nothing

# Check title format
grep "^\*\*.*\*\* (" CHANGELOG.md | tail -5

# Verify line count (~170-200 for maintained log)
wc -l CHANGELOG.md
```

## Code Formatting Rules

| Element | Format | Example |
|---------|--------|---------|
| Function | `` `function()` `` | `call_agent()` |
| File path | `` `path/file` `` | `config_validator.py` |
| Command | `` `command` `` | `git status` |
| Technical term | `` `term` `` | `JWT`, `YAML` |
| Code | `` `code` `` | `update → save` |
| Folder | `` `folder/` `` | `.claude/hooks/` |

## Table Format (Multi-Component Entries)

**Required Structure**:
```markdown
| Component | Metric | Type | Impact |
|-----------|--------|------|--------|
| Item 1 | Value | Category | Description |
| **TOTAL** | **Sum** | **Summary** | **Overall** |
```

**Checklist**:
- [ ] Header row with `|`
- [ ] Separator `|---|---|`
- [ ] All rows aligned
- [ ] Bold totals row
- [ ] Consistent column count

## Grouping Guidelines

**Group when**:
- Same date + same area (hooks migration)
- Same date + same category (dead code cleanup)
- Same date + part of larger initiative (token optimization)

**Good (Grouped)**:
```markdown
**Hooks Migration** (2025-11-03)
- Migrated scripts/claude-hooks/ → .claude/hooks/
- Updated paths: config_validator, pre_tool_use
- File protection operational
```

**Bad (Scattered)**:
```markdown
**Hooks Path** (2025-11-03)
- Changed directory

**Config Update** (2025-11-03)
- Updated config

**Pre Tool Fix** (2025-11-03)
- Fixed pre_tool
```

## Quality Checklist by Type

### For Optimizations
- [ ] % or token savings in title
- [ ] Before→after metrics
- [ ] Technique/approach mentioned
- [ ] Impact quantified (per session, % of budget)
- [ ] Table format if multi-component

### For Features
- [ ] Scope quantified (N items)
- [ ] Key mechanism (1 line)
- [ ] Files/locations
- [ ] Usage model if relevant

### For Fixes
- [ ] Problem stated (1 line)
- [ ] Solution (1 line)
- [ ] Files with :line numbers
- [ ] Verification result

## When to Skip Changelog

**Skip for**:
- Typo fixes in non-code files
- Whitespace/formatting only
- Internal refactors (no external impact)
- Temporary debugging
- WIP commits

**Always include for**:
- User-facing changes
- Performance optimizations
- Bug fixes
- Architecture changes
- Documentation affecting usage
- Breaking changes
- Deprecations

## Pre-Commit Final Check

1. **Read aloud** - Clear and concise?
2. **Scan** - Understand in 5 seconds?
3. **Check metrics** - Numbers present and correct?
4. **Verify files** - Paths accurate?
5. **Run validation** - Commands above pass?
6. **Check length** - <10 lines or justified?
7. **Review grouping** - Could combine entries?
8. **Compare examples** - Matches EXAMPLES.md style?
