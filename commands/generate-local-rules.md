---
allowed-tools: Bash, Read, Write, Glob
description: Auto-generate CLAUDE.local.md from template + project analysis
---

# Generate Local Rules

**Purpose**: Create customized `CLAUDE.local.md` from nested template

⚠️ **Critical**: Template has `{placeholders}` - replace ALL with real values

## Phase 1: Analyze Project

| Command | Purpose |
|---------|---------|
| `ls -la` | Root structure |
| `find . -maxdepth 2 -type f \( -name "package.json" -o -name "requirements.txt" ... \)` | Package managers |
| `find . -type d \( -name "tests" -o -name "__tests__" ... \)` | Test directories |
| `ls -la docker*` | Docker files |
| `find . -maxdepth 2 -type d \( -name "frontend" -o -name "backend" ... \)` | Monorepo/nested |

**Read**: README.md, package.json, requirements.txt, .gitignore, docker-compose.yml, CLAUDE.md

## Phase 2: Detect Patterns

| Pattern | Options |
|---------|---------|
| Project Type | Monorepo / Single app / Frontend-only / Backend-only / Full-stack / Microservices / Library |
| Tech Stack | Frontend: React/Vue/Angular/Next.js, Backend: Node/Python/Go/Rust, DB: PostgreSQL/MySQL/MongoDB |
| Structure | Flat / Domain-driven / Layered / Nested projects |
| Testing | Framework: Jest/Pytest/Go test, Locations: tests/__tests__/src/tests, Types: unit/integration/e2e |

## Phase 3: Replace Placeholders

**Read Template**: `.claude/templates/claude-rules/RULE_CLAUDECODE__copy-to-root-project-rename-to:CLAUDE.local.md`

**Replace ALL** `{placeholders}` and `{auto-generate-...}` with detected values:
- `{Project Name}` → Actual name from package.json/README
- `{auto-generate-based-on-package.json-scripts}` → Real commands
- `{auto-generate-table-rows-based-on-project-structure}` → Actual paths table
- Conditionals: `{if-monorepo-...}` → Generate or remove section

## Phase 4: Validation
1. Verify file created at root
2. Check all placeholders replaced
3. Ensure paths accurate
4. Confirm sections match structure
5. Ask user for customizations

**Custom Instructions**: $ARGUMENTS
