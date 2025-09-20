#!/usr/bin/env python3
"""
Claude Code Hooks - Installation Validator

This script validates an existing Claude Code hooks installation
and provides detailed diagnostics and repair suggestions.

Features:
- Comprehensive installation validation
- Detailed diagnostic reports
- Automatic repair suggestions
- Configuration file validation
- Hook execution testing
- Environment compatibility checking
- Cross-platform validation

Usage:
    python3 .claude/validate_installation.py
    python3 .claude/validate_installation.py --repair
    python3 .claude/validate_installation.py --detailed
"""

import sys
import os
import json
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

# Ensure we can import our utilities
script_dir = Path(__file__).parent
hooks_dir = script_dir / "hooks"
utils_dir = hooks_dir / "utils"

# Add to Python path if directories exist
if hooks_dir.exists():
    sys.path.insert(0, str(hooks_dir))
if utils_dir.exists():
    sys.path.insert(0, str(utils_dir))

try:
    from environment_detector import EnvironmentDetector
    from dependency_manager import DependencyManager, setup_default_fallbacks
    UTILS_AVAILABLE = True
except ImportError:
    UTILS_AVAILABLE = False


class InstallationValidator:
    """Validates Claude Code hooks installation."""

    def __init__(self, project_root: Optional[Path] = None, verbose: bool = False):
        """
        Initialize the validator.

        Args:
            project_root: Optional project root path
            verbose: Whether to show detailed output
        """
        self.verbose = verbose
        self.project_root = project_root or self._find_project_root()
        self.claude_dir = self.project_root / '.claude' if self.project_root else None
        self.hooks_dir = self.claude_dir / 'hooks' if self.claude_dir else None

        # Initialize components if utilities are available
        if UTILS_AVAILABLE and self.project_root:
            self.env_detector = EnvironmentDetector(self.project_root)
            self.dep_manager = DependencyManager(self.project_root)
            setup_default_fallbacks(self.dep_manager)
        else:
            self.env_detector = None
            self.dep_manager = None

        self.validation_results = {
            'overall_status': 'unknown',
            'tests': {},
            'warnings': [],
            'errors': [],
            'repair_suggestions': []
        }

    def validate(self) -> Dict[str, Any]:
        """
        Run comprehensive validation.

        Returns:
            Dictionary with validation results
        """
        print("🔍 Claude Code Hooks - Installation Validator")
        print("=" * 50)

        # Core structure validation
        self._validate_core_structure()

        # Configuration validation
        self._validate_configuration()

        # Environment validation
        self._validate_environment()

        # Dependency validation
        self._validate_dependencies()

        # Hook execution validation
        self._validate_hook_execution()

        # Integration validation
        self._validate_integration()

        # Determine overall status
        self._determine_overall_status()

        # Generate report
        self._generate_report()

        return self.validation_results

    def repair(self) -> bool:
        """
        Attempt to repair common issues.

        Returns:
            True if repairs were successful, False otherwise
        """
        print("🔧 Attempting to repair installation...")

        repairs_attempted = 0
        repairs_successful = 0

        for suggestion in self.validation_results['repair_suggestions']:
            print(f"\n🔄 {suggestion['description']}")
            repairs_attempted += 1

            try:
                if suggestion['action'] == 'run_setup':
                    if self._repair_run_setup():
                        repairs_successful += 1
                        print("✅ Repair successful")
                    else:
                        print("❌ Repair failed")

                elif suggestion['action'] == 'create_file':
                    if self._repair_create_file(suggestion['file_path'], suggestion.get('content', '')):
                        repairs_successful += 1
                        print("✅ Repair successful")
                    else:
                        print("❌ Repair failed")

                elif suggestion['action'] == 'fix_permissions':
                    if self._repair_fix_permissions(suggestion['file_path']):
                        repairs_successful += 1
                        print("✅ Repair successful")
                    else:
                        print("❌ Repair failed")

                elif suggestion['action'] == 'install_dependencies':
                    if self._repair_install_dependencies():
                        repairs_successful += 1
                        print("✅ Repair successful")
                    else:
                        print("❌ Repair failed")

            except Exception as e:
                print(f"❌ Repair failed with error: {e}")

        print(f"\n📊 Repair Summary: {repairs_successful}/{repairs_attempted} repairs successful")
        return repairs_successful == repairs_attempted

    def _validate_core_structure(self):
        """Validate core directory and file structure."""
        print("\n📁 Validating Core Structure...")

        # Check project root
        if not self.project_root:
            self._add_error("core_structure", "Project root not found",
                          "Could not locate project root directory")
            return

        self._add_success("core_structure", "project_root", f"Found: {self.project_root}")

        # Check .claude directory
        if not self.claude_dir or not self.claude_dir.exists():
            self._add_error("core_structure", ".claude directory missing",
                          "Run installation script or clone .claude properly")
            return

        self._add_success("core_structure", "claude_dir", f"Found: {self.claude_dir}")

        # Check hooks directory
        if not self.hooks_dir or not self.hooks_dir.exists():
            self._add_error("core_structure", "hooks directory missing",
                          "Reinstall hooks or check .claude structure")
            return

        self._add_success("core_structure", "hooks_dir", f"Found: {self.hooks_dir}")

        # Check required files
        required_files = {
            'settings.json.sample': 'Settings template',
            'hooks/setup_hooks.py': 'Setup script',
            'hooks/execute_hook.py': 'Hook executor',
            'hooks/utils/environment_detector.py': 'Environment detector',
            'hooks/utils/dependency_manager.py': 'Dependency manager'
        }

        for file_path, description in required_files.items():
            full_path = self.claude_dir / file_path
            if full_path.exists():
                self._add_success("core_structure", f"file_{file_path.replace('/', '_')}",
                                f"{description}: Found")
            else:
                self._add_error("core_structure", f"{description} missing",
                              f"File not found: {file_path}")

    def _validate_configuration(self):
        """Validate configuration files."""
        print("\n⚙️  Validating Configuration...")

        # Check settings.json
        settings_file = self.claude_dir / 'settings.json'
        if not settings_file.exists():
            self._add_warning("configuration", "settings.json not found",
                            "Run setup_hooks.py to generate configuration")
            self._add_repair_suggestion("run_setup", "Generate settings.json configuration")
            return

        self._add_success("configuration", "settings_exists", "settings.json found")

        # Validate settings.json content
        try:
            with open(settings_file, 'r') as f:
                settings = json.load(f)

            # Check required sections
            required_sections = ['hooks', 'statusLine', 'permissions']
            for section in required_sections:
                if section in settings:
                    self._add_success("configuration", f"settings_{section}",
                                    f"settings.json has {section} section")
                else:
                    self._add_warning("configuration", f"Missing {section} section",
                                    "Regenerate settings.json")

            # Check for placeholder replacement
            settings_str = json.dumps(settings)
            if '{{PROJECT_ROOT}}' in settings_str:
                self._add_error("configuration", "PROJECT_ROOT placeholder not replaced",
                              "Run setup_hooks.py to replace placeholders")
                self._add_repair_suggestion("run_setup", "Replace PROJECT_ROOT placeholder")
            else:
                self._add_success("configuration", "placeholders_replaced",
                                "PROJECT_ROOT placeholder properly replaced")

            # Validate hook commands
            self._validate_hook_commands(settings)

        except json.JSONDecodeError as e:
            self._add_error("configuration", f"Invalid JSON in settings.json: {e}",
                          "Fix JSON syntax or regenerate settings.json")
        except Exception as e:
            self._add_error("configuration", f"Error reading settings.json: {e}",
                          "Check file permissions and content")

        # Check project configuration files
        self._validate_project_config_files()

    def _validate_hook_commands(self, settings: Dict[str, Any]):
        """Validate hook commands in settings."""
        hooks = settings.get('hooks', {})

        for hook_type, hook_configs in hooks.items():
            for config in hook_configs:
                if 'hooks' in config:
                    for hook in config['hooks']:
                        if hook.get('type') == 'command' and 'command' in hook:
                            command = hook['command']

                            # Check if command uses execute_hook.py
                            if 'execute_hook.py' in command:
                                parts = command.split()
                                if len(parts) >= 3:
                                    hook_name = parts[2]
                                    hook_path = self.hooks_dir / hook_name

                                    if hook_path.exists():
                                        self._add_success("configuration", f"hook_{hook_name}",
                                                        f"Hook file found: {hook_name}")
                                    else:
                                        self._add_error("configuration", f"Hook file missing: {hook_name}",
                                                      f"Missing hook file: {hook_path}")

    def _validate_project_config_files(self):
        """Validate project-level configuration files."""
        project_files = {
            'CLAUDE.md': 'Team AI instructions',
            'CLAUDE.local.md': 'Personal AI settings',
            '.mcp.json': 'API configuration'
        }

        for filename, description in project_files.items():
            file_path = self.project_root / filename
            if file_path.exists():
                self._add_success("configuration", f"project_{filename.replace('.', '_')}",
                                f"{description}: Found")

                # Validate .mcp.json specifically
                if filename == '.mcp.json':
                    self._validate_mcp_json(file_path)
            else:
                sample_path = self.claude_dir / f"copy-to-root-project-rename-to:{filename}"
                if sample_path.exists():
                    self._add_warning("configuration", f"{description} not configured",
                                    f"Copy sample file: {sample_path}")
                else:
                    self._add_warning("configuration", f"{description} not found",
                                    f"Create {filename} file")

    def _validate_mcp_json(self, mcp_file: Path):
        """Validate .mcp.json configuration."""
        try:
            with open(mcp_file, 'r') as f:
                mcp_config = json.load(f)

            # Check for API token placeholder
            config_str = json.dumps(mcp_config)
            if 'YOUR_API_TOKEN_HERE' in config_str:
                self._add_warning("configuration", "API token not configured",
                                "Replace YOUR_API_TOKEN_HERE with actual token")
            elif 'Authorization' in config_str:
                self._add_success("configuration", "api_token_configured",
                                "API token appears to be configured")

        except json.JSONDecodeError as e:
            self._add_error("configuration", f"Invalid JSON in .mcp.json: {e}",
                          "Fix JSON syntax")
        except Exception as e:
            self._add_warning("configuration", f"Could not validate .mcp.json: {e}",
                            "Check file permissions")

    def _validate_environment(self):
        """Validate environment compatibility."""
        print("\n🌍 Validating Environment...")

        if not UTILS_AVAILABLE:
            self._add_warning("environment", "Utility modules not available",
                            "Some validation features limited")
            return

        # Use environment detector
        is_valid, issues = self.env_detector.validate_environment()

        if is_valid:
            self._add_success("environment", "environment_valid", "Environment validation passed")
        else:
            for issue in issues:
                self._add_warning("environment", issue, "Check environment requirements")

        # Platform-specific checks
        env_info = self.env_detector.get_environment_info()
        platform = env_info['platform']

        self._add_success("environment", "platform",
                        f"Platform: {platform['system']} {platform['release']}")

        # Python version check
        python = env_info['python']
        if python['version_info']['major'] >= 3 and python['version_info']['minor'] >= 7:
            self._add_success("environment", "python_version",
                            f"Python version: {python['version_info']['major']}.{python['version_info']['minor']}")
        else:
            self._add_error("environment", "Python version too old",
                          "Python 3.7+ required")

        # Git repository check
        git = env_info['git']
        if git['git_available']:
            self._add_success("environment", "git_available", "Git is available")

            if git['is_git_repo']:
                self._add_success("environment", "git_repo", f"Git repository detected")

                if git['is_submodule']:
                    self._add_success("environment", "git_submodule",
                                    ".claude detected as git submodule")
        else:
            self._add_warning("environment", "Git not available",
                            "Git recommended for version control")

    def _validate_dependencies(self):
        """Validate dependencies."""
        print("\n📦 Validating Dependencies...")

        if not UTILS_AVAILABLE:
            self._add_warning("dependencies", "Dependency manager not available",
                            "Cannot check optional dependencies")
            return

        dep_status = self.dep_manager.check_dependencies()

        available_count = sum(1 for status in dep_status['available'].values() if status)
        missing_count = len(dep_status['missing'])

        self._add_success("dependencies", "available_packages",
                        f"Available packages: {available_count}")

        if missing_count == 0:
            self._add_success("dependencies", "all_dependencies",
                            "All dependencies available")
        else:
            self._add_warning("dependencies", f"{missing_count} packages missing",
                            "Some optional packages not available")

            # Check for packages with fallbacks
            has_fallbacks = sum(1 for name in dep_status['missing'].keys()
                              if dep_status['fallbacks_available'].get(name, False))

            if has_fallbacks > 0:
                self._add_success("dependencies", "fallbacks_available",
                                f"{has_fallbacks} packages have fallback implementations")

            # Check for installable packages
            installable = [name for name in dep_status['missing'].keys()
                         if name in dep_status['install_commands']]

            if installable:
                self._add_repair_suggestion("install_dependencies",
                                          f"Install {len(installable)} missing packages")

    def _validate_hook_execution(self):
        """Validate hook execution."""
        print("\n🔧 Validating Hook Execution...")

        execute_hook = self.hooks_dir / 'execute_hook.py'
        if not execute_hook.exists():
            self._add_error("hook_execution", "execute_hook.py missing",
                          "Reinstall hooks")
            return

        # Test basic execution
        try:
            result = subprocess.run([
                sys.executable, str(execute_hook), '--help'
            ], capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                self._add_success("hook_execution", "basic_execution",
                                "Hook executor responds to --help")
            else:
                self._add_warning("hook_execution", "Hook executor returned non-zero",
                                "May indicate configuration issue")

        except subprocess.TimeoutExpired:
            self._add_warning("hook_execution", "Hook execution timed out",
                            "Check for infinite loops or blocking operations")
        except Exception as e:
            self._add_error("hook_execution", f"Hook execution failed: {e}",
                          "Check Python environment and permissions")

        # Test with a simple hook if available
        test_hooks = ['session_start.py', 'stop.py', 'notification.py']
        for hook_name in test_hooks:
            hook_path = self.hooks_dir / hook_name
            if hook_path.exists():
                try:
                    # Quick syntax check
                    result = subprocess.run([
                        sys.executable, '-m', 'py_compile', str(hook_path)
                    ], capture_output=True, text=True, timeout=10)

                    if result.returncode == 0:
                        self._add_success("hook_execution", f"syntax_{hook_name}",
                                        f"Hook syntax valid: {hook_name}")
                    else:
                        self._add_error("hook_execution", f"Syntax error in {hook_name}",
                                      "Fix Python syntax errors")
                        break

                except Exception as e:
                    self._add_warning("hook_execution", f"Could not validate {hook_name}: {e}",
                                    "Check hook file integrity")
                    break

    def _validate_integration(self):
        """Validate Claude Code integration."""
        print("\n🔗 Validating Integration...")

        # Check if settings.json would be recognized by Claude Code
        settings_file = self.claude_dir / 'settings.json'
        if settings_file.exists():
            self._add_success("integration", "settings_location",
                            "settings.json in correct location")

            # Check gitignore status
            gitignore_file = self.project_root / '.gitignore'
            if gitignore_file.exists():
                try:
                    with open(gitignore_file, 'r') as f:
                        gitignore_content = f.read()

                    if '.claude/settings.json' in gitignore_content:
                        self._add_success("integration", "settings_gitignored",
                                        "settings.json properly gitignored")
                    else:
                        self._add_warning("integration", "settings.json not in .gitignore",
                                        "Add .claude/settings.json to .gitignore")
                except Exception:
                    pass

        # Check hook protection files
        config_dir = self.hooks_dir / 'config'
        protection_files = [
            '__claude_hook__allowed_root_files',
            '__claude_hook__valid_test_paths'
        ]

        for filename in protection_files:
            file_path = config_dir / filename
            if file_path.exists():
                self._add_success("integration", f"protection_{filename}",
                                f"Hook protection configured: {filename}")
            else:
                sample_path = config_dir / f"{filename}.sample"
                if sample_path.exists():
                    self._add_warning("integration", f"Hook protection not configured: {filename}",
                                    f"Copy {filename}.sample to {filename}")

    def _determine_overall_status(self):
        """Determine overall validation status."""
        error_count = len(self.validation_results['errors'])
        warning_count = len(self.validation_results['warnings'])

        if error_count == 0:
            if warning_count == 0:
                self.validation_results['overall_status'] = 'excellent'
            elif warning_count <= 3:
                self.validation_results['overall_status'] = 'good'
            else:
                self.validation_results['overall_status'] = 'fair'
        else:
            if error_count <= 2:
                self.validation_results['overall_status'] = 'poor'
            else:
                self.validation_results['overall_status'] = 'broken'

    def _generate_report(self):
        """Generate validation report."""
        print("\n" + "=" * 50)
        print("VALIDATION REPORT")
        print("=" * 50)

        # Overall status
        status = self.validation_results['overall_status']
        status_emoji = {
            'excellent': '🌟',
            'good': '✅',
            'fair': '⚠️',
            'poor': '❌',
            'broken': '💥'
        }

        print(f"\n{status_emoji.get(status, '❓')} Overall Status: {status.upper()}")

        # Summary
        error_count = len(self.validation_results['errors'])
        warning_count = len(self.validation_results['warnings'])
        success_count = sum(len(tests) for tests in self.validation_results['tests'].values())

        print(f"\n📊 Summary:")
        print(f"   ✅ Successful tests: {success_count}")
        print(f"   ⚠️  Warnings: {warning_count}")
        print(f"   ❌ Errors: {error_count}")

        # Errors
        if error_count > 0:
            print(f"\n❌ Errors ({error_count}):")
            for error in self.validation_results['errors']:
                print(f"   • {error['message']}")
                if error['suggestion']:
                    print(f"     → {error['suggestion']}")

        # Warnings
        if warning_count > 0:
            print(f"\n⚠️  Warnings ({warning_count}):")
            for warning in self.validation_results['warnings']:
                print(f"   • {warning['message']}")
                if warning['suggestion']:
                    print(f"     → {warning['suggestion']}")

        # Repair suggestions
        if self.validation_results['repair_suggestions']:
            print(f"\n🔧 Repair Suggestions:")
            for suggestion in self.validation_results['repair_suggestions']:
                print(f"   • {suggestion['description']}")

        # Detailed test results if verbose
        if self.verbose:
            print(f"\n📋 Detailed Test Results:")
            for category, tests in self.validation_results['tests'].items():
                print(f"\n   {category.replace('_', ' ').title()}:")
                for test_name, result in tests.items():
                    status_symbol = "✅" if result['status'] == 'success' else "❌"
                    print(f"     {status_symbol} {result['message']}")

    def _add_success(self, category: str, test_name: str, message: str):
        """Add a successful test result."""
        if category not in self.validation_results['tests']:
            self.validation_results['tests'][category] = {}

        self.validation_results['tests'][category][test_name] = {
            'status': 'success',
            'message': message
        }

    def _add_warning(self, category: str, message: str, suggestion: str = ""):
        """Add a warning."""
        self.validation_results['warnings'].append({
            'category': category,
            'message': message,
            'suggestion': suggestion
        })

    def _add_error(self, category: str, message: str, suggestion: str = ""):
        """Add an error."""
        self.validation_results['errors'].append({
            'category': category,
            'message': message,
            'suggestion': suggestion
        })

    def _add_repair_suggestion(self, action: str, description: str, **kwargs):
        """Add a repair suggestion."""
        suggestion = {
            'action': action,
            'description': description
        }
        suggestion.update(kwargs)
        self.validation_results['repair_suggestions'].append(suggestion)

    def _repair_run_setup(self) -> bool:
        """Repair by running setup_hooks.py."""
        setup_script = self.hooks_dir / 'setup_hooks.py'
        if not setup_script.exists():
            return False

        try:
            result = subprocess.run([
                sys.executable, str(setup_script)
            ], capture_output=True, text=True, cwd=self.project_root, timeout=60)

            return result.returncode == 0
        except Exception:
            return False

    def _repair_create_file(self, file_path: str, content: str) -> bool:
        """Repair by creating a file."""
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w') as f:
                f.write(content)
            return True
        except Exception:
            return False

    def _repair_fix_permissions(self, file_path: str) -> bool:
        """Repair file permissions."""
        try:
            path = Path(file_path)
            if path.exists():
                path.chmod(0o755)
                return True
        except Exception:
            pass
        return False

    def _repair_install_dependencies(self) -> bool:
        """Repair by installing dependencies."""
        if not UTILS_AVAILABLE or not self.dep_manager:
            return False

        try:
            result = self.dep_manager.install_missing_dependencies(
                interactive=False, dry_run=False
            )
            return len(result['failed']) == 0
        except Exception:
            return False

    def _find_project_root(self) -> Optional[Path]:
        """Find the project root directory."""
        # Marker files that indicate project root (ordered by priority)
        markers = [
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

        # Start from current directory and this script's location
        start_paths = [
            Path.cwd(),
            Path(__file__).parent.parent if __file__ else Path.cwd()
        ]

        for start in start_paths:
            try:
                current = start.resolve()

                # Walk up the directory tree
                while current != current.parent:
                    # Check for marker files in priority order
                    for marker in markers:
                        marker_path = current / marker
                        if marker_path.exists():
                            # Verify it's a Claude project by checking for .claude directory
                            claude_dir = current / '.claude'
                            if claude_dir.exists():
                                return current

                    current = current.parent

            except (OSError, PermissionError):
                continue

        return None


def main():
    """Main function for CLI usage."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Claude Code Hooks - Installation Validator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python3 .claude/validate_installation.py
    python3 .claude/validate_installation.py --verbose
    python3 .claude/validate_installation.py --repair
        """
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed validation results'
    )

    parser.add_argument(
        '--repair',
        action='store_true',
        help='Attempt to repair found issues automatically'
    )

    parser.add_argument(
        '--project-root',
        type=Path,
        help='Specify project root directory (auto-detected if not provided)'
    )

    args = parser.parse_args()

    validator = InstallationValidator(
        project_root=args.project_root,
        verbose=args.verbose
    )

    # Run validation
    results = validator.validate()

    # Run repairs if requested
    if args.repair and results['repair_suggestions']:
        print("\n" + "=" * 50)
        success = validator.repair()
        if success:
            print("\n✅ All repairs completed successfully!")
            print("Re-run validation to verify fixes.")
        else:
            print("\n⚠️  Some repairs failed. Check output above for details.")

    # Exit with appropriate code
    status = results['overall_status']
    if status in ['excellent', 'good']:
        sys.exit(0)
    elif status == 'fair':
        sys.exit(1)
    else:  # poor or broken
        sys.exit(2)


if __name__ == "__main__":
    main()