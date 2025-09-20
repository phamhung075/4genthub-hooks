#!/usr/bin/env python3
"""
Test script to verify all hooks work correctly after path fixes.
This script tests hooks from both project root and .claude directory.
"""

import subprocess
import sys
import os
from pathlib import Path


def test_hook_execution(hook_name, cwd_path):
    """Test execution of a specific hook from a given directory."""
    try:
        cmd = [sys.executable, "hooks/execute_hook.py", hook_name]
        result = subprocess.run(
            cmd,
            cwd=cwd_path,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0, result.stderr
    except subprocess.TimeoutExpired:
        return False, "Timeout expired"
    except Exception as e:
        return False, str(e)


def main():
    """Main test function."""
    project_root = Path(__file__).parent.parent.parent
    claude_dir = project_root / ".claude"

    # List of hooks to test
    hooks_to_test = [
        "pre_tool_use.py",
        "post_tool_use.py",
        "notification.py",
        "stop.py",
        "subagent_stop.py",
        "user_prompt_submit.py",
        "pre_compact.py",
        "session_start.py"
    ]

    print("🧪 Testing Claude Code hooks path configuration...")
    print(f"Project root: {project_root}")
    print(f"Claude dir: {claude_dir}")
    print()

    all_passed = True

    # Test from both directories to simulate different execution contexts
    test_dirs = [
        ("Project Root", project_root),
        ("Claude Directory", claude_dir)
    ]

    for dir_name, test_dir in test_dirs:
        print(f"📁 Testing from {dir_name}: {test_dir}")

        for hook_name in hooks_to_test:
            success, error_msg = test_hook_execution(hook_name, test_dir)

            if success:
                print(f"  ✅ {hook_name}")
            else:
                print(f"  ❌ {hook_name} - {error_msg}")
                all_passed = False

        print()

    if all_passed:
        print("🎉 All hooks are working correctly!")
        print("✅ Claude Code hooks path configuration issue has been resolved.")
        return 0
    else:
        print("❌ Some hooks are failing. Check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())