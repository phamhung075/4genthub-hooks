#!/usr/bin/env python3
"""
Script to find project root dynamically and construct paths.
Works from any subdirectory within the project.
"""

import os
import sys
from pathlib import Path
from typing import Optional, List

class ProjectRootFinder:
    """Utility class to find project root and construct paths."""

    # Marker files that indicate project root
    MARKER_FILES = [
        '.git',
        'package.json',
        'CLAUDE.md',
        '.env',
        'docker-compose.yml',
        'pyproject.toml',
        'setup.py',
        'requirements.txt'
    ]

    def __init__(self, start_path: Optional[str] = None):
        """
        Initialize the finder.

        Args:
            start_path: Directory to start search from (defaults to current dir)
        """
        self.start_path = Path(start_path or os.getcwd()).resolve()
        self._project_root = None

    def find_project_root(self) -> Optional[Path]:
        """
        Find the project root by looking for marker files.
        Prefers the highest level directory with CLAUDE.md file.

        Returns:
            Path to project root or None if not found
        """
        if self._project_root:
            return self._project_root

        current_dir = self.start_path
        found_roots = []

        # Search upward and collect all potential roots
        while current_dir != current_dir.parent:
            # Check for CLAUDE.md first (most specific marker)
            if (current_dir / 'CLAUDE.md').exists():
                found_roots.append(current_dir)

            # Check for other marker files
            for marker in self.MARKER_FILES:
                if (current_dir / marker).exists():
                    # Don't add duplicates
                    if current_dir not in found_roots:
                        found_roots.append(current_dir)
                    break

            # Go up one directory
            current_dir = current_dir.parent

        # Prefer the root with CLAUDE.md file
        for root in found_roots:
            if (root / 'CLAUDE.md').exists() and (root / '.env.dev').exists():
                self._project_root = root
                return self._project_root

        # Fallback to first found root
        if found_roots:
            self._project_root = found_roots[0]
            return self._project_root

        return None

    def get_absolute_path(self, relative_path: str) -> Optional[Path]:
        """
        Get absolute path from project root.

        Args:
            relative_path: Path relative to project root

        Returns:
            Absolute path or None if project root not found
        """
        root = self.find_project_root()
        if not root:
            return None

        # Remove leading slash if present
        relative_path = relative_path.lstrip('/')
        return root / relative_path

    def get_project_paths(self) -> dict:
        """
        Get common project paths.

        Returns:
            Dictionary of common project paths
        """
        root = self.find_project_root()
        if not root:
            return {}

        paths = {
            'root': root,
            'hooks': root / '.claude' / 'hooks',
            'scripts': root / 'scripts',
            'docker': root / 'docker-system',
            'ai_docs': root / 'ai_docs',
            'backend': root / 'agenthub_main',
            'frontend': root / 'agenthub-frontend',
            'tests': root / 'agenthub_main' / 'src' / 'tests',
            'env_file': root / '.env',
            'claude_md': root / 'CLAUDE.md',
            'claude_local': root / 'CLAUDE.local.md'
        }

        # Only include paths that exist
        return {k: v for k, v in paths.items() if v.exists()}


def main():
    """Main entry point for script."""
    finder = ProjectRootFinder()

    # Find project root
    project_root = finder.find_project_root()

    if not project_root:
        print("Error: Could not find project root", file=sys.stderr)
        sys.exit(1)

    print(f"Project Root: {project_root}")
    print("-" * 50)

    # Get all project paths
    paths = finder.get_project_paths()

    for name, path in paths.items():
        print(f"{name.capitalize()}: {path}")

    # Example of getting specific path
    print("-" * 50)
    print("Example usage:")

    # Get path relative to project root
    example_path = finder.get_absolute_path("ai_docs/index.json")
    if example_path:
        print(f"ai_docs/index.json: {example_path}")

    # Export as environment variables if requested
    if '--export' in sys.argv:
        print("-" * 50)
        print("Export commands (copy and run in shell):")
        for name, path in paths.items():
            env_name = f"PROJECT_{name.upper()}"
            print(f"export {env_name}='{path}'")


if __name__ == "__main__":
    main()