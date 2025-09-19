# agenthub Project - Local AI Agent Rules
DATABASE agenthub
rolname = 'agenthub_user'

## About This File
This file (`CLAUDE.local.md`) contains **local, environment-specific rules** for AI agents working on this project. It is NOT checked into version control and complements the main `CLAUDE.md` file.

- **CLAUDE.md**: Main AI agent instructions (checked into repository, shared across team)
- **CLAUDE.local.md**: Local environment rules and overrides (NOT checked in, local only)


## Core Project Structure
**Source Code Paths:**
<ai must update later>


### Security Guidelines (Local Environment)
- **Credentials**: NEVER expose passwords - all stored in `.env` file only
- **Environment Variables**: Access secrets via environment variables only


## Documentation Architecture

### AI Documentation System Overview
The documentation system provides intelligent tracking, automatic indexing, and selective enforcement to help AI agents maintain high-quality documentation while not disrupting workflow.

```
ai_docs/
├── _absolute_docs/           # File-specific documentation (marks importance)
│   ├── scripts/             # Documentation for scripts folder
│   │   ├── f_index.md       # Folder documentation (marks folder as important)
│   │   └── docker-menu.sh.md # Specific file documentation
│   └── claude-hooks-pre-tool-use.py.md  # Hook documentation
├── _obsolete_docs/          # Auto-archived when source files deleted
├── index.json               # Auto-generated documentation index (by hooks)
├── api-integration/         # API documentation
├── authentication/          # Auth system documentation
├── claude-code/             # Claude Code specific docs
├── context-system/          # Context management docs
├── core-architecture/       # System architecture (kebab-case)
├── development-guides/      # Developer resources (kebab-case)
├── issues/                  # Issue tracking and resolution
├── keycloak/                # Keycloak integration docs
├── migration-guides/        # Version migration guides
├── operations/              # Deployment & configuration
├── reports-status/          # Status reports and analysis
├── setup-guides/            # Setup and configuration
├── testing-qa/              # Testing documentation
└── troubleshooting-guides/ # Problem resolution (kebab-case)
```
<ai must update later>

### Key Features for AI Agents

#### 1. Fast Context Access
- **index.json**: Machine-readable index with all documentation metadata
- **Automatic updates**: Hooks update index.json when docs change
- **Quick lookup**: AI can quickly find relevant documentation via index
- **MD5 hashing**: Track document changes and versions

#### 2. Selective Documentation Enforcement
- **_absolute_docs pattern**: Files with docs here are marked as "important"
- **Smart blocking**: Only blocks modifications if documentation exists
- **Session tracking**: 2-hour sessions prevent workflow disruption
- **f_index.md**: Mark entire folders as important with folder documentation

#### 3. Automatic Documentation Management
- **Post-tool hook**: Updates index.json after any ai_docs changes
- **Obsolete tracking**: Moves docs to _obsolete_docs when source deleted
- **Warning system**: Non-blocking warnings for missing documentation
- **Path mapping**: `ai_docs/_absolute_docs/{path}/file.ext.md` for `/path/file.ext`

### Documentation Structure Rules
- **Test files**: Must write in correct location (`agenthub_main/src/tests/`)
- **Document files**: Must write in correct location (`ai_docs/`)
- **Kebab-case folders**: All ai_docs subfolders must use lowercase-with-dashes
- **Organization**: Create subfolders for easy management
- **Index files**: Auto-generated index.json (not index.md anymore)
- **NO LOOSE DOCUMENTATION IN ROOT**: All documentation MUST be in appropriate folders:
  - Troubleshooting guides → `ai_docs/troubleshooting-guides/`
  - Migration guides → `ai_docs/migration-guides/`
  - Issue documentation → `ai_docs/issues/`
  - Reports & status → `ai_docs/reports-status/`
  - Operations guides → `ai_docs/operations/`
  - **ONLY 5 .md FILES ALLOWED IN PROJECT ROOT**: 
    - README.md (project overview)
    - CHANGELOG.md (project-wide changes)
    - TEST-CHANGELOG.md (tests changes)
    - CLAUDE.md (AI agent instructions - checked in)
    - CLAUDE.local.md (local AI rules - not checked in)

### How AI Should Use Documentation System

1. **Check index.json for existing docs**:
   - Located at `ai_docs/index.json`
   - Contains all documentation with metadata
   - Use to quickly find relevant documentation

2. **Create absolute documentation for important files**:
   - Place in `ai_docs/_absolute_docs/` with path structure
   - This marks the file as important and requires doc updates
   - Example: For `scripts/test.sh` → `ai_docs/_absolute_docs/scripts/test.sh.md`

3. **Follow kebab-case for all folders**:
   - Valid: `api-integration`, `test-results`, `setup-guides`
   - Invalid: `API_Integration`, `Test Results`, `SetupGuides`

4. **Respect session tracking**:
   - First modification might trigger warning
   - Subsequent modifications in same session won't be blocked
   - Sessions last 2 hours for uninterrupted work

## Essential Rules

### 🚨 CRITICAL: Changelog Updates
**MANDATORY**: AI agents MUST update CHANGELOG.md when making ANY project changes:
- Add new features under `### Added`
- Document fixes under `### Fixed`
- Note breaking changes under `### Changed`
- Follow [Keep a Changelog](https://keepachangelog.com/) format
- Include file paths modified/created
- Describe impact and testing performed


### Documentation & Changelog Rules
- Check `ai_docs/index.md` first for structure
- **MANDATORY**: Update CHANGELOG.md for ALL project changes
- **CHANGELOG LOCATION RULES**:
  - **Use ONLY ONE CHANGELOG.md in project root** (`./CHANGELOG.md`)
  - **NEVER create CHANGELOG.md in subdirectories** (except frontend has its own for frontend-specific changes)
  - All project-wide changes go in root CHANGELOG.md
  - CHANGELOG.md is the official project changelog (checked into repository)
  - CLAUDE.local.md is for local AI agent rules and instructions only
  - Never add version history or change logs to CLAUDE.local.md

### Recent Changes
**Note**: All changelog entries have been moved to the main CHANGELOG.md file where they belong.
See CHANGELOG.md for version history and recent changes.

### Testing
- Location: <demande user where create tests files>
- Categories: unit/, integration/, e2e/, performance/
- Run tests before committing changes
- Write tests for new features

## System Behaviors
<ai add here when working>

## Quick Reference
1. **UPDATE CHANGELOG.md for ALL project changes (NOT CLAUDE.local.md)**
2. Check existing ai_docs structure before creating files
3. Follow DDD patterns in codebase
4. Test code examples before documentation
5. Use Docker menu: `docker-system/docker-menu.sh`
6. CLAUDE.local.md is for AI rules only, not for changelog entries
7. Refer to CLAUDE.md for comprehensive Vision System documentation

## Important Notes
- **ALWAYS** remove backward or legacy code on working, update to last version code -> CLEAN code
- **NEVER** create files unless absolutely necessary
- **NEVER** create test files, scripts for test or debug, document on root project
- **ALWAYS** prefer editing existing files over creating new ones
- **NEVER** proactively create documentation unless explicitly requested

- **TEST-CHANGELOG.md Updates**: AI agents MUST update TEST-CHANGELOG.md when making changes to test files. Document all test additions, modifications, or fixes in TEST-CHANGELOG.md (located in project root). This rule belongs in CLAUDE.local.md, NOT in CLAUDE.md.
- Use the Task tool to launch the Claude Code troubleshooter agent

## Git Commit Guidelines

Follow [Conventional Commits 1.0.0](https://conventionalcommits.org/) specification:

**Format**: `<type>[optional scope]: <description>`

**Common Types**:
- `feat:` - New feature
- `fix:` - Bug fix  
- `ai_docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc)
- `refactor:` - Code refactoring
- `test:` - Adding/updating tests
- `chore:` - Maintenance tasks

**Examples**:
- `feat(auth): add JWT token validation`
- `fix(ui): resolve login form validation error`
- `ai_docs: update API documentation`
- `test: add unit tests for context management`

### Hook System Files
Located in `.claude/hooks/`

## Important Instruction Reminders
- Do what has been asked; nothing more, nothing less
- **NEVER** create files unless absolutely necessary
- **ALWAYS** prefer editing existing files over creating new ones  
- **NEVER** proactively create documentation unless explicitly requested
- **NEVER** create test files, scripts for test or debug, document on root project
- **ALWAYS** remove backward or legacy code when working, update to latest version code → CLEAN code
- docker-menu.sh option R for rebuild to view code changes in dev mode, need start docker posgresql for have data dev
- Use the Task tool to launch specialized agents when appropriate