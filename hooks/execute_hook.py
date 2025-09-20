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
5. Prevents infinite recursion during hook execution
6. Provides clear error messages for common issues

Git Submodule Support:
- Works with .claude as a Git submodule
- No symlink handling needed - uses direct paths
- Maintains compatibility across different project structures

Error Handling:
- Checks if settings.json exists, suggests running setup_hooks.py if missing
- Validates hook file paths before execution
- Prevents infinite loops with CLAUDE_HOOK_EXECUTING environment variable
- Provides troubleshooting guidance for common issues

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


def check_recursion_prevention():
    """
    Check for infinite recursion prevention and set environment variable.

    Returns:
        bool: True if execution should continue, False if recursion detected
    """
    if os.environ.get('CLAUDE_HOOK_EXECUTING') == '1':
        print("Warning: Hook execution recursion detected - stopping to prevent infinite loop", file=sys.stderr)
        return False

    # Set environment variable to prevent recursion
    os.environ['CLAUDE_HOOK_EXECUTING'] = '1'
    return True


def check_settings_file(project_root):
    """
    Check if settings.json exists and provide helpful error messages.

    Args:
        project_root: Path to the project root directory

    Returns:
        bool: True if settings.json exists, False otherwise
    """
    settings_path = project_root / '.claude' / 'settings.json'

    if not settings_path.exists():
        print("❌ ERROR: settings.json not found", file=sys.stderr)
        print(f"   Expected location: {settings_path}", file=sys.stderr)
        print("", file=sys.stderr)
        print("🔧 SOLUTION: Run the setup script to create settings.json:", file=sys.stderr)
        print(f"   python3 {project_root}/.claude/hooks/setup_hooks.py", file=sys.stderr)
        print("", file=sys.stderr)
        print("📖 This will:", file=sys.stderr)
        print("   1. Auto-detect your project paths", file=sys.stderr)
        print("   2. Create settings.json with correct absolute paths", file=sys.stderr)
        print("   3. Validate all hook files exist", file=sys.stderr)
        print("   4. Add settings.json to .gitignore", file=sys.stderr)
        return False

    return True


def validate_hook_path(hook_path, hook_name, claude_dir):
    """
    Validate hook file exists and provide helpful error messages.

    Args:
        hook_path: Path to the hook file
        hook_name: Name of the hook file
        claude_dir: Path to the .claude directory

    Returns:
        bool: True if hook file exists, False otherwise
    """
    if hook_path.exists():
        return True

    print(f"❌ ERROR: Hook file not found: {hook_name}", file=sys.stderr)
    print(f"   Expected location: {hook_path}", file=sys.stderr)
    print("", file=sys.stderr)

    # List available hook files to help user
    hooks_dir = claude_dir / 'hooks'
    if hooks_dir.exists():
        print("📁 Available hook files:", file=sys.stderr)
        python_files = list(hooks_dir.glob('*.py'))
        if python_files:
            for py_file in sorted(python_files):
                print(f"   - {py_file.name}", file=sys.stderr)
        else:
            print("   No Python files found in hooks directory", file=sys.stderr)

    print("", file=sys.stderr)
    print("🔧 POSSIBLE SOLUTIONS:", file=sys.stderr)
    print("   1. Check your settings.json paths are correct", file=sys.stderr)
    print("   2. Re-run setup script: python3 .claude/hooks/setup_hooks.py", file=sys.stderr)
    print("   3. Verify the hook file exists and has correct name", file=sys.stderr)

    return False


def main():
    """Main execution wrapper with enhanced error handling."""
    # Check for help flag
    if len(sys.argv) >= 2 and sys.argv[1] in ['--help', '-h', 'help']:
        print("Claude Code Hook Executor")
        print("=" * 25)
        print("Usage: python3 execute_hook.py <hook_name> [args...]")
        print("")
        print("Examples:")
        print("  python3 execute_hook.py user_prompt_submit.py --log-only")
        print("  python3 execute_hook.py pre_tool_use.py")
        print("  python3 execute_hook.py status_line_mcp.py")
        print("")
        print("Setup:")
        print("  If you get errors about missing settings.json, run:")
        print("  python3 .claude/hooks/setup_hooks.py")
        sys.exit(0)

    if len(sys.argv) < 2:
        print("Usage: python3 execute_hook.py <hook_name> [args...]", file=sys.stderr)
        print("Example: python3 execute_hook.py user_prompt_submit.py --log-only", file=sys.stderr)
        print("For help: python3 execute_hook.py --help", file=sys.stderr)
        sys.exit(1)

    # Check for recursion prevention
    if not check_recursion_prevention():
        sys.exit(1)

    try:
        # Extract hook name and arguments
        hook_name = sys.argv[1]
        hook_args = sys.argv[2:] if len(sys.argv) > 2 else []

        # Find project root
        project_root = find_project_root()
        if not project_root:
            print("❌ ERROR: Could not find project root", file=sys.stderr)
            print("", file=sys.stderr)
            print("🔍 TROUBLESHOOTING:", file=sys.stderr)
            print("   1. Make sure you're running this from within a project directory", file=sys.stderr)
            print("   2. Ensure one of these files exists in your project root:", file=sys.stderr)
            print("      - CLAUDE.md, .git, package.json, pyproject.toml, .env", file=sys.stderr)
            print("   3. Make sure .claude/hooks/ directory exists", file=sys.stderr)
            sys.exit(1)

        # Check if settings.json exists
        if not check_settings_file(project_root):
            sys.exit(1)

        # Resolve the hooks directory for Git submodule structure
        hooks_dir = resolve_claude_hooks_path(project_root)
        if not hooks_dir:
            print("❌ ERROR: Could not find .claude/hooks directory", file=sys.stderr)
            print(f"   Expected location: {project_root}/.claude/hooks", file=sys.stderr)
            print("", file=sys.stderr)
            print("🔧 SOLUTION: Ensure .claude/hooks directory exists with hook files", file=sys.stderr)
            sys.exit(1)

        # Get the base .claude directory (Git submodule - no symlink resolution needed)
        claude_dir = project_root / '.claude'

        # First try in hooks directory
        hook_path = hooks_dir / hook_name

        # If not found, try in status_lines directory (for status line scripts)
        if not hook_path.exists() and 'status_line' in hook_name:
            status_lines_dir = claude_dir / 'status_lines'
            if status_lines_dir.exists():
                hook_path = status_lines_dir / hook_name

        # If still not found, try to find it in any .claude subdirectory
        if not hook_path.exists():
            for subdir in ['hooks', 'status_lines', 'scripts']:
                potential_path = claude_dir / subdir / hook_name
                if potential_path.exists():
                    hook_path = potential_path
                    break

        # Validate hook file exists with helpful error messages
        if not validate_hook_path(hook_path, hook_name, claude_dir):
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
            print(f"❌ ERROR: Failed to execute hook: {e}", file=sys.stderr)
            print(f"   Command: {' '.join(cmd)}", file=sys.stderr)
            print(f"   Working directory: {project_root}", file=sys.stderr)
            sys.exit(1)
        finally:
            os.chdir(original_cwd)

    finally:
        # Clear recursion prevention flag
        if 'CLAUDE_HOOK_EXECUTING' in os.environ:
            del os.environ['CLAUDE_HOOK_EXECUTING']


if __name__ == "__main__":
    main()