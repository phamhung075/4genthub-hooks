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
git submodule add git@github.com:phamhung075/4genthub-hooks.git .claude

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
3. ✅ Generates `settings.json` with correct paths
4. ✅ Creates config files from templates
5. ✅ Deploys rules files to project root
6. ✅ Validates everything

**Time: < 2 minutes** ⚡

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

---

## 📁 File Structure

```
.claude/
├── setup.py                    # 🚀 Run this
├── SETUP.md                    # 📖 This file
├── README.md                   # Full documentation
├── settings.json               # Generated config
├── templates/
│   └── settings.json.template  # Template with placeholders
├── hooks/
│   ├── *.py                    # Hook scripts
│   ├── config/
│   │   ├── __claude_hook__allowed_root_files
│   │   └── __claude_hook__valid_test_paths
│   ├── claude-rules/           # Claude Code rules
│   └── codex-rules/            # Codex rules
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
Use this path? [Y/n]:

Which AI coding tool are you using?
  [1] Claude Code (Anthropic)
  [2] OpenAI Codex
  [3] Both

Choice [1-3]: 1

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

Validating setup...
  ✓ settings.json
  ✓ allowed_root_files config
  ✓ valid_test_paths config
  ✓ Python path configured correctly

╔════════════════════════════════════════════╗
║          Setup Complete! 🎉                ║
╚════════════════════════════════════════════╝

Next steps:
  1. Review generated settings.json
  2. Customize config files if needed
  3. Review rules files in project root
  4. Start using Claude Code!

To reconfigure, run this script again anytime.
```

---

## 💡 Tips

1. **Re-run after Python upgrade**: If you upgrade Python, re-run setup to update paths
2. **Per-project customization**: Edit `CLAUDE.local.md` for project-specific rules
3. **Backup before re-running**: Setup will prompt before overwriting files
4. **Version control**: Add `.claude/settings.json` to `.gitignore` (contains local paths)

---

## 🎯 Design Principles

- **Simplicity**: One command does everything
- **Intelligence**: Auto-detect 90%, ask 10%
- **Safety**: Idempotent, validated, with backups
- **Clarity**: Clear output, helpful error messages
- **Flexibility**: Works across projects, PCs, environments

---

For full documentation, see [README.md](README.md)
