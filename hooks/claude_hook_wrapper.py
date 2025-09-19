#!/usr/bin/env python3
"""
Claude Hook Wrapper - Python-based wrapper for Claude Code hooks

This Python-based wrapper replaces the shell-based claude_hook_exec to solve
symlink and executable permission issues. It provides a robust solution that:

1. Works with symlinked .claude directories automatically
2. Doesn't require executable permissions (called with python3)
3. Resolves paths correctly from any subdirectory
4. Provides better error messages and debugging
5. Is more portable across different shell environments

Usage:
    python3 ./.claude/hooks/claude_hook_wrapper.py <hook_name> [args...]

Examples:
    python3 ./.claude/hooks/claude_hook_wrapper.py status_line_mcp.py
    python3 ./.claude/hooks/claude_hook_wrapper.py user_prompt_submit.py --log-only

The wrapper automatically finds the project root and resolves the correct
path to execute_hook.py, handling symlinked .claude directories properly.
"""

import sys
import os
import subprocess
from pathlib import Path


def find_project_root():
    """
    Find the project root by looking for marker files.

    This function searches up the directory tree from the current working
    directory and the wrapper script's location to find project markers.

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
                        # Verify it's a Claude project by checking for .claude
                        claude_dir = current / '.claude'
                        if claude_dir.exists():
                            return current

                current = current.parent

        except (OSError, PermissionError):
            continue

    return None


def resolve_execute_hook_path(project_root):
    """
    Find and resolve the path to execute_hook.py, handling symlinked .claude directories.

    Args:
        project_root: Path to the project root

    Returns:
        Path to execute_hook.py or None if not found
    """
    claude_dir = project_root / '.claude'

    # Check if .claude exists
    if not claude_dir.exists():
        return None

    # If .claude is a symlink, resolve it to the real path
    if claude_dir.is_symlink():
        try:
            # Resolve the symlink to get the real .claude directory
            real_claude_dir = claude_dir.resolve()
            execute_hook_path = real_claude_dir / 'hooks' / 'execute_hook.py'
        except (OSError, RuntimeError):
            # If symlink resolution fails, fall back to original path
            execute_hook_path = claude_dir / 'hooks' / 'execute_hook.py'
    else:
        # .claude is a regular directory
        execute_hook_path = claude_dir / 'hooks' / 'execute_hook.py'

    return execute_hook_path if execute_hook_path.exists() else None


def main():
    """
    Main execution function.

    This function:
    1. Validates command line arguments
    2. Finds the project root
    3. Resolves the path to execute_hook.py
    4. Executes the hook with proper environment setup
    """
    # Check if at least one argument provided
    if len(sys.argv) < 2:
        print("Usage: python3 claude_hook_wrapper.py <hook_name> [args...]", file=sys.stderr)
        print("Example: python3 claude_hook_wrapper.py user_prompt_submit.py --log-only", file=sys.stderr)
        print("\nThis wrapper replaces claude_hook_exec and provides better symlink support.", file=sys.stderr)
        sys.exit(1)

    # Find project root
    project_root = find_project_root()
    if not project_root:
        print("Error: Could not find project root", file=sys.stderr)
        print("Searched for markers: CLAUDE.md, .env.dev, .env.claude, .git, package.json, pyproject.toml", file=sys.stderr)
        print(f"Current directory: {Path.cwd()}", file=sys.stderr)
        print(f"Script location: {Path(__file__).parent if __file__ else 'unknown'}", file=sys.stderr)
        sys.exit(1)

    # Resolve the execute_hook.py path, handling symlinked .claude directories
    execute_hook_path = resolve_execute_hook_path(project_root)
    if not execute_hook_path:
        print("Error: Could not find execute_hook.py", file=sys.stderr)
        print(f"Project root: {project_root}", file=sys.stderr)
        print(f"Expected location: {project_root}/.claude/hooks/execute_hook.py", file=sys.stderr)

        # Check if .claude is a symlink and provide helpful debugging
        claude_dir = project_root / '.claude'
        if claude_dir.is_symlink():
            try:
                real_claude = claude_dir.resolve()
                print(f"Symlinked .claude resolves to: {real_claude}", file=sys.stderr)
                print(f"Expected symlink target: {real_claude}/hooks/execute_hook.py", file=sys.stderr)
            except (OSError, RuntimeError) as e:
                print(f"Error resolving .claude symlink: {e}", file=sys.stderr)

        sys.exit(1)

    # Prepare command arguments
    hook_args = sys.argv[1:]  # All arguments starting from hook name

    # Execute execute_hook.py with all arguments
    # We use execute_hook.py which handles the actual hook execution
    cmd = [sys.executable, str(execute_hook_path)] + hook_args

    try:
        # Execute and pass through stdin/stdout/stderr directly
        result = subprocess.run(cmd, capture_output=False)
        sys.exit(result.returncode)
    except Exception as e:
        print(f"Error executing hook: {e}", file=sys.stderr)
        print(f"Command: {' '.join(cmd)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()