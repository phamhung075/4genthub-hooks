#!/usr/bin/env python3
"""
Universal hook loader that can be called from anywhere.
Place this in each subdirectory where Claude might run.
"""

import sys
import os
from pathlib import Path

def find_and_run_hook():
    """Find the actual hook in the project root and run it."""
    # Get the hook name from the script name
    hook_name = Path(sys.argv[0]).name

    # Find project root
    current = Path.cwd()
    while current != current.parent:
        if (current / 'CLAUDE.md').exists() or (current / '.git').exists():
            hook_path = current / '.claude' / 'hooks' / hook_name
            if hook_path.exists():
                # Add hooks directory to path for imports
                sys.path.insert(0, str(hook_path.parent))
                sys.path.insert(0, str(hook_path.parent / 'utils'))

                # Execute the hook
                with open(hook_path) as f:
                    code = compile(f.read(), str(hook_path), 'exec')
                    exec(code, {'__file__': str(hook_path), '__name__': '__main__'})
                return

        current = current.parent

    # Fallback to known location
    project_root = Path('/home/daihungpham/__projects__/4genthub')
    hook_path = project_root / '.claude' / 'hooks' / hook_name
    if hook_path.exists():
        sys.path.insert(0, str(hook_path.parent))
        sys.path.insert(0, str(hook_path.parent / 'utils'))
        with open(hook_path) as f:
            code = compile(f.read(), str(hook_path), 'exec')
            exec(code, {'__file__': str(hook_path), '__name__': '__main__'})
    else:
        print(f"Error: Could not find hook {hook_name}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    find_and_run_hook()