# Universal Claude Hook System

This system provides a universal hook execution wrapper that works seamlessly with symlinked `.claude` directories across all projects.

## Problem Solved

When `.claude` directories are symlinked to other projects, the relative paths in `settings.json` (like `python3 ./.claude/hooks/execute_hook.py`) fail because:

1. Claude Code resolves the relative path from the current working directory
2. The actual `execute_hook.py` doesn't exist in the symlinked directory - it exists in the real directory
3. This causes "No such file or directory" errors

## Solution

The universal hook system uses a shell wrapper (`claude_hook_exec`) that:

1. **Resolves real paths**: Finds the actual location of hook files even through symlinks
2. **Works from anywhere**: Can be called from any subdirectory in any project
3. **Maintains compatibility**: Uses the existing `execute_hook.py` with all its sophisticated features
4. **Requires no modification**: Uses the same command structure in `settings.json`

## Architecture

```
Project (any)
├── .claude (may be symlinked)
│   ├── settings.json (uses ./claude_hook_exec commands)
│   └── hooks/
│       ├── claude_hook_exec (universal wrapper - shell script)
│       ├── execute_hook.py (symlinked to real location)
│       ├── session_start.py (symlinked to real location)
│       └── ... (other hooks symlinked)
└── any_subdirectory/
    └── (hooks work from here too)
```

## Usage

### Setting Up New Projects

1. **Quick Setup** (recommended):
   ```bash
   # From the hooks project
   ./setup_universal_hooks.sh /path/to/target/project
   ```

2. **Manual Setup**:
   ```bash
   # Copy the universal executor
   cp claude_hook_exec /target/project/.claude/hooks/
   chmod +x /target/project/.claude/hooks/claude_hook_exec

   # Create symlinks to hook files
   ln -s /path/to/real/hooks/*.py /target/project/.claude/hooks/

   # Update settings.json commands (see below)
   ```

### Settings.json Configuration

Replace all `python3 ./.claude/hooks/execute_hook.py` commands with `./.claude/hooks/claude_hook_exec`:

**Before (problematic with symlinks):**
```json
{
  "command": "python3 ./.claude/hooks/execute_hook.py session_start.py"
}
```

**After (works universally):**
```json
{
  "command": "./.claude/hooks/claude_hook_exec session_start.py"
}
```

### Example Complete Settings.json

```json
{
  "statusLine": {
    "type": "command",
    "command": "./.claude/hooks/claude_hook_exec status_line_mcp.py",
    "padding": 0
  },
  "hooks": {
    "SessionStart": [{
      "hooks": [{
        "type": "command",
        "command": "./.claude/hooks/claude_hook_exec session_start.py"
      }]
    }],
    "PreToolUse": [{
      "hooks": [{
        "type": "command",
        "command": "./.claude/hooks/claude_hook_exec pre_tool_use.py"
      }]
    }]
    // ... etc for all hooks
  }
}
```

## How It Works

### 1. Universal Path Resolution

The `claude_hook_exec` wrapper finds `execute_hook.py` using multiple strategies:

1. **Script directory**: Most reliable when called via symlink
2. **Current directory**: Original approach for compatibility
3. **Symlink resolution**: Resolves `.claude` symlinks to real locations
4. **Project tree search**: Walks up directories looking for project markers

### 2. Project Root Detection

Searches for these markers (in priority order):
- `CLAUDE.md` (most specific)
- `.env.dev`, `.env.claude`, `CLAUDE.local.md`
- `.git` (git repository)
- `package.json` (Node.js project)
- `pyproject.toml` (Python project)
- Other common project markers

### 3. Symlink Handling

- Detects symlinked `.claude` directories
- Resolves to real directory where hooks actually exist
- Maintains all original functionality of `execute_hook.py`

## Benefits

✅ **Universal compatibility**: Works in any project, with or without symlinks
✅ **No path issues**: Handles nested directories and symlink resolution
✅ **Zero configuration**: Same commands work across all projects
✅ **Backward compatible**: Existing hooks continue to work unchanged
✅ **Error resilient**: Clear error messages when hooks can't be found
✅ **Performance**: Minimal overhead, direct execution once path is resolved

## Testing

```bash
# Test the wrapper directly
./.claude/hooks/claude_hook_exec session_start.py --help

# Test from subdirectories
cd some/deep/subdirectory
../../../.claude/hooks/claude_hook_exec session_start.py --help

# Test with symlinked .claude
ln -s /path/to/real/.claude /other/project/.claude
cd /other/project
./.claude/hooks/claude_hook_exec session_start.py --help
```

## Troubleshooting

### "Could not find execute_hook.py"

1. Ensure `claude_hook_exec` is executable: `chmod +x claude_hook_exec`
2. Verify project has a marker file (CLAUDE.md, .git, etc.)
3. Check that hook files exist in the real `.claude/hooks` directory
4. Verify symlinks are not broken

### "Could not find project root"

1. Create a project marker: `touch CLAUDE.md` or `git init`
2. Ensure you're in or below a directory with `.claude/hooks`
3. Check file permissions on parent directories

### Hooks not executing properly

1. Verify `settings.json` uses `claude_hook_exec` instead of direct Python calls
2. Check that all hook dependencies are properly symlinked
3. Ensure the `utils` directory is linked if hooks depend on it

## Migration from Old System

1. **Backup current settings**: `cp .claude/settings.json .claude/settings.json.backup`
2. **Run setup script**: `./setup_universal_hooks.sh`
3. **Update commands**: Replace `python3 ./.claude/hooks/execute_hook.py` with `./.claude/hooks/claude_hook_exec`
4. **Test thoroughly**: Verify all hooks work from various directories

The universal hook system maintains full backward compatibility while solving symlink path resolution issues permanently.