#!/usr/bin/env python3
"""
Test script to verify that the execute_hook.py wrapper solution works correctly.
This tests the new approach that uses a wrapper to handle path resolution.
"""

import os
import sys
import subprocess
from pathlib import Path


def test_wrapper_execution_from_directory(test_dir, hook_name="user_prompt_submit.py"):
    """
    Test executing a hook using the wrapper from a specific directory.

    Args:
        test_dir: Directory to execute the wrapper from
        hook_name: Name of the hook to test
    """
    print(f"\n=== Testing wrapper execution from: {test_dir} ===")

    # Change to test directory
    original_cwd = os.getcwd()
    os.chdir(test_dir)

    print(f"Current working directory: {os.getcwd()}")

    # Test the wrapper approach that would be in settings.json
    wrapper_command = ["python3", "./.claude/hooks/execute_hook.py", hook_name, "--help"]
    print(f"Attempting to execute: {' '.join(wrapper_command)}")

    try:
        # This simulates what Claude Code would do with our new settings
        result = subprocess.run(
            wrapper_command,
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            print("✅ SUCCESS: Hook executed successfully via wrapper")
            print(f"Output preview: {result.stdout[:200]}...")
        else:
            print("❌ FAILED: Hook execution failed via wrapper")
            print(f"Error: {result.stderr}")

    except subprocess.TimeoutExpired:
        print("⏱️ TIMEOUT: Hook execution timed out")
    except FileNotFoundError as e:
        print(f"❌ FILE NOT FOUND: {e}")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    finally:
        # Restore original directory
        os.chdir(original_cwd)


def test_status_line_wrapper():
    """Test the status line wrapper specifically."""
    print("\n=== Testing Status Line Wrapper ===")

    # Find project root
    current = Path(__file__).parent
    project_root = None

    while current != current.parent:
        if (current / 'CLAUDE.md').exists():
            project_root = current
            break
        current = current.parent

    if not project_root:
        print("❌ Could not find project root!")
        return

    # Test from a subdirectory
    temp_subdir = project_root / 'temp_test_subdir'
    try:
        temp_subdir.mkdir(exist_ok=True)
        original_cwd = os.getcwd()
        os.chdir(temp_subdir)

        print(f"Testing status line from: {temp_subdir}")

        # Test status line wrapper command (as it would appear in settings.json)
        wrapper_command = ["python3", "./.claude/hooks/execute_hook.py", "status_line_mcp.py"]
        print(f"Attempting to execute: {' '.join(wrapper_command)}")

        try:
            result = subprocess.run(
                wrapper_command,
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                print("✅ SUCCESS: Status line executed successfully via wrapper")
            else:
                print("❌ FAILED: Status line execution failed")
                print(f"Error: {result.stderr}")

        except Exception as e:
            print(f"❌ ERROR: {e}")
        finally:
            os.chdir(original_cwd)

    except Exception as e:
        print(f"❌ Could not test status line: {e}")
    finally:
        # Clean up
        try:
            if temp_subdir.exists():
                temp_subdir.rmdir()
        except Exception:
            pass


def test_all_hooks_with_wrapper():
    """Test multiple hooks with the wrapper approach."""
    print("\n=== Testing Multiple Hooks with Wrapper ===")

    # Find project root
    current = Path(__file__).parent
    project_root = None

    while current != current.parent:
        if (current / 'CLAUDE.md').exists():
            project_root = current
            break
        current = current.parent

    if not project_root:
        print("❌ Could not find project root!")
        return

    # List of hooks to test (with --help to avoid side effects)
    hooks_to_test = [
        ("user_prompt_submit.py", ["--help"]),
        ("session_start.py", ["--help"]),
        ("notification.py", ["--help"]),
        ("stop.py", ["--help"]),
    ]

    # Test from a problematic subdirectory
    temp_subdir = project_root / 'nested' / 'test' / 'dir'
    try:
        temp_subdir.mkdir(parents=True, exist_ok=True)
        original_cwd = os.getcwd()
        os.chdir(temp_subdir)

        print(f"Testing from deeply nested directory: {temp_subdir}")

        for hook_name, args in hooks_to_test:
            print(f"\n  Testing {hook_name}...")

            wrapper_command = ["python3", "./.claude/hooks/execute_hook.py", hook_name] + args

            try:
                result = subprocess.run(
                    wrapper_command,
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                if result.returncode == 0:
                    print(f"    ✅ {hook_name} executed successfully")
                else:
                    print(f"    ❌ {hook_name} failed: {result.stderr[:100]}...")

            except Exception as e:
                print(f"    ❌ {hook_name} error: {e}")

    except Exception as e:
        print(f"❌ Could not test multiple hooks: {e}")
    finally:
        # Clean up
        try:
            os.chdir(original_cwd)
            if temp_subdir.exists():
                temp_subdir.rmdir()
                (temp_subdir.parent / 'test').rmdir()
                (temp_subdir.parent.parent / 'nested').rmdir()
        except Exception:
            pass


def main():
    """Main test function."""
    print("=== Claude Hook Wrapper Solution Test ===")
    print("Testing the execute_hook.py wrapper approach...")

    # Find project root
    current = Path(__file__).parent
    project_root = None

    while current != current.parent:
        if (current / 'CLAUDE.md').exists():
            project_root = current
            break
        current = current.parent

    if not project_root:
        print("❌ Could not find project root!")
        return

    print(f"Project root found: {project_root}")

    # Test from project root (should work)
    test_wrapper_execution_from_directory(project_root)

    # Test from problematic subdirectories
    test_subdirs = [
        project_root / '.claude',
        project_root / '.claude' / 'hooks',
    ]

    # Create a temporary deeply nested subdirectory
    temp_subdir = project_root / 'very' / 'deep' / 'nested' / 'subdir'
    try:
        temp_subdir.mkdir(parents=True, exist_ok=True)
        test_subdirs.append(temp_subdir)
    except Exception:
        pass

    for subdir in test_subdirs:
        if subdir.exists():
            test_wrapper_execution_from_directory(subdir)

    # Test status line specifically
    test_status_line_wrapper()

    # Test multiple hooks
    test_all_hooks_with_wrapper()

    # Clean up
    try:
        if temp_subdir.exists():
            # Remove the nested structure
            for parent in [temp_subdir, temp_subdir.parent, temp_subdir.parent.parent, temp_subdir.parent.parent.parent]:
                if parent.exists() and parent != project_root:
                    try:
                        parent.rmdir()
                    except OSError:
                        break
    except Exception:
        pass

    print("\n=== Test Summary ===")
    print("✅ If all tests passed, the wrapper solution fixes the path resolution issue!")
    print("✅ The settings.json can now use relative paths that work from any directory")
    print("✅ The execute_hook.py wrapper handles all path resolution automatically")


if __name__ == "__main__":
    main()