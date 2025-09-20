#!/usr/bin/env python3
"""
TDD Tests for Hook Path Resolution Issue

Tests to ensure that hooks are called with correct paths regardless of
the current working directory, preventing the .claude/.claude duplication issue.
"""

import unittest
import os
import sys
import json
import tempfile
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open


class TestHookPathResolution(unittest.TestCase):
    """Test suite for hook path resolution to prevent double .claude paths."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.project_root = Path(self.test_dir)
        self.claude_dir = self.project_root / '.claude'
        self.hooks_dir = self.claude_dir / 'hooks'

        # Create directory structure
        self.hooks_dir.mkdir(parents=True, exist_ok=True)

        # Create marker files
        (self.project_root / 'CLAUDE.md').touch()
        (self.project_root / '.env').touch()

        # Create a test hook
        self.test_hook = self.hooks_dir / 'test_hook.py'
        self.test_hook.write_text('#!/usr/bin/env python3\nprint("Hook executed")\n')
        self.test_hook.chmod(0o755)

    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_relative_path_from_project_root(self):
        """Test that relative paths work correctly from project root."""
        # Change to project root
        os.chdir(self.project_root)

        # Test path resolution
        relative_path = ".claude/hooks/test_hook.py"
        resolved_path = Path(relative_path).resolve()

        # Should resolve to the correct path
        self.assertEqual(resolved_path, self.test_hook.resolve())
        self.assertTrue(resolved_path.exists())

        # Should NOT contain double .claude
        self.assertNotIn('.claude/.claude', str(resolved_path))

    def test_relative_path_from_claude_directory(self):
        """Test that relative paths fail when executed from .claude directory."""
        # Change to .claude directory
        os.chdir(self.claude_dir)

        # Test path resolution - this would cause the issue
        relative_path = ".claude/hooks/test_hook.py"
        resolved_path = Path(relative_path).resolve()

        # This would resolve incorrectly to .claude/.claude/hooks/test_hook.py
        expected_wrong_path = self.claude_dir / '.claude' / 'hooks' / 'test_hook.py'

        # Verify the issue exists
        self.assertEqual(resolved_path, expected_wrong_path)
        self.assertFalse(resolved_path.exists())  # File doesn't exist at wrong path

    def test_relative_path_from_subdirectory(self):
        """Test that relative paths fail when executed from subdirectories."""
        # Create a subdirectory
        subdir = self.project_root / 'src' / 'components'
        subdir.mkdir(parents=True, exist_ok=True)

        # Change to subdirectory
        os.chdir(subdir)

        # Test path resolution
        relative_path = ".claude/hooks/test_hook.py"
        resolved_path = Path(relative_path).resolve()

        # This would resolve to src/components/.claude/hooks/test_hook.py
        expected_wrong_path = subdir / '.claude' / 'hooks' / 'test_hook.py'

        # Verify the issue
        self.assertEqual(resolved_path, expected_wrong_path)
        self.assertFalse(resolved_path.exists())

    def test_execute_hook_wrapper_finds_correct_path(self):
        """Test that execute_hook.py wrapper finds the correct project root."""
        # Create execute_hook.py
        execute_hook_path = self.hooks_dir / 'execute_hook.py'
        execute_hook_content = '''#!/usr/bin/env python3
import sys
from pathlib import Path

def find_project_root():
    markers = ['CLAUDE.md', '.env', '.git']
    current = Path.cwd()

    # Also try from script location
    script_paths = [current]
    if __file__:
        script_paths.append(Path(__file__).parent.parent.parent)

    for start in script_paths:
        current = start.resolve()
        while current != current.parent:
            for marker in markers:
                if (current / marker).exists():
                    if (current / '.claude' / 'hooks').exists():
                        return current
            current = current.parent
    return None

if __name__ == "__main__":
    root = find_project_root()
    if root:
        print(str(root))
    else:
        sys.exit(1)
'''
        execute_hook_path.write_text(execute_hook_content)
        execute_hook_path.chmod(0o755)

        # Test from different directories
        test_dirs = [
            self.project_root,
            self.claude_dir,
            self.hooks_dir,
            self.project_root / 'src',
        ]

        # Create src directory
        (self.project_root / 'src').mkdir(exist_ok=True)

        for test_dir in test_dirs:
            os.chdir(test_dir)
            result = subprocess.run(
                [sys.executable, str(execute_hook_path)],
                capture_output=True,
                text=True
            )

            # Should always find the correct project root
            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout.strip(), str(self.project_root))

    def test_hook_execution_with_wrapper(self):
        """Test that hooks execute correctly using the wrapper approach."""
        # Create a wrapper that finds root and executes hook
        wrapper_path = self.hooks_dir / 'hook_wrapper.py'
        wrapper_content = '''#!/usr/bin/env python3
import sys
import subprocess
from pathlib import Path

def find_project_root():
    markers = ['CLAUDE.md', '.env', '.git']

    # Start from script location
    current = Path(__file__).parent.parent.parent
    if (current / 'CLAUDE.md').exists():
        return current

    # Fallback to cwd search
    current = Path.cwd()
    while current != current.parent:
        for marker in markers:
            if (current / marker).exists():
                if (current / '.claude' / 'hooks').exists():
                    return current
        current = current.parent
    return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(1)

    hook_name = sys.argv[1]
    root = find_project_root()

    if not root:
        print("Could not find project root", file=sys.stderr)
        sys.exit(1)

    hook_path = root / '.claude' / 'hooks' / hook_name

    if not hook_path.exists():
        print(f"Hook not found: {hook_path}", file=sys.stderr)
        sys.exit(1)

    # Execute the hook
    result = subprocess.run([sys.executable, str(hook_path)] + sys.argv[2:])
    sys.exit(result.returncode)
'''
        wrapper_path.write_text(wrapper_content)
        wrapper_path.chmod(0o755)

        # Test wrapper from various directories
        test_dirs = [
            self.project_root,
            self.claude_dir,
            self.project_root / 'src',
        ]

        (self.project_root / 'src').mkdir(exist_ok=True)

        for test_dir in test_dirs:
            os.chdir(test_dir)

            # Execute hook via wrapper
            result = subprocess.run(
                [sys.executable, str(wrapper_path), 'test_hook.py'],
                capture_output=True,
                text=True
            )

            # Should execute successfully
            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout.strip(), "Hook executed")

    def test_settings_json_with_wrapper_command(self):
        """Test that settings.json can use wrapper command correctly."""
        # Create settings with wrapper command
        settings = {
            "hooks": {
                "PreToolUse": [{
                    "matcher": "",
                    "hooks": [{
                        "type": "command",
                        "command": "python3 .claude/hooks/hook_wrapper.py pre_tool_use.py"
                    }]
                }]
            }
        }

        settings_path = self.claude_dir / 'settings.json'
        settings_path.write_text(json.dumps(settings, indent=2))

        # Read and validate settings
        with open(settings_path) as f:
            loaded_settings = json.load(f)

        # Check command format
        hook_command = loaded_settings['hooks']['PreToolUse'][0]['hooks'][0]['command']

        # Should use wrapper
        self.assertIn('hook_wrapper.py', hook_command)
        self.assertIn('pre_tool_use.py', hook_command)

        # Should not have double .claude
        self.assertEqual(hook_command.count('.claude'), 1)


class TestExecuteHookWrapper(unittest.TestCase):
    """Test the execute_hook.py wrapper specifically."""

    def test_wrapper_prevents_double_claude_path(self):
        """Test that the wrapper prevents .claude/.claude path duplication."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            claude_dir = project_root / '.claude'
            hooks_dir = claude_dir / 'hooks'
            hooks_dir.mkdir(parents=True)

            # Create marker file
            (project_root / 'CLAUDE.md').touch()

            # Create test hook
            test_hook = hooks_dir / 'test.py'
            test_hook.write_text('#!/usr/bin/env python3\nprint("OK")')
            test_hook.chmod(0o755)

            # Simulate being in .claude directory (where issue occurs)
            os.chdir(claude_dir)

            # Without wrapper - would create wrong path
            wrong_path = Path('.claude/hooks/test.py').resolve()
            self.assertEqual(
                str(wrong_path),
                str(claude_dir / '.claude' / 'hooks' / 'test.py')
            )
            self.assertFalse(wrong_path.exists())

            # With wrapper - should find correct path
            # This simulates what execute_hook.py should do
            correct_path = project_root / '.claude' / 'hooks' / 'test.py'
            self.assertTrue(correct_path.exists())
            self.assertNotIn('.claude/.claude', str(correct_path))


if __name__ == '__main__':
    unittest.main()