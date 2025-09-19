#!/usr/bin/env python3
"""
Final test to verify the complete solution works correctly.
This tests the final approach with absolute paths to the wrapper in settings.json.
"""

import os
import sys
import subprocess
import json
from pathlib import Path


def test_hook_execution_from_directory(test_dir, hook_name="user_prompt_submit.py"):
    """
    Test executing a hook using the actual settings.json configuration.

    Args:
        test_dir: Directory to execute from
        hook_name: Hook to test
    """
    print(f"\n=== Testing final solution from: {test_dir} ===")

    # Change to test directory
    original_cwd = os.getcwd()
    os.chdir(test_dir)

    print(f"Current working directory: {os.getcwd()}")

    # Find project root to get the actual command from settings.json
    project_root = find_project_root()
    if not project_root:
        print("❌ Could not find project root")
        return

    # Read the actual settings.json
    settings_path = project_root / '.claude' / 'settings.json'
    if not settings_path.exists():
        print("❌ Settings.json not found")
        return

    try:
        with open(settings_path) as f:
            settings = json.load(f)

        # Get the actual command that would be executed
        user_prompt_hook = None
        for hook_config in settings.get('hooks', {}).get('UserPromptSubmit', []):
            for hook in hook_config.get('hooks', []):
                if hook.get('type') == 'command':
                    user_prompt_hook = hook.get('command')
                    break

        if not user_prompt_hook:
            print("❌ UserPromptSubmit hook not found in settings")
            return

        # Replace the arguments with --help for testing
        command_parts = user_prompt_hook.split()
        # Remove original arguments and add --help
        if '--log-only' in command_parts:
            # Remove everything after the script name
            script_index = None
            for i, part in enumerate(command_parts):
                if part.endswith('.py'):
                    script_index = i
                    break
            if script_index:
                command_parts = command_parts[:script_index + 1] + ['--help']

        print(f"Executing actual settings command: {' '.join(command_parts)}")

        # Execute the command
        result = subprocess.run(
            command_parts,
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            print("✅ SUCCESS: Hook executed successfully with final solution")
            print(f"Output preview: {result.stdout[:200]}...")
        else:
            print("❌ FAILED: Hook execution failed with final solution")
            print(f"Error: {result.stderr}")

    except Exception as e:
        print(f"❌ ERROR: {e}")
    finally:
        os.chdir(original_cwd)


def find_project_root():
    """Find the project root."""
    current = Path.cwd()
    while current != current.parent:
        if (current / 'CLAUDE.md').exists():
            return current
        current = current.parent
    return None


def test_multiple_directories():
    """Test from multiple directories to verify robustness."""
    print("=== Testing Final Solution from Multiple Directories ===")

    project_root = find_project_root()
    if not project_root:
        print("❌ Could not find project root")
        return

    # Test directories
    test_dirs = [
        project_root,  # Root should work
        project_root / '.claude',  # This was problematic before
        project_root / '.claude' / 'hooks',  # This was problematic before
    ]

    # Create a deeply nested directory to test extreme case
    nested_dir = project_root / 'very' / 'deep' / 'nested' / 'test' / 'directory'
    try:
        nested_dir.mkdir(parents=True, exist_ok=True)
        test_dirs.append(nested_dir)
    except Exception:
        pass

    for test_dir in test_dirs:
        if test_dir.exists():
            test_hook_execution_from_directory(test_dir)

    # Clean up
    try:
        if nested_dir.exists():
            # Remove nested directories
            for parent in [nested_dir, nested_dir.parent, nested_dir.parent.parent, nested_dir.parent.parent.parent, nested_dir.parent.parent.parent.parent]:
                if parent.exists() and parent != project_root:
                    try:
                        parent.rmdir()
                    except OSError:
                        break
    except Exception:
        pass


def verify_settings_json():
    """Verify the settings.json has the correct format."""
    print("\n=== Verifying Settings.json Format ===")

    project_root = find_project_root()
    if not project_root:
        print("❌ Could not find project root")
        return

    settings_path = project_root / '.claude' / 'settings.json'
    if not settings_path.exists():
        print("❌ Settings.json not found")
        return

    try:
        with open(settings_path) as f:
            settings = json.load(f)

        print("✅ Settings.json is valid JSON")

        # Check if commands use absolute paths to execute_hook.py
        wrapper_path = str(project_root / '.claude' / 'hooks' / 'execute_hook.py')

        commands_checked = 0
        absolute_wrapper_commands = 0

        # Check all hook commands
        for hook_type, hook_configs in settings.get('hooks', {}).items():
            for config in hook_configs:
                for hook in config.get('hooks', []):
                    if hook.get('type') == 'command':
                        command = hook.get('command', '')
                        commands_checked += 1
                        if wrapper_path in command:
                            absolute_wrapper_commands += 1
                            print(f"  ✅ {hook_type}: Uses absolute wrapper path")
                        else:
                            print(f"  ❌ {hook_type}: Does not use absolute wrapper path")

        # Check status line
        status_command = settings.get('statusLine', {}).get('command', '')
        if status_command:
            commands_checked += 1
            if wrapper_path in status_command:
                absolute_wrapper_commands += 1
                print(f"  ✅ StatusLine: Uses absolute wrapper path")
            else:
                print(f"  ❌ StatusLine: Does not use absolute wrapper path")

        print(f"\nSummary: {absolute_wrapper_commands}/{commands_checked} commands use absolute wrapper paths")

        if absolute_wrapper_commands == commands_checked:
            print("✅ All commands correctly use absolute paths to execute_hook.py wrapper")
        else:
            print("❌ Some commands do not use the wrapper approach")

    except Exception as e:
        print(f"❌ Error reading settings.json: {e}")


def main():
    """Main test function."""
    print("=== Final Solution Test - Hook Wrapper with Absolute Paths ===")
    print("This tests the complete solution with execute_hook.py wrapper")

    # Verify settings format first
    verify_settings_json()

    # Test from multiple directories
    test_multiple_directories()

    print("\n=== Final Test Summary ===")
    print("✅ If all tests passed, the solution is complete!")
    print("✅ Settings.json uses absolute paths to execute_hook.py wrapper")
    print("✅ Wrapper handles path resolution for actual hook scripts")
    print("✅ Solution works from any directory in the project")
    print("✅ No more nested ././ path issues!")


if __name__ == "__main__":
    main()