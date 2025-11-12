# .claude Automated Setup Guide

Quick and easy configuration for Claude Code and OpenAI Codex across different projects and PCs.

## 📋 Prerequisites

- **Python 3.14** (recommended) or 3.8+
- **Git** (for submodule management - recommended)

## 🚀 Quick Start

### Step 1: Add .claude to Your Project (RECOMMENDED: Submodule)

```bash
# Navigate to your project
cd your-project

# Add as git submodule - enables easy updates across ALL projects!
## SSH
git submodule add git@github.com:phamhung075/4genthub-hooks.git .claude

## Https
git submodule add https://github.com/phamhung075/4genthub-hooks.git .claude

# Initialize
git submodule update --init --recursive
cd .claude && git checkout main && cd ..

# Commit
git add .gitmodules .claude
git commit -m "Add 4genthub-hooks as .claude submodule"
```

**Why Submodule?**
- ✅ Update all projects: `git submodule update --remote .claude`
- ✅ Works in ANY nested project structure (paths auto-detected)
- ✅ Version control for hooks - track what version each project uses

### Step 2: Run Automated Setup

```bash
# From project root
python .claude/setup.py

# Or
python3 .claude/setup.py
```

**What it does:**
1. ✅ Auto-detects Python path (pyenv, virtualenv, system)
2. ✅ Asks which AI tool you're using (Claude Code/Codex/Both)
3. ✅ Asks token optimization strategy (Economic/Performance)
4. ✅ Asks virtual environment preference (recommended)
5. ✅ **Prompts for MCP API token from https://www.4genthub.com/**
6. ✅ Creates virtual environment
7. ✅ Installs hook dependencies (pyyaml, python-dotenv, psutil, requests)
8. ✅ Generates `settings.json` with correct paths
9. ✅ Creates config files from templates
10. ✅ Deploys rules files to project root (CLAUDE.md, CLAUDE.local.md)
11. ✅ Deploys `.env.claude` for environment variables
12. ✅ Deploys `.mcp.json` **with your token pre-configured**
13. ✅ Verifies hooks are executable
14. ✅ Validates entire setup

**Time: < 2 minutes** ⚡

### Step 3: Start Using Claude Code!

That's it! The setup wizard handles everything automatically, including:
- ✅ MCP API token configuration (no manual editing needed)
- ✅ Dependency installation
- ✅ Virtual environment creation
- ✅ All configuration files

**🔑 About the MCP API Token:**

During setup, you'll be prompted to enter your **4genthub.com API token**:

1. The wizard will show you: **https://www.4genthub.com/**
2. Visit the site and create an account
3. Navigate to **Account Settings** → **API Keys**
4. Generate a new API token
5. Copy and paste it into the setup wizard
6. The token is **automatically injected** into `.mcp.json`
7. You can press **Enter to skip** and configure later

**⚠️ Security:**
- ✅ `.mcp.json` is automatically added to `.gitignore`
- ✅ Your token is never committed to version control
- ✅ Token enables MCP features (task management, agent coordination)

---

## 📋 What Gets Configured

### 1. `.claude/settings.json`
- Python interpreter path (9 locations updated automatically)
- Hook commands
- Permissions (allow/deny patterns)
- Environment variables

### 2. Configuration Files
- `__claude_hook__allowed_root_files` - Files allowed in root
- `__claude_hook__valid_test_paths` - Where tests can be created

### 3. Rules Files (Project Root)

| AI Tool | Files Deployed |
|---------|----------------|
| Claude Code | `CLAUDE.md`, `CLAUDE.local.md` |
| Codex | `AGENTS.md` |
| Both | All of the above |

### 4. Environment Configuration
- `.env.claude` - Claude Code environment variables (copied from `.env.claude.sample`)

### 5. MCP Server Configuration
- `.mcp.json` - Model Context Protocol servers configuration
  - **agenthub_http** - 4genthub.com MCP server for task management
  - **sequential-thinking** - Enhanced reasoning capabilities
  - **shadcn-ui-server** - UI component integration
  - **browsermcp** - Browser automation
  - **Requires:** API token from https://www.4genthub.com/
  - **Security:** Automatically added to `.gitignore`

### 6. Git Configuration
- `.gitignore` - Automatically updated with recommended patterns:
  - `.mcp.json` - MCP configuration with API secrets
  - `.claude/settings.json` - Local settings with machine-specific paths
  - `.env.claude` - Environment variables
  - `logs/` and `logs/**` - Log files and directories

---

## 🔄 Migrating to New Project/PC

### Option 1: Copy & Re-configure

```bash
# Copy .claude directory
cp -r /old/project/.claude /new/project/

# Update paths for new environment
cd /new/project
python .claude/setup.py
```

### Option 2: Git Clone

```bash
git clone <repository>
cd <project>
python .claude/setup.py
```

Setup is **idempotent** - safe to run multiple times!

---

## 🛠️ Advanced: Manual Configuration

If you prefer manual setup, edit these files:

### settings.json
Replace hardcoded Python paths (9 locations):
```json
{
  "statusLine": {
    "command": "/your/python/path ..."
  },
  "hooks": {
    "PreToolUse": [{
      "hooks": [{
        "command": "/your/python/path .claude/hooks/pre_tool_use.py"
      }]
    }],
    // ... 7 more locations
  }
}
```

### Config Files
Copy and customize:
```bash
cp .claude/hooks/config/__claude_hook__allowed_root_files.sample \
   .claude/hooks/config/__claude_hook__allowed_root_files

cp .claude/hooks/config/__claude_hook__valid_test_paths.sample \
   .claude/hooks/config/__claude_hook__valid_test_paths
```

### Rules Files
Copy based on your AI tool:
```bash
# Claude Code
cp .claude/hooks/claude-rules/RULE_CLAUDECODE*.md CLAUDE.md
cp .claude/hooks/claude-rules/*local.md CLAUDE.local.md

# Codex
cp .claude/hooks/codex-rules/AGENTS.md AGENTS.md
```

---

## 🔍 Troubleshooting

### Python Not Found

```bash
# Find Python manually
which python3
pyenv which python3
which python

# Then enter path when setup prompts
```

### Setup Script Not Running

```bash
chmod +x .claude/setup.py
```

### Hooks Not Executing

```bash
# Check permissions
chmod +x .claude/hooks/*.py

# Verify Python path
cat .claude/settings.json | grep python
```

### Re-run Setup

```bash
# Safe to run anytime
python .claude/setup.py
```

### MCP Token Issues

```bash
# Verify .mcp.json exists
ls -la .mcp.json

# Check token is configured
cat .mcp.json | grep "Bearer"

# Should NOT show: <YOUR_API_TOKEN_HERE>
# Should show: Bearer eyJhbGc... (your actual token)
```

**Common Issues:**
- ❌ Forgot to replace `<YOUR_API_TOKEN_HERE>` → Edit `.mcp.json`
- ❌ Token expired → Generate new token at https://www.4genthub.com/
- ❌ `.mcp.json` missing → Run `python .claude/setup.py` to deploy
- ❌ 401 Unauthorized errors → Check token is valid and properly formatted

---

## 📁 File Structure

```
project-root/
├── .mcp.json                   # 🔑 MCP servers + API token
├── CLAUDE.md                   # 📋 AI rules (from setup)
├── CLAUDE.local.md             # 📋 Local overrides (from setup)
├── .env.claude                 # 🔧 Environment variables (from setup)
└── .claude/
    ├── setup.py                # 🚀 Run this
    ├── SETUP.md                # 📖 This file
    ├── README.md               # Full documentation
    ├── settings.json           # Generated config
    ├── .venv/                  # Virtual environment
    ├── templates/
    │   ├── settings.json.template
    │   └── .mcp.json.sample    # MCP template
    └── hooks/
        ├── *.py                # Hook scripts
        ├── config/
        │   ├── __claude_hook__allowed_root_files
        │   └── __claude_hook__valid_test_paths
        ├── claude-rules/       # Claude Code rules
        └── codex-rules/        # Codex rules
```

---

## ✨ Features

- **Auto-detection**: Finds Python path using 5 different methods
- **Interactive**: Clear prompts with defaults
- **Idempotent**: Safe to re-run anytime
- **Validated**: Checks JSON syntax and file existence
- **Cross-platform**: Linux, Mac, Windows
- **Project-aware**: Detects test directories automatically

---

## 📝 Example Session

```
╔════════════════════════════════════════════╗
║   .claude Configuration Setup Wizard      ║
╚════════════════════════════════════════════╝

Project root: /home/user/projects/myapp

Detecting Python path...
  ✓ Found via pyenv shims: /home/user/.pyenv/shims/python3

Python path detected: /home/user/.pyenv/shims/python3
Use this path? [Y/n]: y

Which AI coding tool are you using?
  [1] Claude Code (Anthropic)
  [2] OpenAI Codex
  [3] Both

Choice [1-3]: 1

Token Optimization Strategy:
  [1] Economic (Balanced - saves tokens, good performance)
  [2] Max Performance (Token burn — maximum context)

  Recommendation: Use Economic for most projects

Choice [1-2, default: 1]: 1

Python Environment for Hooks:
  [1] Virtual Environment (Recommended - isolated dependencies)
  [2] System Python (Use existing Python installation)

  Recommendation: Use virtual environment for better isolation

Choice [1-2, default: 1]: 1

MCP API Token Configuration:
  ℹ  MCP (Model Context Protocol) enables advanced features like:
     • Task management and tracking
     • Agent coordination
     • Sequential thinking
     • Enhanced context handling

  📍 Get your API token:
     1. Visit: https://www.4genthub.com/
     2. Create an account or log in
     3. Navigate to Account Settings → API Keys
     4. Generate a new API token
     5. Copy and paste it below

  ℹ  You can skip this and configure later by editing .mcp.json

Enter your 4genthub.com API token
  (Press Enter to skip and configure later):

API Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0...

  Token preview: eyJhbGciOiJIUzI1N...yJzdWIiOi
  Use this token? [Y/n]: y

Creating virtual environment...
  Creating venv at: .claude/.venv
  ✓ Created: .claude/.venv
  ✓ Updated Python path to venv: .claude/.venv/bin/python3

Installing hook dependencies...
  Using pyproject.toml for dependency management
  Installing core dependencies...
  ✓ Installed core: python-dotenv, psutil, pyyaml, requests
  Installing optional dependencies...
  ✓ Installed optional: colorama, rich, GitPython

Generating settings.json...
  ✓ Created: .claude/settings.json

Setting up configuration files...
  ✓ Created: __claude_hook__allowed_root_files
  ✓ Created: __claude_hook__valid_test_paths

  Detected test directories:
    - tests
    - src/tests
  Consider adding these to __claude_hook__valid_test_paths

Deploying rules files...
  ✓ Deployed: CLAUDE.md
  ✓ Deployed: CLAUDE.local.md

Deploying environment configuration...
  ✓ Deployed: .env.claude
  ℹ  Edit .env.claude to configure Claude Code environment variables

Deploying MCP configuration...
  ✓ Deployed: .mcp.json
  ✓ Configured: API token set for agenthub_http
  ✓ Updated .gitignore (.mcp.json, .claude/settings.json, .env.claude, logs/**)

Verifying hook functionality...
  ✓ Hook verification passed!

Validating setup...
  ✓ settings.json
  ✓ allowed_root_files config
  ✓ valid_test_paths config
  ✓ Python path configured correctly

╔════════════════════════════════════════════╗
║       Configuration Summary                ║
╚════════════════════════════════════════════╝

  Python Environment   /home/user/.pyenv/shims/python3
  AI Tool              Claude
  Token Strategy       Economic
  Virtual Environment  ✓ Created at .claude/.venv
  Dependencies         ✓ Installed (python-dotenv, psutil, pyyaml, requests, colorama, rich, GitPython)
  settings.json        ✓ Generated with hook configurations
  Config Files         ✓ Created (__claude_hook__allowed_root_files, __claude_hook__valid_test_paths)
  Rules Files          ✓ Deployed (CLAUDE.md, CLAUDE.local.md)
  .env.claude          ✓ Deployed
  MCP Configuration    ✓ Token configured in .mcp.json
  .gitignore           ✓ Updated (.mcp.json, .claude/settings.json, .env.claude, logs/**)
  Hooks                ✓ Verified and functional

╔════════════════════════════════════════════╗
║          Setup Complete! 🎉                ║
╚════════════════════════════════════════════╝

Next steps:
  1. Review generated settings.json
  2. ✓ Virtual environment created at: .claude/.venv
     ✓ Core dependencies: python-dotenv, psutil, pyyaml, requests
     ✓ Optional dependencies: colorama, rich, GitPython
     ℹ  Managed via pyproject.toml
  3. Customize config files if needed:
     - .claude/hooks/config/__claude_hook__allowed_root_files
     - .claude/hooks/config/__claude_hook__valid_test_paths
  4. Review rules files in project root
  5. ✓ MCP API token configured!
     - Token set for agenthub_http in .mcp.json
     - ⚠ Keep .mcp.json secure (already in .gitignore)
  6. [RECOMMENDED] Generate project-specific CLAUDE.local.md:
     Run: /generate-local-rules or /init-local
  7. Start using Claude Code / Codex!

To reconfigure, run this script again anytime.
```

---

## 💡 Tips

1. **Configure MCP token first**: Get your API token from https://www.4genthub.com/ and configure `.mcp.json` before using MCP features
2. **Automatic gitignore**: Setup automatically adds these to `.gitignore`:
   - `.mcp.json` - MCP configuration with API secrets
   - `.claude/settings.json` - Local settings with machine-specific paths
   - `.env.claude` - Environment variables
   - `logs/**` - Log files and directories
3. **Re-run after Python upgrade**: If you upgrade Python, re-run setup to update paths
4. **Per-project customization**: Edit `CLAUDE.local.md` for project-specific rules
5. **Backup before re-running**: Setup will prompt before overwriting files
6. **Safe to re-run**: Setup is idempotent and won't duplicate gitignore entries

---

## 🎯 Design Principles

- **Simplicity**: One command does everything
- **Intelligence**: Auto-detect 90%, ask 10%
- **Safety**: Idempotent, validated, with backups
- **Clarity**: Clear output, helpful error messages
- **Flexibility**: Works across projects, PCs, environments

---

For full documentation, see [README.md](README.md)
