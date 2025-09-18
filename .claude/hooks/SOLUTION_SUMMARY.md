# Hook Path Resolution Solution

## Problem Solved

The Claude Code hook system was experiencing path resolution issues when executing hooks from subdirectories, causing nested `././` path structures like:
```
/project/subdir/./.claude/hooks/user_prompt_submit.py
```

This resulted in "No such file or directory" errors when hooks were executed from any directory other than the project root.

## Root Cause

When Claude Code executed commands like `python3 ./.claude/hooks/script.py` from subdirectories, the shell resolved the relative path incorrectly, creating malformed nested paths.

## Solution: Execute Hook Wrapper

### Architecture

1. **execute_hook.py**: Universal wrapper script that handles path resolution
2. **settings.json**: Uses absolute paths to the wrapper (for reliability)
3. **Wrapper logic**: Internally resolves hook locations and executes from correct project root

### Key Components

#### 1. execute_hook.py
- **Location**: `.claude/hooks/execute_hook.py`
- **Purpose**: Universal hook executor with intelligent path resolution
- **Features**:
  - Finds project root using multiple marker files (CLAUDE.md, .env.dev, .git, etc.)
  - Resolves hook paths in multiple subdirectories (hooks/, status_lines/)
  - Changes working directory to project root before execution
  - Maintains all original hook functionality

#### 2. Updated settings.json
- **Before**: `"command": "python3 ./.claude/hooks/script.py"`
- **After**: `"command": "python3 /absolute/path/.claude/hooks/execute_hook.py script.py"`
- **Benefit**: Wrapper path is absolute (reliable), but hook resolution is dynamic

#### 3. generate_settings.py
- **Purpose**: Automatically generates correct settings.json with wrapper approach
- **Usage**: `python3 ./.claude/hooks/utils/generate_settings.py`
- **Benefit**: Easy deployment on different machines

### Implementation Details

#### Wrapper Execution Flow
```
1. Claude Code executes: python3 /project/.claude/hooks/execute_hook.py user_prompt_submit.py --args
2. execute_hook.py finds project root
3. execute_hook.py locates user_prompt_submit.py in .claude/hooks/
4. execute_hook.py changes to project root directory
5. execute_hook.py executes: python3 /project/.claude/hooks/user_prompt_submit.py --args
```

#### Project Root Detection
```python
MARKER_FILES = [
    'CLAUDE.md',        # Most specific to Claude projects
    '.env.dev',         # Development environment marker
    '.env.claude',      # Claude-specific environment
    'CLAUDE.local.md',  # Local Claude configuration
    '.git',             # Git repository root
    # ... additional markers
]
```

## Files Created/Modified

### Created Files
- `.claude/hooks/execute_hook.py` - Main wrapper script
- `.claude/hooks/utils/path_resolver.py` - Path resolution utility
- `.claude/hooks/claude_hook_wrapper.py` - Alternative wrapper (not used in final solution)
- `.claude/hooks/test_*.py` - Test scripts for verification

### Modified Files
- `.claude/settings.json` - Updated to use wrapper approach
- `.claude/hooks/utils/generate_settings.py` - Updated to generate wrapper-based settings

## Testing Results

✅ **All tests passed:**
- Execution from project root
- Execution from `.claude` subdirectory (previously problematic)
- Execution from `.claude/hooks` subdirectory (previously problematic)
- Execution from deeply nested test directories
- Both regular hooks and status line scripts work correctly

## Usage

### For End Users
No changes needed - hooks work automatically from any directory.

### For Deployment
1. Run: `python3 ./.claude/hooks/utils/generate_settings.py`
2. This generates correct `settings.json` with absolute wrapper paths for the current machine

### For Development
- Hooks are executed via the wrapper transparently
- Original hook functionality is preserved
- Working directory is automatically set to project root

## Benefits

1. **Maintains Portability**: Only wrapper path is absolute, hook logic remains relative
2. **Backward Compatible**: All existing hooks work without modification
3. **Robust**: Works from any subdirectory within the project
4. **Self-Healing**: Wrapper finds project root automatically
5. **Easy Deployment**: Single command updates settings for new machines

## Acceptance Criteria ✅

- [x] .claude/settings.json maintains portability approach
- [x] Hook wrapper correctly resolves relative paths to absolute paths
- [x] No more nested ././ in final executed paths
- [x] Works from any subdirectory in project
- [x] Same settings approach works on different PCs (via generate_settings.py)

## Migration Guide

### From Relative Paths
If you have settings with relative paths like:
```json
"command": "python3 ./.claude/hooks/script.py"
```

Run:
```bash
python3 ./.claude/hooks/utils/generate_settings.py
```

This will update to:
```json
"command": "python3 /absolute/path/.claude/hooks/execute_hook.py script.py"
```

### From Absolute Paths
If you have settings with absolute paths, the same command works and provides better portability.

## Future Maintenance

- **Adding new hooks**: Works automatically with wrapper
- **Moving to new machine**: Run `generate_settings.py` to update wrapper paths
- **Project structure changes**: Wrapper automatically adapts using marker file detection

## Error Handling

The wrapper provides clear error messages:
- "Error: Could not find project root" - Project structure issue
- "Error: Hook not found: script.py" - Hook file missing
- Includes search paths in error messages for debugging

This solution completely eliminates the nested `././` path resolution issues while maintaining full compatibility and portability.