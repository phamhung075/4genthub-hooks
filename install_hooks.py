#!/usr/bin/env python3
"""
Claude Code Hooks - Portable Bootstrap Installer

This script provides a one-command installation for Claude Code hooks
that works across different project structures, environments, and platforms.

Features:
- Auto-detects project root and structure
- Works with .claude as regular folder or git submodule
- Cross-platform compatibility (Windows/macOS/Linux)
- Handles virtual environments automatically
- Graceful dependency management with fallbacks
- Comprehensive validation and troubleshooting
- One-command setup from any directory

Usage:
    python3 .claude/install_hooks.py
    # OR from any subdirectory:
    python3 path/to/.claude/install_hooks.py

This installer will:
1. Detect your environment and project structure
2. Install or validate dependencies
3. Configure hooks with correct paths
4. Set up necessary configuration files
5. Validate the installation
6. Provide next steps and troubleshooting
"""

import sys
import os
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
    from environment_detector import EnvironmentDetector, generate_environment_report
    from dependency_manager import DependencyManager, setup_default_fallbacks, generate_dependency_report
    UTILS_AVAILABLE = True
except ImportError:
    print("⚠️  Warning: Hook utilities not found. Using basic installation mode.")
    UTILS_AVAILABLE = False


class ClaudeHooksInstaller:
    """Portable installer for Claude Code hooks."""

    def __init__(self, force_reinstall: bool = False, verbose: bool = False):
        """
        Initialize the installer.

        Args:
            force_reinstall: Whether to force reinstallation even if already configured
            verbose: Whether to show detailed output
        """
        self.force_reinstall = force_reinstall
        self.verbose = verbose
        self.project_root = self._find_project_root()
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

    def install(self) -> bool:
        """
        Run the complete installation process.

        Returns:
            True if installation was successful, False otherwise
        """
        print("🚀 Claude Code Hooks - Portable Installer")
        print("=" * 50)

        # Step 1: Environment Detection
        if not self._detect_environment():
            return False

        # Step 2: Pre-installation Checks
        if not self._pre_installation_checks():
            return False

        # Step 3: Dependency Management
        if not self._handle_dependencies():
            return False

        # Step 4: Configuration Setup
        if not self._setup_configuration():
            return False

        # Step 5: Installation Validation
        if not self._validate_installation():
            return False

        # Step 6: Post-installation Setup
        self._post_installation_setup()

        print("\n✅ Installation completed successfully!")
        return True

    def _detect_environment(self) -> bool:
        """Detect and validate the environment."""
        print("\n🔍 Step 1: Environment Detection")
        print("-" * 30)

        if not self.project_root:
            print("❌ Error: Could not find project root directory")
            print("\nTroubleshooting:")
            print("1. Ensure you're running this from within a project directory")
            print("2. Make sure one of these files exists in your project root:")
            print("   - CLAUDE.md, .git, package.json, pyproject.toml, .env")
            return False

        print(f"✅ Project root: {self.project_root}")

        if not self.claude_dir or not self.claude_dir.exists():
            print("❌ Error: .claude directory not found")
            print(f"Expected location: {self.claude_dir}")
            return False

        print(f"✅ Claude directory: {self.claude_dir}")

        if not self.hooks_dir or not self.hooks_dir.exists():
            print("❌ Error: .claude/hooks directory not found")
            print(f"Expected location: {self.hooks_dir}")
            return False

        print(f"✅ Hooks directory: {self.hooks_dir}")

        # Show environment details if available
        if UTILS_AVAILABLE and self.env_detector:
            if self.verbose:
                print("\n📊 Environment Details:")
                env_info = self.env_detector.get_environment_info()
                print(f"   • Platform: {env_info['platform']['system']}")
                print(f"   • Python: {env_info['python']['version_info']['major']}.{env_info['python']['version_info']['minor']}")
                if env_info['virtual_env']['is_virtual_env']:
                    print(f"   • Virtual Env: {env_info['virtual_env']['type']} ({env_info['virtual_env']['name']})")
                if env_info['git']['is_git_repo']:
                    print(f"   • Git: {env_info['git']['current_branch']}")
                    if env_info['git']['is_submodule']:
                        print(f"   • .claude is a git submodule")

        return True

    def _pre_installation_checks(self) -> bool:
        """Perform pre-installation checks."""
        print("\n🔍 Step 2: Pre-installation Checks")
        print("-" * 35)

        # Check if already installed
        settings_file = self.claude_dir / 'settings.json'
        if settings_file.exists() and not self.force_reinstall:
            print("ℹ️  Claude hooks appear to be already configured")
            answer = input("Do you want to reconfigure? [y/N]: ")
            if answer.lower() not in ['y', 'yes']:
                print("Skipping installation. Use --force to force reinstallation.")
                return False

        # Check for required files
        required_files = [
            'settings.json.sample',
            'hooks/setup_hooks.py',
            'hooks/execute_hook.py'
        ]

        missing_files = []
        for file_path in required_files:
            full_path = self.claude_dir / file_path
            if not full_path.exists():
                missing_files.append(file_path)
            else:
                print(f"✅ Found: {file_path}")

        if missing_files:
            print(f"\n❌ Missing required files:")
            for file_path in missing_files:
                print(f"   • {file_path}")
            print("\nThis appears to be an incomplete Claude hooks installation.")
            return False

        # Check Python version
        if sys.version_info.major < 3:
            print("❌ Error: Python 3.x is required")
            print(f"Current version: {sys.version_info.major}.{sys.version_info.minor}")
            return False

        if sys.version_info.minor < 7:
            print("⚠️  Warning: Python 3.7+ is recommended")
            print(f"Current version: {sys.version_info.major}.{sys.version_info.minor}")

        print(f"✅ Python version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")

        return True

    def _handle_dependencies(self) -> bool:
        """Handle dependency detection and installation."""
        print("\n📦 Step 3: Dependency Management")
        print("-" * 32)

        if not UTILS_AVAILABLE:
            print("⚠️  Utilities not available - skipping dependency management")
            print("The hooks will use fallback implementations where needed")
            return True

        # Check dependencies
        dep_status = self.dep_manager.check_dependencies()

        available_count = sum(1 for status in dep_status['available'].values() if status)
        missing_count = len(dep_status['missing'])

        print(f"✅ Available packages: {available_count}")
        if missing_count > 0:
            print(f"⚠️  Missing packages: {missing_count}")

            # Show missing packages
            for name, reason in dep_status['missing'].items():
                print(f"   • {name}: {reason}")

        # Handle missing dependencies
        if missing_count > 0:
            print("\n🔧 Handling Missing Dependencies:")

            # Check which ones have fallbacks
            has_fallbacks = [name for name in dep_status['missing'].keys()
                           if dep_status['fallbacks_available'].get(name, False)]

            if has_fallbacks:
                print(f"✅ {len(has_fallbacks)} packages have fallback implementations")

            # Offer to install missing packages
            installable = [name for name in dep_status['missing'].keys()
                         if name in dep_status['install_commands']]

            if installable:
                print(f"\n📥 {len(installable)} packages can be installed automatically:")
                for name in installable:
                    cmd = dep_status['install_commands'][name]
                    print(f"   • {name}: {cmd}")

                answer = input("\nInstall missing packages? [y/N]: ")
                if answer.lower() in ['y', 'yes']:
                    print("\n🔄 Installing packages...")
                    install_result = self.dep_manager.install_missing_dependencies(
                        interactive=False, dry_run=False
                    )

                    for package in install_result['successful']:
                        print(f"✅ Installed: {package}")

                    for package in install_result['failed']:
                        print(f"❌ Failed to install: {package}")

                    if install_result['failed']:
                        print("⚠️  Some packages failed to install, but fallbacks are available")

        print("✅ Dependency management completed")
        return True

    def _setup_configuration(self) -> bool:
        """Set up configuration files."""
        print("\n⚙️  Step 4: Configuration Setup")
        print("-" * 30)

        # Run setup_hooks.py
        setup_script = self.hooks_dir / 'setup_hooks.py'
        if not setup_script.exists():
            print("❌ Error: setup_hooks.py not found")
            return False

        print("🔄 Running setup_hooks.py...")
        try:
            # Run setup_hooks.py as a subprocess
            result = subprocess.run([
                sys.executable, str(setup_script)
            ], capture_output=True, text=True, cwd=self.project_root, timeout=60)

            if result.returncode == 0:
                print("✅ Configuration setup completed")
                if self.verbose and result.stdout:
                    print("Output:")
                    for line in result.stdout.split('\n'):
                        if line.strip():
                            print(f"   {line}")
            else:
                print("❌ Configuration setup failed")
                if result.stderr:
                    print("Error output:")
                    for line in result.stderr.split('\n'):
                        if line.strip():
                            print(f"   {line}")
                return False

        except subprocess.TimeoutExpired:
            print("❌ Configuration setup timed out")
            return False
        except Exception as e:
            print(f"❌ Error running setup: {e}")
            return False

        return True

    def _validate_installation(self) -> bool:
        """Validate the installation."""
        print("\n🧪 Step 5: Installation Validation")
        print("-" * 33)

        validation_passed = True

        # Check if settings.json was created
        settings_file = self.claude_dir / 'settings.json'
        if settings_file.exists():
            print("✅ settings.json created")
        else:
            print("❌ settings.json not found")
            validation_passed = False

        # Check if settings.json has valid content
        if settings_file.exists():
            try:
                import json
                with open(settings_file, 'r') as f:
                    settings = json.load(f)

                # Validate structure
                required_sections = ['hooks', 'statusLine']
                for section in required_sections:
                    if section in settings:
                        print(f"✅ settings.json has {section} section")
                    else:
                        print(f"❌ settings.json missing {section} section")
                        validation_passed = False

                # Check for PROJECT_ROOT placeholder replacement
                settings_str = json.dumps(settings)
                if '{{PROJECT_ROOT}}' in settings_str:
                    print("❌ PROJECT_ROOT placeholder not replaced in settings.json")
                    validation_passed = False
                else:
                    print("✅ PROJECT_ROOT placeholder properly replaced")

            except json.JSONDecodeError as e:
                print(f"❌ settings.json contains invalid JSON: {e}")
                validation_passed = False
            except Exception as e:
                print(f"❌ Error reading settings.json: {e}")
                validation_passed = False

        # Test hook execution
        execute_hook = self.hooks_dir / 'execute_hook.py'
        if execute_hook.exists():
            print("🔄 Testing hook execution...")
            try:
                result = subprocess.run([
                    sys.executable, str(execute_hook), '--help'
                ], capture_output=True, text=True, timeout=10)

                if result.returncode == 0:
                    print("✅ Hook execution test passed")
                else:
                    print("⚠️  Hook execution test failed (but this may be normal)")
                    if self.verbose and result.stderr:
                        print(f"   Error: {result.stderr.strip()}")

            except subprocess.TimeoutExpired:
                print("⚠️  Hook execution test timed out")
            except Exception as e:
                print(f"⚠️  Hook execution test error: {e}")

        # Environment validation if available
        if UTILS_AVAILABLE and self.env_detector:
            is_valid, issues = self.env_detector.validate_environment()
            if is_valid:
                print("✅ Environment validation passed")
            else:
                print("⚠️  Environment validation found issues:")
                for issue in issues:
                    print(f"   • {issue}")

        return validation_passed

    def _post_installation_setup(self):
        """Show post-installation instructions."""
        print("\n📋 Step 6: Next Steps")
        print("-" * 20)

        # Check for configuration files that need to be set up
        project_files_needed = []

        claude_md = self.project_root / 'CLAUDE.md'
        if not claude_md.exists():
            project_files_needed.append(('CLAUDE.md', 'Team AI instructions'))

        claude_local_md = self.project_root / 'CLAUDE.local.md'
        if not claude_local_md.exists():
            project_files_needed.append(('CLAUDE.local.md', 'Your personal AI settings'))

        mcp_json = self.project_root / '.mcp.json'
        if not mcp_json.exists():
            project_files_needed.append(('.mcp.json', 'API configuration'))

        if project_files_needed:
            print("📄 Configuration files to set up:")
            for filename, description in project_files_needed:
                print(f"   • {filename}: {description}")

            # Check for sample files
            sample_files = []
            for filename, description in project_files_needed:
                sample_path = self.claude_dir / f"copy-to-root-project-rename-to:{filename}"
                if sample_path.exists():
                    sample_files.append((filename, str(sample_path)))

            if sample_files:
                print("\n💡 Copy these sample files to your project root:")
                for filename, sample_path in sample_files:
                    print(f"   cp '{sample_path}' './{filename}'")

        # Check hook protection files
        config_dir = self.hooks_dir / 'config'
        protection_files_needed = []

        allowed_files = config_dir / '__claude_hook__allowed_root_files'
        if not allowed_files.exists():
            protection_files_needed.append('__claude_hook__allowed_root_files')

        valid_paths = config_dir / '__claude_hook__valid_test_paths'
        if not valid_paths.exists():
            protection_files_needed.append('__claude_hook__valid_test_paths')

        if protection_files_needed:
            print("\n🛡️  Hook protection files to configure:")
            for filename in protection_files_needed:
                sample_path = config_dir / f"{filename}.sample"
                if sample_path.exists():
                    target_path = config_dir / filename
                    print(f"   cp '{sample_path}' '{target_path}'")

        # Final instructions
        print("\n🚀 Ready to use Claude Code!")
        print("1. Complete the configuration steps above")
        if mcp_json not in [f[0] for f in project_files_needed]:
            print("2. Make sure your API token is configured in .mcp.json")
        else:
            print("2. Set up .mcp.json with your API token")
        print("3. Run: claude-code .")
        print("4. The AI agents will automatically initialize!")

        # Show environment report if requested
        if self.verbose and UTILS_AVAILABLE:
            print("\n" + "=" * 50)
            print("DETAILED ENVIRONMENT REPORT")
            print("=" * 50)
            print(self.env_detector.generate_environment_report())

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
        description="Claude Code Hooks - Portable Bootstrap Installer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python3 .claude/install_hooks.py
    python3 .claude/install_hooks.py --verbose
    python3 .claude/install_hooks.py --force
        """
    )

    parser.add_argument(
        '--force',
        action='store_true',
        help='Force reinstallation even if already configured'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed output and environment information'
    )

    parser.add_argument(
        '--environment-report',
        action='store_true',
        help='Generate detailed environment report without installing'
    )

    parser.add_argument(
        '--dependency-report',
        action='store_true',
        help='Generate dependency report without installing'
    )

    args = parser.parse_args()

    # Handle report generation
    if args.environment_report:
        if UTILS_AVAILABLE:
            print(generate_environment_report())
        else:
            print("❌ Environment report requires hook utilities to be available")
        return

    if args.dependency_report:
        if UTILS_AVAILABLE:
            print(generate_dependency_report())
        else:
            print("❌ Dependency report requires hook utilities to be available")
        return

    # Run installer
    installer = ClaudeHooksInstaller(
        force_reinstall=args.force,
        verbose=args.verbose
    )

    success = installer.install()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()