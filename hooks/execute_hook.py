#!/usr/bin/env python3
"""
Execute Hook Wrapper - Universal hook executor for Claude Code

This wrapper solves the path resolution issue where relative paths in
.claude/settings.json cause nested ././ path problems when Claude Code
executes hooks from subdirectories.

Instead of having commands like:
  "command": "python3 ./.claude/hooks/user_prompt_submit.py --args"

We use:
  "command": "python3 ./.claude/hooks/execute_hook.py user_prompt_submit.py --args"

This wrapper:
1. Finds the correct project root regardless of execution directory
2. Resolves the hook path correctly for Git submodule structure
3. Executes the hook with proper environment setup
4. Maintains all original functionality

Git Submodule Support:
- Works with .claude as a Git submodule
- No symlink handling needed - uses direct paths
- Maintains compatibility across different project structures

Usage: python3 execute_hook.py <hook_name> [args...]
"""

import sys
import os
import subprocess
from pathlib import Path


def find_project_root():
    """
    Find the project root by looking for marker files.

    Returns:
        Path to project root or None if not found
    """
    # Marker files that indicate project root (ordered by priority)
    markers = [
        'CLAUDE.md',        # Most specific to Claude projects
        '.env.dev',         # Development environment marker
        '.env.claude',      # Claude-specific environment
        'CLAUDE.local.md',  # Local Claude configuration
        '.git',             # Git repository root
        'package.json',     # Node.js project
        'pyproject.toml',   # Python project
        'docker-compose.yml', # Docker project
        '.env',             # General environment file
    ]

    # Start from current directory and this script's location
    start_paths = [
        Path.cwd(),
        Path(__file__).parent.parent.parent if __file__ else Path.cwd()
    ]

    for start in start_paths:
        try:
            current = start.resolve()

            # Walk up the directory tree
            while current != current.parent:
                # Check for marker files in priority order
                for marker in markers:
                    marker_path = current / marker
                    if marker_path.exists():
                        # Verify it's a Claude project by checking for .claude/hooks
                        claude_dir = current / '.claude'
                        if claude_dir.exists():
                            # Direct path - no symlink handling needed for Git submodules
                            claude_hooks = claude_dir / 'hooks'
                            if claude_hooks.exists():
                                return current

                current = current.parent

        except (OSError, PermissionError):
            continue

    return None


def resolve_claude_hooks_path(project_root):
    """
    Resolve the path to .claude/hooks for Git submodule structure.

    Args:
        project_root: Path to the project root

    Returns:
        Path to the hooks directory
    """
    claude_dir = project_root / '.claude'

    # Check if .claude exists
    if not claude_dir.exists():
        return None

    # Direct path for Git submodule - no symlink handling needed
    hooks_dir = claude_dir / 'hooks'

    return hooks_dir if hooks_dir.exists() else None


def main():
    """Main execution wrapper."""
    if len(sys.argv) < 2:
        print("Usage: python3 execute_hook.py <hook_name> [args...]", file=sys.stderr)
        print("Example: python3 execute_hook.py user_prompt_submit.py --log-only", file=sys.stderr)
        sys.exit(1)

    # Extract hook name and arguments
    hook_name = sys.argv[1]
    hook_args = sys.argv[2:] if len(sys.argv) > 2 else []

    # Find project root
    project_root = find_project_root()
    if not project_root:
        print("Error: Could not find project root", file=sys.stderr)
        sys.exit(1)

    # Resolve the hooks directory for Git submodule structure
    hooks_dir = resolve_claude_hooks_path(project_root)
    if not hooks_dir:
        print("Error: Could not find .claude/hooks directory", file=sys.stderr)
        sys.exit(1)

    # Get the base .claude directory (may be symlinked)
    claude_dir = project_root / '.claude'
    # Resolve symlink if necessary
    if claude_dir.is_symlink():
        try:
            real_claude_dir = claude_dir.resolve()
        except (OSError, RuntimeError):
            real_claude_dir = claude_dir
    else:
        real_claude_dir = claude_dir

    # First try in hooks directory
    hook_path = hooks_dir / hook_name

    # If not found, try in status_lines directory (for status line scripts)
    if not hook_path.exists() and 'status_line' in hook_name:
        status_lines_dir = real_claude_dir / 'status_lines'
        if status_lines_dir.exists():
            hook_path = status_lines_dir / hook_name

    # If still not found, try to find it in any .claude subdirectory
    if not hook_path.exists():
        for subdir in ['hooks', 'status_lines', 'scripts']:
            potential_path = real_claude_dir / subdir / hook_name
            if potential_path.exists():
                hook_path = potential_path
                break

    if not hook_path.exists():
        print(f"Error: Hook not found: {hook_name}", file=sys.stderr)
        print(f"Searched in: {hooks_dir}, {real_claude_dir}/status_lines/", file=sys.stderr)
        sys.exit(1)

    # Construct command with absolute path
    cmd = [sys.executable, str(hook_path)] + hook_args

    # Change to project root before execution (important for imports and relative paths)
    original_cwd = os.getcwd()
    os.chdir(project_root)

    try:
        # Execute the hook and pass through stdin/stdout/stderr
        result = subprocess.run(cmd, capture_output=False)
        sys.exit(result.returncode)
    except Exception as e:
        print(f"Error executing hook: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        os.chdir(original_cwd)


if __name__ == "__main__":
    main()