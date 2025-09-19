#!/usr/bin/env python3
"""
Path Resolver Utility - Ensures hooks work correctly regardless of execution context.

This utility provides robust path resolution for Claude hooks that need to work
when called from any directory within the project. It solves the issue where
relative paths in .claude/settings.json cause nested ././ path problems.

Key Features:
- Automatically finds the correct project root
- Resolves paths relative to project root, not current directory
- Provides centralized path management for all hooks
- Maintains compatibility with existing hook code
- Ensures hooks work from any subdirectory

Usage in hooks:
    from utils.path_resolver import PathResolver

    # Initialize at the start of your hook
    resolver = PathResolver()

    # Get properly resolved paths
    project_root = resolver.get_project_root()
    hooks_dir = resolver.get_hooks_dir()
    utils_dir = resolver.get_utils_dir()

    # Ensure working directory is correct
    resolver.ensure_correct_working_directory()
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any


class PathResolver:
    """Utility class for resolving paths correctly in Claude hooks."""

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

    def __init__(self, debug: bool = False):
        """
        Initialize the path resolver.

        Args:
            debug: Enable debug logging
        """
        self._project_root = None
        self._original_cwd = os.getcwd()
        self._debug = debug or os.getenv('CLAUDE_HOOK_DEBUG', '').lower() in ('1', 'true', 'yes')

        # Automatically find project root on initialization
        self._find_project_root()

    def _log_debug(self, message: str):
        """Log debug information if debugging is enabled."""
        if self._debug:
            print(f"[PATH_RESOLVER_DEBUG] {message}", file=sys.stderr)

    def _find_project_root(self) -> Optional[Path]:
        """
        Find the project root by looking for marker files.

        Returns:
            Path to project root or None if not found
        """
        if self._project_root:
            return self._project_root

        # Start from script location (where this utility is called from)
        start_paths = []

        # Try to determine starting point from the calling script
        if hasattr(sys, '_getframe'):
            try:
                # Get the caller's filename
                caller_frame = sys._getframe(1)
                caller_file = caller_frame.f_globals.get('__file__')
                if caller_file:
                    start_paths.append(Path(caller_file).parent)
            except (AttributeError, ValueError):
                pass

        # Add additional starting points
        start_paths.extend([
            Path(__file__).parent.parent.parent,  # From utils -> hooks -> .claude -> project
            Path.cwd(),
            Path(__file__).parent.parent if __file__ else Path.cwd()
        ])

        self._log_debug(f"Starting search from paths: {start_paths}")

        for start in start_paths:
            try:
                current = start.resolve()
                self._log_debug(f"Searching upward from: {current}")

                # Walk up the directory tree
                while current != current.parent:
                    self._log_debug(f"Checking directory: {current}")

                    # Check for marker files in priority order
                    for marker in self.MARKER_FILES:
                        marker_path = current / marker
                        if marker_path.exists():
                            self._log_debug(f"Found marker: {marker_path}")

                            # Verify it's a Claude project by checking for .claude/hooks
                            claude_hooks = current / '.claude' / 'hooks'
                            if claude_hooks.exists():
                                self._log_debug(f"Confirmed Claude project root: {current}")
                                self._project_root = current
                                return self._project_root
                            else:
                                self._log_debug(f"Found {marker} but no .claude/hooks directory")

                    current = current.parent

            except (OSError, PermissionError) as e:
                self._log_debug(f"Error accessing {start}: {e}")
                continue

        self._log_debug("Project root not found")
        return None

    def get_project_root(self) -> Optional[Path]:
        """
        Get the project root directory.

        Returns:
            Path to project root or None if not found
        """
        return self._project_root

    def get_hooks_dir(self) -> Optional[Path]:
        """
        Get the .claude/hooks directory.

        Returns:
            Path to hooks directory or None if not found
        """
        if not self._project_root:
            return None
        return self._project_root / '.claude' / 'hooks'

    def get_utils_dir(self) -> Optional[Path]:
        """
        Get the .claude/hooks/utils directory.

        Returns:
            Path to utils directory or None if not found
        """
        hooks_dir = self.get_hooks_dir()
        if not hooks_dir:
            return None
        return hooks_dir / 'utils'

    def get_claude_dir(self) -> Optional[Path]:
        """
        Get the .claude directory.

        Returns:
            Path to .claude directory or None if not found
        """
        if not self._project_root:
            return None
        return self._project_root / '.claude'

    def resolve_path(self, relative_path: str) -> Optional[Path]:
        """
        Resolve a path relative to project root.

        Args:
            relative_path: Path relative to project root

        Returns:
            Absolute path or None if project root not found
        """
        if not self._project_root:
            return None

        # Clean up the relative path
        path_str = str(relative_path)
        if path_str.startswith('./'):
            path_str = path_str[2:]
        elif path_str.startswith('.\\'):  # Windows
            path_str = path_str[2:]

        # Remove any leading slashes
        path_str = path_str.lstrip('/').lstrip('\\')

        # Construct absolute path
        absolute_path = self._project_root / path_str

        self._log_debug(f"Resolved '{relative_path}' to '{absolute_path}'")
        return absolute_path

    def ensure_correct_working_directory(self):
        """
        Ensure the current working directory is set to project root.
        This is important for hooks that rely on relative imports or file paths.
        """
        if not self._project_root:
            self._log_debug("Cannot change to project root - not found")
            return

        current_cwd = Path.cwd()
        if current_cwd != self._project_root:
            self._log_debug(f"Changing working directory from {current_cwd} to {self._project_root}")
            os.chdir(self._project_root)
        else:
            self._log_debug(f"Already in correct working directory: {current_cwd}")

    def add_paths_to_sys_path(self):
        """
        Add necessary paths to sys.path for proper imports.
        This ensures hooks can import their utilities regardless of execution context.
        """
        paths_to_add = []

        hooks_dir = self.get_hooks_dir()
        if hooks_dir and hooks_dir.exists():
            paths_to_add.append(str(hooks_dir))

        utils_dir = self.get_utils_dir()
        if utils_dir and utils_dir.exists():
            paths_to_add.append(str(utils_dir))

        # Add to sys.path if not already present
        for path in paths_to_add:
            if path not in sys.path:
                sys.path.insert(0, path)
                self._log_debug(f"Added to sys.path: {path}")

    def get_project_info(self) -> Dict[str, Any]:
        """
        Get comprehensive project information.

        Returns:
            Dictionary with project paths and status
        """
        info = {
            'project_root': str(self._project_root) if self._project_root else None,
            'hooks_dir': str(self.get_hooks_dir()) if self.get_hooks_dir() else None,
            'utils_dir': str(self.get_utils_dir()) if self.get_utils_dir() else None,
            'claude_dir': str(self.get_claude_dir()) if self.get_claude_dir() else None,
            'original_cwd': self._original_cwd,
            'current_cwd': os.getcwd(),
            'project_found': self._project_root is not None
        }
        return info

    def __str__(self):
        """String representation of the resolver state."""
        return f"PathResolver(project_root={self._project_root}, debug={self._debug})"


def initialize_hook_environment(debug: bool = False) -> PathResolver:
    """
    Initialize the hook execution environment.

    This is a convenience function that:
    1. Creates a PathResolver instance
    2. Sets correct working directory
    3. Adds necessary paths to sys.path

    Args:
        debug: Enable debug logging

    Returns:
        PathResolver instance

    Usage at the start of any hook:
        from utils.path_resolver import initialize_hook_environment

        resolver = initialize_hook_environment()
        if not resolver.get_project_root():
            print("Error: Could not find project root", file=sys.stderr)
            sys.exit(1)
    """
    resolver = PathResolver(debug=debug)

    if not resolver.get_project_root():
        return resolver

    # Set up the environment
    resolver.ensure_correct_working_directory()
    resolver.add_paths_to_sys_path()

    return resolver


# For backward compatibility and convenience
def get_project_root() -> Optional[Path]:
    """Quick function to get project root."""
    resolver = PathResolver()
    return resolver.get_project_root()


if __name__ == "__main__":
    # Test the path resolver
    resolver = PathResolver(debug=True)

    print("=== Path Resolver Test ===")
    project_info = resolver.get_project_info()

    for key, value in project_info.items():
        print(f"{key}: {value}")

    if resolver.get_project_root():
        print("\n=== Testing path resolution ===")
        test_paths = [
            "./.claude/hooks/session_start.py",
            "ai_docs/index.json",
            ".env.dev"
        ]

        for path in test_paths:
            resolved = resolver.resolve_path(path)
            exists = resolved.exists() if resolved else False
            print(f"{path} -> {resolved} (exists: {exists})")
    else:
        print("Error: Could not find project root!")