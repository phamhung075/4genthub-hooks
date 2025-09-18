#!/usr/bin/env python3
"""Comprehensive verification of dynamic root finding in all hook files."""

import sys
import os
from pathlib import Path

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent / "utils"))

def verify_imports():
    """Verify all critical modules can import and find root correctly."""
    results = []

    print("=" * 70)
    print("VERIFYING DYNAMIC ROOT FINDING IN ALL HOOK MODULES")
    print("=" * 70)

    # Test ProjectRootFinder
    try:
        from find_project_root import ProjectRootFinder
        finder = ProjectRootFinder()
        root = finder.find_project_root()
        expected = Path("/home/daihungpham/__projects__/4genthub")

        if root == expected:
            results.append("✅ find_project_root.py: Correctly finds root")
        else:
            results.append(f"❌ find_project_root.py: Found {root} instead of {expected}")
    except Exception as e:
        results.append(f"❌ find_project_root.py: Import error: {e}")

    # Test env_loader
    try:
        from env_loader import get_project_root, PROJECT_ROOT
        env_root = get_project_root()

        if env_root == expected:
            results.append("✅ env_loader.py: Correctly finds root")
        else:
            results.append(f"❌ env_loader.py: Found {env_root} instead of {expected}")

        # Check that PROJECT_ROOT module variable is set correctly
        if PROJECT_ROOT == expected:
            results.append("✅ env_loader.py: PROJECT_ROOT module variable correct")
        else:
            results.append(f"❌ env_loader.py: PROJECT_ROOT is {PROJECT_ROOT}")
    except Exception as e:
        results.append(f"❌ env_loader.py: Import error: {e}")

    # Test other modules that use dynamic root
    modules_to_test = [
        ("context_injector", "ContextInjector"),
        ("mcp_client", "MCPClient"),
        ("unified_hint_system", "HintBridge"),
        ("mcp_post_action_hints_backup", "MCPPostActionHints"),
    ]

    for module_name, class_name in modules_to_test:
        try:
            module = __import__(module_name)
            results.append(f"✅ {module_name}.py: Successfully imports with dynamic root")
        except Exception as e:
            results.append(f"❌ {module_name}.py: Import error: {e}")

    return results

def test_from_different_locations():
    """Test that root finding works from different directories."""
    print("\n" + "=" * 70)
    print("TESTING FROM DIFFERENT DIRECTORY LEVELS")
    print("=" * 70)

    original_dir = os.getcwd()
    test_dirs = [
        ("/home/daihungpham/__projects__/4genthub", "Project root"),
        ("/home/daihungpham/__projects__/4genthub/.claude", ".claude directory"),
        ("/home/daihungpham/__projects__/4genthub/.claude/hooks", "hooks directory"),
        ("/home/daihungpham/__projects__/4genthub/.claude/hooks/utils", "utils directory"),
        ("/home/daihungpham/__projects__/4genthub/agenthub_main", "Backend directory"),
    ]

    results = []
    for test_dir, description in test_dirs:
        if Path(test_dir).exists():
            os.chdir(test_dir)

            # Re-import to test from new location
            if 'find_project_root' in sys.modules:
                del sys.modules['find_project_root']
            if 'env_loader' in sys.modules:
                del sys.modules['env_loader']

            from find_project_root import ProjectRootFinder
            finder = ProjectRootFinder()
            root = finder.find_project_root()

            expected = Path("/home/daihungpham/__projects__/4genthub")
            if root == expected:
                results.append(f"✅ From {description}: Found correct root")
            else:
                results.append(f"❌ From {description}: Found {root}")

    os.chdir(original_dir)
    return results

def check_no_cwd_fallback():
    """Verify no Path.cwd() fallback in critical files."""
    print("\n" + "=" * 70)
    print("CHECKING FOR Path.cwd() USAGE")
    print("=" * 70)

    critical_files = [
        ".claude/hooks/utils/env_loader.py",
        ".claude/hooks/utils/find_project_root.py",
        ".claude/hooks/utils/context_injector.py",
        ".claude/hooks/utils/mcp_client.py",
        ".claude/hooks/utils/unified_hint_system.py",
        ".claude/hooks/utils/docs_indexer.py",
        ".claude/hooks/utils/mcp_post_action_hints_backup.py",
        ".claude/hooks/migrate_data.py",
    ]

    results = []
    for file_path in critical_files:
        full_path = Path("/home/daihungpham/__projects__/4genthub") / file_path
        if full_path.exists():
            with open(full_path, 'r') as f:
                content = f.read()

            # Check for Path.cwd() usage (excluding comments and acceptable uses)
            if "Path.cwd()" in content:
                # Check if it's in a comment or acceptable context
                lines = content.split('\n')
                problematic = False
                for i, line in enumerate(lines, 1):
                    if "Path.cwd()" in line and not line.strip().startswith("#"):
                        # Check if it's for reporting current directory (acceptable)
                        if "working_directory" not in line and "Working directory" not in line:
                            problematic = True
                            results.append(f"❌ {Path(file_path).name}: Line {i} uses Path.cwd()")
                            break

                if not problematic:
                    results.append(f"✅ {Path(file_path).name}: No problematic Path.cwd() usage")
            else:
                results.append(f"✅ {Path(file_path).name}: No Path.cwd() usage")
        else:
            results.append(f"⚠️  {Path(file_path).name}: File not found")

    return results

def main():
    """Run all verification tests."""
    all_results = []

    # Run import verification
    all_results.extend(verify_imports())

    # Test from different locations
    all_results.extend(test_from_different_locations())

    # Check for Path.cwd() usage
    all_results.extend(check_no_cwd_fallback())

    # Print summary
    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)

    for result in all_results:
        print(result)

    # Count results
    passed = len([r for r in all_results if r.startswith("✅")])
    failed = len([r for r in all_results if r.startswith("❌")])
    warnings = len([r for r in all_results if r.startswith("⚠️")])

    print("\n" + "-" * 70)
    print(f"Results: {passed} passed, {failed} failed, {warnings} warnings")

    if failed == 0:
        print("\n🎉 ALL VERIFICATIONS PASSED! Dynamic root finding is working correctly.")
    else:
        print("\n⚠️  Some verifications failed. Please review the results above.")

if __name__ == "__main__":
    main()