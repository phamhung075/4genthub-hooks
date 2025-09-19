#!/usr/bin/env python3
"""
Test script to verify that path resolution works correctly with relative paths.
This simulates how Claude Code would execute hooks from different directories.
"""

import os
import sys
import subprocess
from pathlib import Path


def test_hook_execution_from_directory(test_dir, hook_name="user_prompt_submit.py"):
    """
    Test executing a hook from a specific directory.

    Args:
        test_dir: Directory to execute the hook from
        hook_name: Name of the hook to test
    """
    print(f"\n=== Testing hook execution from: {test_dir} ===")

    # Change to test directory
    original_cwd = os.getcwd()
    os.chdir(test_dir)

    print(f"Current working directory: {os.getcwd()}")

    # Test the relative path that would be in settings.json
    relative_hook_path = "./.claude/hooks/" + hook_name
    print(f"Attempting to execute: python3 {relative_hook_path} --help")

    try:
        # This simulates what Claude Code would do
        result = subprocess.run(
            ["python3", relative_hook_path, "--help"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            print("✅ SUCCESS: Hook executed successfully")
            print(f"Output preview: {result.stdout[:200]}...")
        else:
            print("❌ FAILED: Hook execution failed")
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


def test_path_resolver_utility():
    """Test our path resolver utility."""
    print("\n=== Testing PathResolver Utility ===")

    try:
        # Import our utility
        sys.path.insert(0, str(Path(__file__).parent / 'utils'))
        from path_resolver import PathResolver

        resolver = PathResolver(debug=True)
        project_info = resolver.get_project_info()

        print("PathResolver results:")
        for key, value in project_info.items():
            print(f"  {key}: {value}")

        if resolver.get_project_root():
            print("✅ PathResolver successfully found project root")
        else:
            print("❌ PathResolver failed to find project root")

    except ImportError as e:
        print(f"❌ Failed to import PathResolver: {e}")
    except Exception as e:
        print(f"❌ PathResolver error: {e}")


def main():
    """Main test function."""
    print("=== Claude Hook Path Resolution Test ===")

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

    # Test from project root
    test_hook_execution_from_directory(project_root)

    # Test from a subdirectory (simulating the original problem)
    test_subdirs = [
        project_root / '.claude',
        project_root / '.claude' / 'hooks',
    ]

    # Create a temporary subdirectory to test the problematic scenario
    temp_subdir = project_root / 'temp_test_subdir'
    try:
        temp_subdir.mkdir(exist_ok=True)
        test_subdirs.append(temp_subdir)
    except Exception:
        pass

    for subdir in test_subdirs:
        if subdir.exists():
            test_hook_execution_from_directory(subdir)

    # Clean up
    try:
        if temp_subdir.exists():
            temp_subdir.rmdir()
    except Exception:
        pass

    # Test our path resolver utility
    test_path_resolver_utility()

    print("\n=== Test Summary ===")
    print("If hooks executed successfully from all directories, the path resolution is working!")
    print("If any failed, we need to implement additional fixes.")


if __name__ == "__main__":
    main()