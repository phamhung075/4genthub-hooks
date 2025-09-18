#!/usr/bin/env python3
"""
Claude Hook Wrapper - Intelligent Path Resolution for Portable Hook Execution

This wrapper solves the problem of relative paths in .claude/settings.json causing
nested ././ path structures when Claude Code executes hooks from subdirectories.

Key Features:
- Maintains portable relative paths in settings.json
- Resolves relative paths to absolute paths at runtime
- Works from any subdirectory within the project
- Prevents nested ././ path issues
- Finds correct project root before path resolution

Usage:
Instead of calling hooks directly, Claude Code should call:
python3 ./.claude/hooks/claude_hook_wrapper.py <hook_name> [args...]

The wrapper will:
1. Find the project root
2. Resolve the hook path correctly
3. Execute the hook with proper paths
"""

import sys
import os
import subprocess
from pathlib import Path
import shlex


class ClaudeHookWrapper:
    """Wrapper for executing Claude hooks with proper path resolution."""

    # Marker files that indicate project root (ordered by priority)
    MARKER_FILES = [
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

    def __init__(self):
        self.project_root = None
        self._debug = os.getenv('CLAUDE_HOOK_DEBUG', '').lower() in ('1', 'true', 'yes')

    def log_debug(self, message):
        """Log debug information if debugging is enabled."""
        if self._debug:
            print(f"[CLAUDE_HOOK_DEBUG] {message}", file=sys.stderr)

    def find_project_root(self, start_path=None):
        """
        Find the project root by looking for marker files.

        Args:
            start_path: Directory to start search from (defaults to current dir)

        Returns:
            Path to project root or None if not found
        """
        if self.project_root:
            return self.project_root

        # Start from provided path, current directory, or script location
        start_paths = []
        if start_path:
            start_paths.append(Path(start_path))
        start_paths.extend([
            Path.cwd(),
            Path(__file__).parent.parent.parent if __file__ else Path.cwd()
        ])

        self.log_debug(f"Starting search from paths: {start_paths}")

        for start in start_paths:
            try:
                current = start.resolve()
                self.log_debug(f"Searching upward from: {current}")

                # Walk up the directory tree
                while current != current.parent:
                    self.log_debug(f"Checking directory: {current}")

                    # Check for marker files in priority order
                    for marker in self.MARKER_FILES:
                        marker_path = current / marker
                        if marker_path.exists():
                            self.log_debug(f"Found marker: {marker_path}")

                            # Verify it's a Claude project by checking for .claude/hooks
                            claude_hooks = current / '.claude' / 'hooks'
                            if claude_hooks.exists():
                                self.log_debug(f"Confirmed Claude project root: {current}")
                                self.project_root = current
                                return self.project_root
                            else:
                                self.log_debug(f"Found {marker} but no .claude/hooks directory")

                    current = current.parent

            except (OSError, PermissionError) as e:
                self.log_debug(f"Error accessing {start}: {e}")
                continue

        self.log_debug("Project root not found")
        return None

    def resolve_relative_path(self, relative_path):
        """
        Resolve a relative path to an absolute path from project root.

        Args:
            relative_path: Path that may be relative (e.g., "./.claude/hooks/script.py")

        Returns:
            Absolute path or None if project root not found
        """
        project_root = self.find_project_root()
        if not project_root:
            return None

        # Clean up the relative path
        # Remove leading "./" if present
        path_str = str(relative_path)
        if path_str.startswith('./'):
            path_str = path_str[2:]
        elif path_str.startswith('.\\'):  # Windows
            path_str = path_str[2:]

        # Remove any leading slashes
        path_str = path_str.lstrip('/')
        path_str = path_str.lstrip('\\')

        # Construct absolute path
        absolute_path = project_root / path_str

        self.log_debug(f"Resolved '{relative_path}' to '{absolute_path}'")
        return absolute_path

    def parse_command(self, command_line):
        """
        Parse a command line and resolve any relative paths to hooks.

        Args:
            command_line: Full command line as string or list

        Returns:
            Tuple of (executable, resolved_script_path, remaining_args)
        """
        if isinstance(command_line, str):
            parts = shlex.split(command_line)
        else:
            parts = list(command_line)

        if len(parts) < 2:
            raise ValueError("Command must have at least executable and script path")

        executable = parts[0]  # e.g., "python3"
        script_path = parts[1]  # e.g., "./.claude/hooks/script.py"
        args = parts[2:]       # remaining arguments

        # Resolve the script path if it looks like a relative Claude hook path
        if ('.claude' in script_path and
            (script_path.startswith('./') or script_path.startswith('.\\'))):

            resolved_path = self.resolve_relative_path(script_path)
            if resolved_path and resolved_path.exists():
                script_path = str(resolved_path)
            else:
                self.log_debug(f"Warning: Could not resolve or find {script_path}")

        return executable, script_path, args

    def execute_hook(self, command_line, **kwargs):
        """
        Execute a hook command with proper path resolution.

        Args:
            command_line: Command to execute (string or list)
            **kwargs: Additional arguments for subprocess.run()

        Returns:
            subprocess.CompletedProcess result
        """
        try:
            executable, script_path, args = self.parse_command(command_line)

            # Construct final command
            final_command = [executable, script_path] + args

            self.log_debug(f"Executing: {' '.join(final_command)}")

            # Change to project root before execution (important for imports)
            project_root = self.find_project_root()
            original_cwd = os.getcwd()

            if project_root:
                os.chdir(project_root)
                self.log_debug(f"Changed working directory to: {project_root}")

            try:
                # Execute the command
                result = subprocess.run(final_command, **kwargs)
                return result
            finally:
                os.chdir(original_cwd)

        except Exception as e:
            self.log_debug(f"Error executing hook: {e}")
            raise


def main():
    """
    Main entry point for the wrapper.

    Usage: python3 claude_hook_wrapper.py <hook_name> [args...]
    """
    if len(sys.argv) < 2:
        print("Usage: python3 claude_hook_wrapper.py <hook_name> [args...]", file=sys.stderr)
        print("Example: python3 claude_hook_wrapper.py user_prompt_submit.py --log-only", file=sys.stderr)
        sys.exit(1)

    # Extract hook name and arguments
    hook_name = sys.argv[1]
    hook_args = sys.argv[2:] if len(sys.argv) > 2 else []

    # Create wrapper instance
    wrapper = ClaudeHookWrapper()

    # Find project root
    project_root = wrapper.find_project_root()
    if not project_root:
        print("Error: Could not find project root", file=sys.stderr)
        sys.exit(1)

    # Construct command
    hook_path = f"./.claude/hooks/{hook_name}"
    command = ["python3", hook_path] + hook_args

    # Execute the hook
    try:
        result = wrapper.execute_hook(command, capture_output=False)
        sys.exit(result.returncode)
    except Exception as e:
        print(f"Error executing hook: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()