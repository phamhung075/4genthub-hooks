# Changelog Entry Templates

Copy-paste templates for common changelog entry types. Replace [PLACEHOLDERS] with actual values.

## Token Optimization

### Multi-Component Table
```markdown
**[NAME] - [TOTAL METRIC]** ([DATE])
| [Component] | [Metric] | [Type] | [Impact] |
|-------------|----------|--------|----------|
| [Component1] | [Number] | [Category] | [Description] |
| [Component2] | [Number] | [Category] | [Description] |
| [Component3] | [Number] | [Category] | [Description] |
| **TOTAL** | **[SUM]** | **[Summary]** | **[% of budget]** |
```
**Example**:
```markdown
**Token Optimization Suite - 21-28k Saved** (2025-11-03)
| Optimization | Savings | Type | Impact |
|--------------|---------|------|--------|
| MCP Descriptions | 10,600 | Startup | 60-70% reduction |
| MinimalSerializer | 6,000-8,000 | Per session | Eliminated echo responses |
| **TOTAL** | **21,720-26,580** | **Per session** | **10.9-13.3% of 200k** |
```

### Single Optimization
```markdown
**[NAME] - [%] Reduction** ([DATE])
- [Action]: [BEFORE] → [AFTER] ([REMOVED], [%])
- [Architecture/Technique]: [APPROACH]
- Impact: ~[TOKEN_RANGE] tokens [per what]
```
**Example**:
```markdown
**Agent Files - 55.7% Reduction** (2025-11-03)
- Rewrote 31 files: 1,878 → 832 lines (1,046 removed, 55.7%)
- Architecture: Metadata only, full prompts via MCP
- Impact: ~2,000-2,500 tokens per agent load
```

### File/Document Optimization
```markdown
**[FILENAME] - [%] Size Reduction** ([DATE])
- Consolidated [BEFORE] ([SIZE/TOKENS]) → [AFTER] ([SIZE/TOKENS])
- Eliminated [WHAT_REMOVED]
- Techniques: [TECHNIQUE1], [TECHNIQUE2], [TECHNIQUE3]
- Result: [% fewer lines], [% quality preserved]
```
**Example**:
```markdown
**CHANGELOG.md - 97.5% Size Reduction** (2025-11-03)
- Consolidated 331 lines (271KB, ~42k tokens) → 170 lines (6.8KB, ~1k tokens)
- Eliminated duplicate sections (### Changed, ### Fixed, ### Analysis)
- Techniques: tables over prose, pattern statements, consolidated redundancy
- Result: 48.6% fewer lines, 100% essential info preserved
```

## Feature Addition

### System/Component
```markdown
**[SYSTEM NAME]** ([DATE])
- [N] [items] ([TYPES_LIST])
- [Key mechanism]: [HOW_IT_WORKS]
- [Technical detail]: [IMPLEMENTATION]
- [Metric]: [BENEFIT_COMPARISON]
```
**Example**:
```markdown
**Agent Management System** (2025-11-03)
- 33 specialized agents (coding, testing, DevOps, security, ML)
- Agent switching via `call_agent()` - load instructions + transform role
- Dynamic tool enforcement from tools array
- Token savings: ~1,200 tokens (70% vs delegation ~4,000)
```

### CLI Tool
```markdown
**[TOOL CATEGORY]** ([DATE])
- `[tool1]` ([mode]) - [DESCRIPTION], [BENEFIT]
- `[tool2]` ([mode]) - [DESCRIPTION], [BENEFIT]
- [Common feature]: [SHARED_CAPABILITY]
```
**Example**:
```markdown
**CLI Tools** (2025-11-03)
- `cclaude` (async) - separate terminals, non-blocking, parallel execution
- `cclaude-wait` (sync) - blocking + JSON results, sequential workflows
- Both support task_id and subtask_id delegation
```

### Skill/Capability
```markdown
**[SKILL TYPE]** ([DATE])
- [Name] skill for [PURPOSE]
- Format: [TECHNICAL_FORMAT]
- Features: [FEATURE1], [FEATURE2], [FEATURE3]
- [Usage model]: [HOW_INVOKED]
```
**Example**:
```markdown
**Agent Skills** (2025-11-03)
- changelog-updater skill for consistent CHANGELOG.md updates
- Format: YAML frontmatter with allowed-tools (Read, Edit, Grep only)
- Features: token optimization, format validation, Keep a Changelog compliance
- Auto-discovery: Claude uses automatically when needed
```

### Documentation System
```markdown
**[SYSTEM NAME]** ([DATE])
- [Structure] with [N] [components] ([CONVENTION])
- [Auto feature1] ([WHAT_IT_DOES])
- [Pattern/Feature2] ([PURPOSE])
- [Pattern/Feature3] ([CAPABILITY])
```
**Example**:
```markdown
**Documentation System** (2025-11-03)
- ai_docs/ with 17 folders (kebab-case enforced)
- Auto-generated index.json (metadata, hashes, timestamps)
- _absolute_docs pattern (file-specific enforcement)
- _obsolete_docs (auto-archival when source deleted)
```

## Bug Fix

### Path/Config Fix
```markdown
**[COMPONENT] [Fix Type]** ([DATE])
- Updated [file] ([OLD_PATH] → [NEW_PATH])
- Fixed [function/method] [WHAT_WAS_WRONG]
- Files: [PATH1:LINES], [PATH2:LINES]
- Result: [WHAT_WORKS_NOW]
```
**Example**:
```markdown
**Hooks Path References** (2025-11-03)
- Updated config_validator.py (scripts/claude-hooks → .claude/hooks)
- Fixed _find_project_root() traversal for new structure
- Files: .claude/hooks/utils/config_validator.py:20,78-83, pre_tool_use.py:50,246
- Result: Hooks load correctly, file protection active
```

### Grouped Fixes
```markdown
**[AREA] & [AREA]** ([DATE])
- [Fix1] via [METHOD]
- [Fix2] ([OLD_PATTERN] → [NEW_PATTERN])
- [Fix3] | [Fix4]
- [Fix5]
```
**Example**:
```markdown
**Repository & Database** (2025-11-03)
- User ID propagation via with_user methods
- Git branch creation (update → save pattern)
- SQLAlchemy session lifecycle | UUID validation
- ORM model alignment with database schema
```

### Test Fixes
```markdown
**[CATEGORY] & [SUBCATEGORY]** ([DATE])
- [Action] [WHAT_WAS_DONE]
- [Structure change]: [NEW_ORGANIZATION]
- Fixed [N]/[TOTAL] [test type] after [TRIGGER]
```
**Example**:
```markdown
**Testing & Code Quality** (2025-11-03)
- Removed duplicate test files
- Organization: unit/, integration/, e2e/, performance/
- Fixed 31/31 unit tests after optimization changes
```

## Architecture Change

### Dead Code Removal
```markdown
**Dead Code Cleanup - [TOTAL] Lines** ([DATE])
- [Component1] ([LINES], [IMPACT_PER_OPERATION])
- [Component2] ([LINES]: [SUBCOMPONENTS_LIST])
- Impact: Prevented [TOKEN_RANGE] per [FREQUENCY]
```
**Example**:
```markdown
**Dead Code Cleanup - 2,430 Lines** (2025-11-03)
- EnrichmentService (566 lines, 500-800 token bloat per operation)
- Hint system (1,864 lines: matrix, post-action, unified, bridge, interceptor)
- Impact: Prevented 4,500-7,000 tokens per session
```

### Principles/Philosophy
```markdown
**[CHANGE CATEGORY]** ([DATE])
- [Principle1] ([REASONING])
- [Principle2] ([IMPLEMENTATION_RULE])
- [Hierarchy/Flow]: [STEP1] → [STEP2] → [STEP3] → [STEP4]
- [Replacement]: [NEW] replaces [OLD]
```
**Example**:
```markdown
**Architecture Changes** (2025-11-03)
- Removed backward compatibility (dev phase = clean breaks)
- ORM = source of truth (update DB to match ORM, never reverse)
- Test hierarchy: Prompt → ORM → Database → Tests → Code
- Dynamic tool enforcement replaces static permissions
```

### System Migration
```markdown
**[SYSTEM] Migration** ([DATE])
- Migrated [OLD_PATH] → [NEW_PATH]
- Updated [SCOPE]: [COMPONENT1], [COMPONENT2], [COMPONENT3]
- [Feature1], [Feature2], [Feature3] operational
```
**Example**:
```markdown
**Hooks System Migration** (2025-11-03)
- Migrated scripts/claude-hooks/ → .claude/hooks/
- Updated paths: config_validator, pre_tool_use, test configs
- File protection, documentation enforcement, session tracking operational
```

## Documentation Update

### Multi-Phase Optimization
```markdown
**[CATEGORY] Optimization** ([DATE])
- Phase [N] ([NAME]): [N] docs, [%], ~[TOKEN_RANGE] tokens
- Phase [N+1] ([NAME]): [N] docs, [%] ([BEFORE]→[AFTER] lines), ~[TOKEN_RANGE] tokens
- Techniques: [TECHNIQUE1] ([%]), [TECHNIQUE2] ([%]), [TECHNIQUE3] ([%])
- Cumulative: ~[TOKEN_RANGE] per session ([%] of [BUDGET])
```
**Example**:
```markdown
**ai_docs Optimization** (2025-11-03)
- Phase 2 (Core): 4 docs, 68-78%, ~16,500-18,500 tokens
- Phase 3 (Dev Guides): 2 docs, 69.8% (4,122→1,209 lines), ~5,800-6,500 tokens
- Techniques: Mermaid→tables (85%), code→patterns (92%), ASCII→tables (81%)
- Cumulative: ~24,630-28,130 per session (10-12% of 200k)
```

## Quick Fill Guide

| Placeholder | What to Fill | Example |
|-------------|--------------|---------|
| `[NAME]` | Feature/component name | Agent Files, MCP Tool Descriptions |
| `[DATE]` | Today in YYYY-MM-DD | 2025-11-03 |
| `[N]` | Count/number | 33, 15, 2,430 |
| `[%]` | Percentage | 55.7%, 97.5% |
| `[BEFORE]` → `[AFTER]` | Before→after comparison | 1,878 → 832, scripts/ → .claude/ |
| `[TOKEN_RANGE]` | Token count or range | 6,000-8,000, ~2,500 |
| `[PATH:LINES]` | File path with line numbers | config_validator.py:20,78-83 |
| `[OLD] → [NEW]` | Change description | update → save, prose → tables |

## Section Quick Reference

| Change Type | Section | Template to Use |
|-------------|---------|-----------------|
| New optimization | ### Changed | Token Optimization templates |
| New feature/tool/system | ### Added | Feature Addition templates |
| Bug fix/correction | ### Fixed | Bug Fix templates |
| Architecture change | ### Changed | Architecture Change templates |
| Documentation work | ### Added or ### Changed | Documentation Update templates |
