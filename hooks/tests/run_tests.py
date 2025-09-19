#!/usr/bin/env python3
"""
Test runner script for Claude hooks system.

This script provides a convenient way to run tests with various options
and configurations for the hooks system.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

# Add hooks directory to Python path
hooks_dir = Path(__file__).parent.parent
sys.path.insert(0, str(hooks_dir))


def run_command(cmd, capture_output=False):
    """Run a shell command and return the result."""
    try:
        if capture_output:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.returncode == 0, result.stdout, result.stderr
        else:
            result = subprocess.run(cmd, shell=True)
            return result.returncode == 0, "", ""
    except Exception as e:
        print(f"Error running command '{cmd}': {e}")
        return False, "", str(e)


def check_dependencies():
    """Check if required testing dependencies are installed."""
    print("Checking testing dependencies...")

    required_packages = [
        'pytest',
        'pytest-cov',
        'pytest-asyncio',
        'httpx'
    ]

    missing_packages = []

    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✓ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"✗ {package} (missing)")

    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        print("Install with: pip install -r tests/requirements-test.txt")
        return False

    print("All dependencies satisfied!")
    return True


def run_unit_tests(verbose=False, coverage=False):
    """Run unit tests."""
    print("Running unit tests...")

    cmd_parts = ["pytest", "unit/"]

    if verbose:
        cmd_parts.append("-v")

    if coverage:
        cmd_parts.extend([
            "--cov=../",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov"
        ])

    cmd = " ".join(cmd_parts)
    success, stdout, stderr = run_command(cmd, capture_output=True)

    if success:
        print("✓ Unit tests passed")
        if stdout:
            print(stdout)
    else:
        print("✗ Unit tests failed")
        if stderr:
            print(stderr)

    return success


def run_integration_tests(verbose=False):
    """Run integration tests."""
    print("Running integration tests...")

    cmd_parts = ["pytest", "integration/"]

    if verbose:
        cmd_parts.append("-v")

    cmd = " ".join(cmd_parts)
    success, stdout, stderr = run_command(cmd, capture_output=True)

    if success:
        print("✓ Integration tests passed")
        if stdout:
            print(stdout)
    else:
        print("✗ Integration tests failed")
        if stderr:
            print(stderr)

    return success


def run_all_tests(verbose=False, coverage=False, parallel=False):
    """Run all tests."""
    print("Running all tests...")

    cmd_parts = ["pytest", "."]

    if verbose:
        cmd_parts.append("-v")

    if coverage:
        cmd_parts.extend([
            "--cov=../",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov",
            "--cov-fail-under=80"
        ])

    if parallel:
        cmd_parts.extend(["-n", "auto"])

    # Add other useful options
    cmd_parts.extend([
        "--tb=short",
        "-ra",
        "--durations=10"
    ])

    cmd = " ".join(cmd_parts)
    success, stdout, stderr = run_command(cmd, capture_output=False)

    if success:
        print("✓ All tests passed")
    else:
        print("✗ Some tests failed")

    return success


def generate_coverage_report():
    """Generate detailed coverage report."""
    print("Generating coverage report...")

    cmd = "pytest . --cov=../ --cov-report=html:htmlcov --cov-report=xml:coverage.xml --cov-report=term"
    success, stdout, stderr = run_command(cmd, capture_output=True)

    if success:
        print("✓ Coverage report generated")
        print("HTML report: htmlcov/index.html")
        print("XML report: coverage.xml")
        if stdout:
            print(stdout)
    else:
        print("✗ Coverage report generation failed")
        if stderr:
            print(stderr)

    return success


def run_linting():
    """Run code linting and style checks."""
    print("Running linting...")

    # Check if ruff is available
    try:
        import ruff
        cmd = "ruff check ../ --exclude=tests/"
        success, stdout, stderr = run_command(cmd, capture_output=True)

        if success:
            print("✓ Linting passed")
        else:
            print("✗ Linting issues found")
            if stdout:
                print(stdout)

        return success
    except ImportError:
        print("Ruff not available, skipping linting")
        return True


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Run Claude hooks system tests")

    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--parallel", "-n", action="store_true", help="Run tests in parallel")
    parser.add_argument("--lint", action="store_true", help="Run linting checks")
    parser.add_argument("--check-deps", action="store_true", help="Check dependencies only")
    parser.add_argument("--quick", action="store_true", help="Quick test run (unit tests only, no coverage)")

    args = parser.parse_args()

    # Change to tests directory
    os.chdir(Path(__file__).parent)

    if args.check_deps:
        return 0 if check_dependencies() else 1

    # Check dependencies first
    if not check_dependencies():
        return 1

    success = True

    if args.lint:
        success &= run_linting()

    if args.quick:
        success &= run_unit_tests(verbose=args.verbose, coverage=False)
    elif args.unit:
        success &= run_unit_tests(verbose=args.verbose, coverage=args.coverage)
    elif args.integration:
        success &= run_integration_tests(verbose=args.verbose)
    elif args.coverage:
        success &= generate_coverage_report()
    else:
        # Run all tests by default
        success &= run_all_tests(
            verbose=args.verbose,
            coverage=args.coverage,
            parallel=args.parallel
        )

    if success:
        print("\n🎉 All tests completed successfully!")
        return 0
    else:
        print("\n❌ Some tests failed. Please check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())