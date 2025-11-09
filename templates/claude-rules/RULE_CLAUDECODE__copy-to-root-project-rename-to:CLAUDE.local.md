# {Project Name} - Local AI Agent Rules

## About This File
This file (`CLAUDE.local.md`) contains **local, environment-specific rules** for AI agents working on this project. It is NOT checked into version control and complements the main `CLAUDE.md` file.

| File | Purpose | Version Control |
|------|---------|----------------|
| **CLAUDE.md** | Main AI agent instructions (shared across team) | ✅ Checked in |
| **CLAUDE.local.md** | Local environment rules and overrides | ❌ NOT checked in |

**Quick Dev Commands:**
{auto-generate-based-on-package.json-scripts-or-Makefile}

**Critical Principles:**
{auto-generate-based-on-detected-architecture-patterns}

---

## 🏗️ System Architecture

### Project Structure
| Path | Purpose | Technology |
|------|---------|------------|
{auto-generate-table-rows-based-on-project-structure}

### Technology Stack
| Component | Technology | Details |
|-----------|-----------|---------|
{auto-generate-based-on-package-managers-and-dependencies}

### Local URLs & Paths
{auto-generate-based-on-docker-compose-ports-and-package-json-scripts}

---

## 📚 Documentation Architecture

### Core Principle
> **AI documentation should be curated, not cluttered.** Every document must provide clear value - teaching architecture, solving problems, or guiding decisions. Anything else degrades AI performance.

### ai_docs Structure (17 Standard Folders)
{if-ai_docs-exists-list-actual-folders-else-show-standard-structure}

```
ai_docs/
├── _absolute_docs/          # File-specific docs (marks importance)
├── _obsolete_docs/          # Auto-archived when source deleted
├── index.json               # Auto-generated index (by hooks)
{auto-generate-additional-folders-found-in-project}
```

### Key Features for AI Agents

**1. Fast Context Access**
- **index.json**: Machine-readable index with metadata, hashes, timestamps
- **Automatic updates**: Hooks update index.json when docs change
- **Quick lookup**: Find relevant documentation via index

**2. Selective Documentation Enforcement**
- **_absolute_docs pattern**: `ai_docs/_absolute_docs/path/to/file.ext.md` documents `/path/to/file.ext`
- **Smart blocking**: Only blocks modifications if documentation exists
- **Session tracking**: 2-hour sessions prevent workflow disruption
- **f_index.md**: Mark entire folders as important

**3. Automatic Management**
- **Post-tool hook**: Updates index.json after ai_docs changes
- **Obsolete tracking**: Moves docs to _obsolete_docs when source deleted
- **Warning system**: Non-blocking warnings for missing documentation

### Documentation Rules

| Rule | Description |
|------|-------------|
| **Test files** | Must be in `{detected-test-paths}` only |
| **Document files** | Must be in `ai_docs/` (except 5 allowed root files) |
| **Kebab-case folders** | All ai_docs subfolders use lowercase-with-dashes |
| **Root .md files** | ONLY 5 allowed: README.md, CHANGELOG.md, TEST-CHANGELOG.md, CLAUDE.md, CLAUDE.local.md |
| **Index files** | Auto-generated index.json (not index.md) |

---

## 🔒 Essential Rules & File System Protection

### Changelog Updates (CRITICAL)
**MANDATORY**: AI agents MUST update CHANGELOG.md when making ANY project changes
- Add new features → `### Added`
- Document fixes → `### Fixed`
- Breaking changes → `### Changed`
- Follow [Keep a Changelog](https://keepachangelog.com/) format
- Include file paths modified/created
- Describe impact and testing performed

**CHANGELOG LOCATION RULES**:
{if-monorepo-describe-multiple-changelogs-else-single-root-changelog}

### Context Management
{if-mcp-detected-add-context-guidelines}

### Database Modes
{if-database-detected-describe-local-test-production-modes}

### File System Protection (Auto-Enforced by Hooks)

#### Root Directory Restrictions
- **NO file creation in root** (except files in `.allowed_root_files`)
- **NO folder creation in root** (all folders should already exist)
- **Allowed root files**: {auto-detect-current-root-files-and-list}

#### File Type Restrictions
| File Type | Allowed Location | Notes |
|-----------|-----------------|-------|
| **.md files** | `ai_docs/` | Except 5 allowed root files |
| **Test files** | {detected-test-directories} | {detected-test-framework} |
| **{other-restrictions}** | {detected-locations} | {notes} |

#### ai_docs Folder Rules
- **Kebab-case required**: lowercase-with-dashes (e.g., `api-integration`, `setup-guides`)
- **Exempt folders**: `_absolute_docs`, `_obsolete_docs` (can use underscores)
- **NO uppercase folders** (except legacy being migrated)

### Hook System Files (Auto-Enforcement)
Located in `.claude/hooks/`:
- **pre_tool_use.py**: Enforces file system protection rules
- **post_tool_use.py**: Updates documentation index
- **utils/session_tracker.py**: Manages 2-hour work sessions
- **utils/docs_indexer.py**: Generates/maintains index.json

### Configuration Files
- **.allowed_root_files**: Files allowed in project root
- **.valid_test_paths**: Directories where test files can be created

---

## 💻 Git Commit Guidelines

Follow [Conventional Commits 1.0.0](https://www.conventionalcommits.org/):

**Format**: `<type>[optional scope]: <description>`

| Type | Purpose | Example |
|------|---------|---------|
| `feat:` | New feature | `feat(auth): add JWT token validation` |
| `fix:` | Bug fix | `fix(ui): resolve login form validation error` |
| `ai_docs:` | Documentation | `ai_docs: update API documentation` |
| `style:` | Code style | `style(frontend): format components` |
| `refactor:` | Code refactoring | `refactor(backend): simplify auth flow` |
| `test:` | Tests | `test: add unit tests for context management` |
| `chore:` | Maintenance | `chore: update dependencies` |

---

## 🎯 AI Workflow Best Practices

### MANDATORY Behaviors
1. ✅ **UPDATE CHANGELOG.md** for ALL project changes (NOT CLAUDE.local.md)
2. ✅ **CHECK ai_docs/index.json** for existing documentation before creating
{auto-generate-additional-mandatory-behaviors-based-on-project}

### NEVER Do
- ❌ Create files unless absolutely necessary
- ❌ Create test files, scripts, or documents in project root
- ❌ Proactively create documentation (only when requested)
- ❌ Add backward/legacy code (ALWAYS clean code)
- ❌ Add changelog entries to CLAUDE.local.md
{auto-generate-additional-anti-patterns-based-on-project}

### Quick Reference Commands
{auto-generate-based-on-package-json-scripts-Makefile-docker-menu}

---

## 📋 System Behaviors & Gotchas
{auto-generate-based-on-detected-frameworks}

---

## 🔗 Additional Resources

{if-primary-docs-exist-list-them}

---

## 🎓 Important Notes

**This is a TEMPLATE file.** To generate a project-specific CLAUDE.local.md:

1. Run the command: `/generate-local-rules` or `/init-local`
2. The AI will analyze your project structure
3. A customized CLAUDE.local.md will be created with:
   - Actual paths from YOUR project
   - Detected technology stack
   - Real ports and URLs
   - Project-specific rules and conventions

**Do NOT manually edit this template.** The `/generate-local-rules` command will create a proper CLAUDE.local.md for you.
