---
allowed-tools: Bash, Read, Write, Glob
description: Auto-generate project-specific CLAUDE.local.md by analyzing codebase structure and architecture
---

# Generate Local Rules

Generate a customized `CLAUDE.local.md` file tailored to this specific project's architecture, tech stack, and conventions.

**How This Works:**
1. Read the nested template from `.claude/templates/claude-rules/RULE_CLAUDECODE__copy-to-root-project-rename-to:CLAUDE.local.md`
2. Analyze the current project to detect structure, tech stack, paths, ports
3. Replace ALL placeholders `{like-this}` and `{auto-generate-...}` with actual detected values
4. Write the fully customized file to project root as `CLAUDE.local.md`

**Critical:** The template is a NESTED TEMPLATE with placeholders. You MUST replace every `{placeholder}` with real project-specific data. Do NOT copy the template as-is.

## Phase 1: Project Structure Analysis

### Execute Commands
Run these commands to understand the project:

```bash
# Project root structure
ls -la

# Find all package managers and config files
find . -maxdepth 2 -type f \( -name "package.json" -o -name "requirements.txt" -o -name "pyproject.toml" -o -name "Cargo.toml" -o -name "pom.xml" -o -name "build.gradle" -o -name "go.mod" \) 2>/dev/null

# Find test directories
find . -type d \( -name "tests" -o -name "test" -o -name "__tests__" -o -name "spec" \) 2>/dev/null | head -20

# Check for Docker
ls -la docker* 2>/dev/null || echo "No Docker files"

# Check for monorepo/nested structure
find . -maxdepth 2 -type d \( -name "frontend" -o -name "backend" -o -name "api" -o -name "apps" -o -name "packages" -o -name "services" \) 2>/dev/null
```

### Read Key Files
Read these files if they exist:
- `README.md` - Project overview
- `package.json` - Node.js dependencies
- `requirements.txt` or `pyproject.toml` - Python dependencies
- `.gitignore` - What's excluded from version control
- `docker-compose.yml` - Service architecture
- Any existing `CLAUDE.md` or `CLAUDE.local.md` - Current rules

## Phase 2: Pattern Detection

Analyze the findings and determine:

1. **Project Type**
   - [ ] Monorepo (multiple packages/apps in one repo)
   - [ ] Single application
   - [ ] Frontend only
   - [ ] Backend only
   - [ ] Full-stack (frontend + backend)
   - [ ] Microservices
   - [ ] Library/Package

2. **Technology Stack**
   - Frontend: React, Vue, Angular, Svelte, Next.js, etc.
   - Backend: Node.js, Python (Django/Flask/FastAPI), Go, Rust, Java, etc.
   - Database: PostgreSQL, MySQL, MongoDB, SQLite, etc.
   - Container: Docker, Kubernetes
   - Build tools: Webpack, Vite, esbuild, etc.

3. **Directory Structure Pattern**
   - Flat (all in root)
   - Domain-driven (features/modules)
   - Layered (controller/service/repository)
   - Nested projects (apps/, packages/)

4. **Testing Setup**
   - Test framework: Jest, Pytest, Go test, etc.
   - Test locations: tests/, __tests__, src/tests/
   - Test types: unit, integration, e2e

5. **Special Constraints**
   - Build process requirements
   - Environment variables usage
   - Docker workflow
   - Database migrations

## Phase 3: Generate CLAUDE.local.md

### Step 1: Read the Template

First, read the nested template:
```bash
cat .claude/templates/claude-rules/RULE_CLAUDECODE__copy-to-root-project-rename-to:CLAUDE.local.md
```

This template contains placeholders marked with `{curly-braces}` and instructions in `{auto-generate-...}` format.

### Step 2: Replace All Placeholders

Go through the template and replace EVERY placeholder with actual detected values:

**Title Section:**
- `{Project Name}` → Actual project name from package.json, README.md, or directory name
- `{auto-generate-based-on-package.json-scripts-or-Makefile}` → Actual commands found
- `{auto-generate-based-on-detected-architecture-patterns}` → Real architectural patterns detected

**System Architecture:**
- `{auto-generate-table-rows-based-on-project-structure}` → Actual table rows with real paths
- `{auto-generate-based-on-package-managers-and-dependencies}` → Technology stack table
- `{auto-generate-based-on-docker-compose-ports-and-package-json-scripts}` → Real URLs and paths

**Example Replacements:**
```markdown
# Before (template):
| Path | Purpose | Technology |
|------|---------|------------|
{auto-generate-table-rows-based-on-project-structure}

# After (generated):
| Path | Purpose | Technology |
|------|---------|------------|
| `agenthub-frontend/` | React frontend | React 19 + TypeScript + Vite |
| `agenthub_main/src/` | Python backend | FastAPI + DDD + SQLAlchemy |
| `docker-system/` | Docker configs | PostgreSQL 18 + Redis |
```

### Step 3: Handle Conditional Sections

For sections with `{if-condition-...}` format:
- IF condition is true → Generate the section with real data
- IF condition is false → Remove the entire section

**Example:**
```markdown
# Template:
{if-monorepo-describe-multiple-changelogs-else-single-root-changelog}

# IF monorepo detected:
- **Root CHANGELOG.md**: Project-wide changes affecting all packages
- **frontend/CHANGELOG.md**: Frontend-specific changes
- **backend/CHANGELOG.md**: Backend-specific changes

# ELSE (single app):
- **Root CHANGELOG.md**: All project changes go here
```

### Step 4: Generate Project-Specific Content

For each `{auto-generate-...}` placeholder:
1. Run the appropriate detection commands from Phase 1
2. Analyze the output
3. Generate specific, actionable content
4. Replace the placeholder

**Do NOT leave any `{placeholders}` or `{auto-generate-...}` instructions in the final file.**

## Phase 4: Customization Rules

When generating content:

1. **Be Specific, Not Generic**
   - Replace `{placeholders}` with actual detected values
   - Include real paths, commands, ports found in the project
   - Reference actual files that exist

2. **Omit What Doesn't Apply**
   - If no Docker → skip Docker sections
   - If single app → skip monorepo sections
   - If no tests found → note this as a warning

3. **Include Helpful Warnings**
   - Missing test directories
   - No CHANGELOG.md found
   - Inconsistent naming patterns
   - Multiple package managers detected

4. **Add Project-Specific Insights**
   - Common gotchas for the detected framework
   - Build process requirements
   - Environment setup notes
   - Database migration workflows (if detected)

5. **Token Optimization**
   - Use tables over prose
   - Use bullets for lists
   - Keep examples concrete and brief
   - Remove fluff, keep actionable info

## Phase 5: Validation

After generating:

1. Verify the file was created at project root
2. Check all placeholders were replaced
3. Ensure all detected paths are accurate
4. Confirm sections match actual project structure
5. Ask user if they want any customizations

## Output

Present to user:
1. Summary of what was detected
2. Path to generated file
3. Key sections included
4. Any warnings or recommendations
5. Prompt to review and customize further

**Do NOT ask permission before generating - just do it intelligently based on analysis.**
