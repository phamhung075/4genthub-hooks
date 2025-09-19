#!/usr/bin/env python3
"""
Universal hook wrapper that finds and executes hooks from the correct project root.
This solves the issue of hooks being called with relative paths from subdirectories.
"""

import sys
import os
import subprocess
from pathlib import Path

def find_project_root():
    """Find the project root by looking for marker files."""
    # Start from current directory or script location
    start_paths = [
        Path.cwd(),
        Path(__file__).parent.parent.parent if __file__ else Path.cwd()
    ]

    for start in start_paths:
        current = start.resolve()

        # Walk up the directory tree
        while current != current.parent:
            # Check for project markers (prioritized)
            markers = [
                'CLAUDE.md',
                '.env.dev',
                '.env.claude',
                'docker-compose.yml',
                '.git'
            ]

            for marker in markers:
                if (current / marker).exists():
                    # Verify it's the right project by checking for .claude/hooks
                    if (current / '.claude' / 'hooks').exists():
                        return current

            current = current.parent

    # Fallback: check known absolute path
    known_root = Path('/home/daihungpham/__projects__/4genthub')
    if known_root.exists() and (known_root / '.claude' / 'hooks').exists():
        return known_root

    return None

def main():
    """Main wrapper logic."""
    # Get the hook name from command line
    if len(sys.argv) < 2:
        print("Error: No hook specified", file=sys.stderr)
        sys.exit(1)

    hook_name = sys.argv[1]
    hook_args = sys.argv[2:] if len(sys.argv) > 2 else []

    # Find project root
    project_root = find_project_root()
    if not project_root:
        print("Error: Could not find project root", file=sys.stderr)
        sys.exit(1)

    # Construct absolute path to the hook
    hook_path = project_root / '.claude' / 'hooks' / hook_name

    if not hook_path.exists():
        print(f"Error: Hook not found: {hook_path}", file=sys.stderr)
        sys.exit(1)

    # Execute the hook with the original arguments
    cmd = [sys.executable, str(hook_path)] + hook_args

    # Change to project root before execution (important for imports)
    original_cwd = os.getcwd()
    os.chdir(project_root)

    try:
        # Run the hook and pass through stdin/stdout/stderr
        result = subprocess.run(cmd, capture_output=False)
        sys.exit(result.returncode)
    except Exception as e:
        print(f"Error executing hook: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        os.chdir(original_cwd)

if __name__ == "__main__":
    main()