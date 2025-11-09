# .claude Quick Start - 2 Minutes Setup ⚡

## For New Projects or PCs

### Step 1: Get the `.claude` directory

**⭐ RECOMMENDED: Git Submodule (Easy Updates)**
```bash
# Navigate to your project
cd your-project

# Add as submodule - updates all projects with one command!
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
- ✅ Works in any nested project structure
- ✅ Version control for hooks

**Alternative: Copy from existing project**
```bash
# If you already have .claude in another project
cp -r /path/to/existing/project/.claude /path/to/new/project/
```

### Step 2: Run setup
```bash
python .claude/setup.py
```

### Step 3: Answer 3 questions
1. **Python path?** (auto-detected, just press Enter)
2. **Which AI tool?** (Choose: 1=Claude Code, 2=Codex, 3=Both)
3. **Token strategy?** (Choose: 1=Economic, 2=Performance)

### Step 4: Generate project-specific rules (RECOMMENDED)
```bash
# In Claude Code, run this slash command:
/generate-local-rules

# Or the shorter alias:
/init-local
```

This will analyze your project and create a custom `CLAUDE.local.md` tailored to your architecture!

### Done! 🎉

---

## What Just Happened?

✅ Auto-detected your Python path
✅ Generated `.claude/settings.json` with correct paths
✅ Created configuration files
✅ Deployed rules files to project root
✅ Deployed `.env.claude` environment configuration
✅ Validated everything works

---

## Files Created

| File | Purpose |
|------|---------|
| `.claude/settings.json` | Main configuration (9 paths updated) |
| `.claude/hooks/config/__claude_hook__allowed_root_files` | Root file restrictions |
| `.claude/hooks/config/__claude_hook__valid_test_paths` | Test directory locations |
| `CLAUDE.md` (root) | Claude Code instructions |
| `CLAUDE.local.md` (root) | Local project rules |
| `AGENTS.md` (root) | Codex agent configuration (if selected) |
| `.env.claude` (root) | Claude Code environment variables |

---

## Troubleshooting

### Python Not Found?
```bash
# Find it manually
which python3

# Then enter path when setup prompts
```

### Re-configure Anytime
```bash
python .claude/setup.py  # Safe to re-run
```

### Make Script Executable
```bash
chmod +x .claude/setup.py
```

---

## Pro Tips

1. **Python 3.14 recommended** - Setup auto-detects, works with 3.8+
2. **Update hooks across ALL projects** - If using submodule: `git submodule update --remote .claude`
3. **Different Python per project?** Re-run setup in each project
4. **Upgrade Python?** Re-run setup to update paths
5. **Custom config?** Edit files in `.claude/hooks/config/`
6. **Share with team?** Use git submodule (everyone gets same version)
7. **New project?** Run `/generate-local-rules` to auto-generate project-specific CLAUDE.local.md
8. **Token optimization?** Choose "Economic" for most projects, "Performance" for learning/exploration

## Updating Hooks (Submodule Method)

```bash
# Update .claude in current project
cd your-project
git submodule update --remote .claude
git add .claude
git commit -m "Update .claude hooks to latest version"

# Update ALL projects with .claude submodule
find ~/projects -name ".gitmodules" -execdir git submodule update --remote .claude \;
```

**This updates hooks in all your projects simultaneously!** 🚀

---

## Full Documentation

- **Setup Guide**: [SETUP.md](SETUP.md)
- **Full Docs**: [README.md](README.md)

---

**That's it! Your .claude configuration is ready to use.** 🚀
