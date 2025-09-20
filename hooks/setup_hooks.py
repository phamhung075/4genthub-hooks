#!/usr/bin/env python3
"""
Setup Hooks - Enhanced Portable hooks configuration setup for Claude Code

This script automatically detects the project root and creates a properly
configured settings.json file from the settings.json.sample template.

Enhanced Features:
- Auto-detects project root directory with improved reliability
- Replaces {{PROJECT_ROOT}} placeholder with actual absolute path
- Cross-platform path handling (Windows, macOS, Linux)
- Enhanced environment detection and validation
- Validates that all hook files exist
- Detects virtual environments and Python executables
- Creates settings.json that's gitignored (local to each environment)
- Provides clear success/error messages and troubleshooting guidance
- Handles git submodule detection
- Graceful dependency handling

Usage:
    python3 .claude/hooks/setup_hooks.py

Requirements:
- .claude/settings.json.sample must exist (template file)
- .claude/hooks/ directory must contain the hook files
- Run from anywhere in the project directory tree

This enables portable .claude folder that works across different:
- Operating systems (Windows, macOS, Linux)
- User directories and project locations
- Development environments and machines
- Virtual environments (venv, conda, pipenv)
- Git repository structures (regular and submodule)
"""

import sys
import os
import json
import platform
import shutil
from pathlib import Path

# Try to import enhanced utilities if available
try:
    # Add utils to path
    script_dir = Path(__file__).parent
    utils_dir = script_dir / 'utils'
    if utils_dir.exists():
        sys.path.insert(0, str(utils_dir))

    from environment_detector import EnvironmentDetector
    from dependency_manager import DependencyManager, setup_default_fallbacks
    ENHANCED_MODE = True
except ImportError:
    ENHANCED_MODE = False


def find_project_root():
    """
    Find the project root by looking for marker files.

    Returns:
        Path to project root or None if not found
    """
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
        Path(__file__).parent.parent.parent if __file__ else Path.cwd()
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
                        # Verify it's a Claude project by checking for .claude/hooks
                        claude_dir = current / '.claude'
                        if claude_dir.exists() and (claude_dir / 'hooks').exists():
                            return current

                current = current.parent

        except (OSError, PermissionError):
            continue

    return None


def validate_hook_files(hooks_dir, config_data):
    """
    Validate that all hook files referenced in the config exist.

    Args:
        hooks_dir: Path to the hooks directory
        config_data: Parsed JSON configuration data

    Returns:
        tuple: (bool success, list of missing files, list of found files)
    """
    missing_files = []
    found_files = []

    # Check status line script if configured
    if 'statusLine' in config_data and 'command' in config_data['statusLine']:
        command = config_data['statusLine']['command']
        # Extract hook filename from command (after execute_hook.py)
        if 'execute_hook.py' in command:
            parts = command.split()
            if len(parts) >= 3:  # python3, execute_hook.py, hook_name
                hook_name = parts[2]
                hook_path = hooks_dir / hook_name
                if hook_path.exists():
                    found_files.append(hook_name)
                else:
                    # Try status_lines directory
                    status_lines_dir = hooks_dir.parent / 'status_lines'
                    if status_lines_dir.exists() and (status_lines_dir / hook_name).exists():
                        found_files.append(f"status_lines/{hook_name}")
                    else:
                        missing_files.append(hook_name)

    # Check hook files in hooks configuration
    if 'hooks' in config_data:
        for hook_type, hook_configs in config_data['hooks'].items():
            for hook_config in hook_configs:
                if 'hooks' in hook_config:
                    for hook in hook_config['hooks']:
                        if hook.get('type') == 'command' and 'command' in hook:
                            command = hook['command']
                            # Extract hook filename from command
                            if 'execute_hook.py' in command:
                                parts = command.split()
                                if len(parts) >= 3:  # python3, execute_hook.py, hook_name
                                    hook_name = parts[2]
                                    hook_path = hooks_dir / hook_name
                                    if hook_path.exists():
                                        found_files.append(hook_name)
                                    else:
                                        missing_files.append(hook_name)

    return len(missing_files) == 0, missing_files, found_files


def create_settings_from_template(project_root, python_executable=None):
    """
    Create settings.json from settings.json.sample template.

    Args:
        project_root: Path to the project root directory
        python_executable: Python executable to use (auto-detected if not provided)

    Returns:
        bool: True if successful, False otherwise
    """
    claude_dir = project_root / '.claude'
    template_path = claude_dir / 'settings.json.sample'
    settings_path = claude_dir / 'settings.json'
    hooks_dir = claude_dir / 'hooks'

    # Check if template exists
    if not template_path.exists():
        print(f"❌ Error: Template file not found: {template_path}")
        print("   Make sure .claude/settings.json.sample exists")
        return False

    # Check if hooks directory exists
    if not hooks_dir.exists():
        print(f"❌ Error: Hooks directory not found: {hooks_dir}")
        print("   Make sure .claude/hooks/ directory exists")
        return False

    try:
        # Read template file
        print(f"📖 Reading template: {template_path}")
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()

        # Use provided or detect Python executable
        if python_executable is None:
            python_executable = get_recommended_python_executable()

        # Cross-platform path handling
        project_root_str = str(project_root)
        if platform.system() == "Windows":
            # On Windows, use forward slashes for consistency in JSON
            project_root_str = project_root_str.replace('\\', '/')

        # Replace placeholders
        settings_content = template_content.replace('{{PROJECT_ROOT}}', project_root_str)
        settings_content = settings_content.replace('{{PYTHON_EXECUTABLE}}', python_executable)

        # Parse JSON to validate structure
        config_data = json.loads(settings_content)

        # Validate hook files exist
        print("🔍 Validating hook files...")
        success, missing_files, found_files = validate_hook_files(hooks_dir, config_data)

        if not success:
            print(f"❌ Error: Missing hook files:")
            for missing in missing_files:
                print(f"   - {missing}")
            print(f"\n   Available in {hooks_dir}:")
            for hook_file in hooks_dir.glob('*.py'):
                print(f"   - {hook_file.name}")
            return False

        # Write settings.json file
        print(f"✍️  Writing settings: {settings_path}")
        with open(settings_path, 'w', encoding='utf-8') as f:
            f.write(settings_content)

        print(f"✅ Successfully created settings.json!")
        print(f"   Project root: {project_root}")
        print(f"   Found {len(found_files)} hook files:")
        for hook in found_files:
            print(f"   - {hook}")

        return True

    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in template: {e}")
        return False
    except Exception as e:
        print(f"❌ Error creating settings: {e}")
        return False


def update_gitignore(project_root):
    """
    Add settings.json to .gitignore if not already present.

    Args:
        project_root: Path to the project root directory
    """
    gitignore_path = project_root / '.gitignore'
    claude_gitignore_path = project_root / '.claude' / '.gitignore'

    # Entries to add to root .gitignore
    entries_to_add = [
        '.claude/settings.json',
        '.claude/hooks/config/__claude_hook__allowed_root_files',
        '.claude/hooks/config/__claude_hook__valid_test_paths'
    ]

    # Check and update root .gitignore
    try:
        if gitignore_path.exists():
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                content = f.read()

            entries_added = []
            for entry in entries_to_add:
                if entry not in content:
                    entries_added.append(entry)

            if entries_added:
                with open(gitignore_path, 'a', encoding='utf-8') as f:
                    f.write('\n# Local Claude Code settings and configs (auto-generated)\n')
                    for entry in entries_added:
                        f.write(f'{entry}\n')
                print(f"✅ Added {len(entries_added)} entries to {gitignore_path}")
                for entry in entries_added:
                    print(f"   • {entry}")
            else:
                print(f"ℹ️  All entries already in {gitignore_path}")
    except Exception as e:
        print(f"⚠️  Warning: Could not update .gitignore: {e}")

    # Check and update .claude/.gitignore
    try:
        # Entries to add to .claude/.gitignore (relative paths from .claude/)
        claude_entries = [
            'settings.json',
            'hooks/config/__claude_hook__allowed_root_files',
            'hooks/config/__claude_hook__valid_test_paths'
        ]

        if claude_gitignore_path.exists():
            with open(claude_gitignore_path, 'r', encoding='utf-8') as f:
                content = f.read()

            entries_added = []
            for entry in claude_entries:
                if entry not in content:
                    entries_added.append(entry)

            if entries_added:
                with open(claude_gitignore_path, 'a', encoding='utf-8') as f:
                    f.write('\n# Local settings and configs (auto-generated)\n')
                    for entry in entries_added:
                        f.write(f'{entry}\n')
                print(f"✅ Added {len(entries_added)} entries to {claude_gitignore_path}")
                for entry in entries_added:
                    print(f"   • {entry}")
            else:
                print(f"ℹ️  All entries already in {claude_gitignore_path}")
    except Exception as e:
        print(f"⚠️  Warning: Could not update .claude/.gitignore: {e}")


def untrack_settings_from_git(project_root):
    """
    Untrack settings.json from git and clean it from history.
    Handles both main repository and .claude submodule cases.

    Args:
        project_root: Path to the project root directory
    """
    import subprocess

    settings_path = '.claude/settings.json'
    claude_dir = project_root / '.claude'

    print("\n🔒 Untracking settings.json from git...")

    try:
        # First, check if .claude is a submodule
        is_submodule = False
        gitmodules_path = project_root / '.gitmodules'
        if gitmodules_path.exists():
            with open(gitmodules_path, 'r', encoding='utf-8') as f:
                if '.claude' in f.read():
                    is_submodule = True
                    print("ℹ️  Detected .claude as a git submodule")

        if is_submodule:
            # Handle submodule case - untrack within the submodule
            print("🔧 Handling submodule settings.json...")

            # Check if settings.json is tracked in the submodule
            result = subprocess.run(['git', 'ls-files', 'settings.json'],
                                  capture_output=True, text=True, cwd=claude_dir)

            if 'settings.json' in result.stdout:
                # File is tracked in submodule, untrack it
                print(f"🔧 Removing settings.json from submodule git tracking...")

                # Remove from submodule index but keep file locally
                result = subprocess.run(['git', 'rm', '--cached', 'settings.json'],
                                      capture_output=True, text=True, cwd=claude_dir)

                if result.returncode == 0:
                    print(f"✅ Successfully untracked settings.json in submodule")
                    print("   The file remains on disk but is no longer tracked")

                    # Check submodule status
                    result = subprocess.run(['git', 'status', '--porcelain', 'settings.json'],
                                          capture_output=True, text=True, cwd=claude_dir)

                    if result.stdout:
                        print(f"   Submodule status: {result.stdout.strip()}")
                        print("\n⚠️  Important: The untracking needs to be committed in the submodule:")
                        print("   Run these commands:")
                        print("   cd .claude")
                        print("   git commit -m 'Untrack settings.json - now local only'")
                        print("   cd ..")
                        print("   git add .claude")
                        print("   git commit -m 'Update .claude submodule'")
                else:
                    print(f"⚠️  Warning: Could not untrack file in submodule: {result.stderr}")
            else:
                print(f"ℹ️  settings.json is not tracked in submodule (good!)")

        else:
            # Handle regular repository case
            # Check if we're in a git repository
            result = subprocess.run(['git', 'status'],
                                  capture_output=True, text=True, cwd=project_root)
            if result.returncode != 0:
                print("ℹ️  Not in a git repository, skipping git operations")
                return

            # Check if settings.json is tracked in main repo
            result = subprocess.run(['git', 'ls-files', settings_path],
                                  capture_output=True, text=True, cwd=project_root)

            if settings_path in result.stdout:
                # File is tracked, untrack it
                print(f"🔧 Removing {settings_path} from git tracking...")

                # Remove from index but keep file locally
                result = subprocess.run(['git', 'rm', '--cached', settings_path],
                                      capture_output=True, text=True, cwd=project_root)

                if result.returncode == 0:
                    print(f"✅ Successfully untracked {settings_path}")
                    print("   The file remains on disk but is no longer tracked by git")

                    # Check git status to confirm
                    result = subprocess.run(['git', 'status', '--porcelain', settings_path],
                                          capture_output=True, text=True, cwd=project_root)

                    if result.stdout:
                        print(f"   Git status: {result.stdout.strip()}")
                        print("\n⚠️  Important: The untracking needs to be committed:")
                        print("   Run: git commit -m 'Untrack .claude/settings.json - now local only'")
                else:
                    print(f"⚠️  Warning: Could not untrack file: {result.stderr}")
            else:
                print(f"ℹ️  {settings_path} is not tracked by git (good!)")

        # Verify file is in .gitignore
        result = subprocess.run(['git', 'check-ignore', settings_path],
                              capture_output=True, text=True, cwd=project_root)

        if result.returncode == 0:
            print(f"✅ {settings_path} is properly ignored by git")
        else:
            print(f"⚠️  Warning: {settings_path} may not be properly ignored")
            print("   Make sure .gitignore contains: .claude/settings.json")

    except FileNotFoundError:
        print("⚠️  Git is not installed or not in PATH, skipping git operations")
    except Exception as e:
        print(f"⚠️  Warning: Could not perform git operations: {e}")


def untrack_hook_configs_from_git(project_root):
    """
    Remove hook configuration files from git tracking if they're currently tracked.
    These files should be local-only for each developer.

    Args:
        project_root: Path to the project root directory
    """
    import subprocess

    print("\n🔒 Untracking hook configuration files from git...")

    # Hook configuration files that should be local-only
    hook_configs = [
        '.claude/hooks/config/__claude_hook__allowed_root_files',
        '.claude/hooks/config/__claude_hook__valid_test_paths'
    ]

    try:
        # First, check if .claude is a submodule
        is_submodule = False
        gitmodules_path = project_root / '.gitmodules'
        if gitmodules_path.exists():
            with open(gitmodules_path, 'r', encoding='utf-8') as f:
                if '.claude' in f.read():
                    is_submodule = True

        for config_file in hook_configs:
            if is_submodule:
                # Handle submodule case
                # Extract just the filename for checking within the submodule
                config_name = Path(config_file).name
                config_dir = project_root / Path(config_file).parent

                # Check if file is tracked in the submodule
                result = subprocess.run(['git', 'ls-files', config_name],
                                      capture_output=True, text=True,
                                      cwd=config_dir)

                if config_name in result.stdout:
                    # File is tracked, untrack it within the submodule
                    print(f"🔧 Removing {config_file} from git submodule tracking...")

                    result = subprocess.run(['git', 'rm', '--cached', config_name],
                                          capture_output=True, text=True,
                                          cwd=config_dir)

                    if result.returncode == 0:
                        print(f"✅ Successfully untracked {config_file}")
                    else:
                        print(f"⚠️  Could not untrack {config_file}: {result.stderr}")
                else:
                    print(f"ℹ️  {config_file} is not tracked (good!)")

            else:
                # Handle regular repository case
                # Check if file is tracked in main repo
                result = subprocess.run(['git', 'ls-files', config_file],
                                      capture_output=True, text=True, cwd=project_root)

                if config_file in result.stdout:
                    # File is tracked, untrack it
                    print(f"🔧 Removing {config_file} from git tracking...")

                    result = subprocess.run(['git', 'rm', '--cached', config_file],
                                          capture_output=True, text=True, cwd=project_root)

                    if result.returncode == 0:
                        print(f"✅ Successfully untracked {config_file}")
                    else:
                        print(f"⚠️  Could not untrack {config_file}: {result.stderr}")
                else:
                    print(f"ℹ️  {config_file} is not tracked (good!)")

    except FileNotFoundError:
        print("⚠️  Git is not installed or not in PATH, skipping git operations")
    except Exception as e:
        print(f"⚠️  Warning: Could not perform git operations: {e}")


def get_recommended_python_executable():
    """Get the recommended Python executable for this environment."""
    current_platform = platform.system()

    # Find available Python executables
    executables = []
    common_names = ['python', 'python3', 'python3.9', 'python3.10', 'python3.11', 'python3.12']

    for name in common_names:
        if shutil.which(name):
            executables.append(name)

    # On Windows, prefer python over python3
    if current_platform == "Windows":
        if 'python' in executables:
            return 'python'
        elif 'python3' in executables:
            return 'python3'
    else:
        # On Unix-like systems, prefer python3 over python
        if 'python3' in executables:
            return 'python3'
        elif 'python' in executables:
            return 'python'

    # Fallback to current executable
    return sys.executable


def test_hook_execution(project_root):
    """
    Test that hook execution works with the new settings.

    Args:
        project_root: Path to the project root directory
    """
    print("\n🧪 Testing hook execution...")

    execute_hook_path = project_root / '.claude' / 'hooks' / 'execute_hook.py'

    if not execute_hook_path.exists():
        print("⚠️  Warning: execute_hook.py not found, skipping test")
        return

    try:
        # Test with a simple hook that should exist
        import subprocess
        python_exe = get_recommended_python_executable()
        result = subprocess.run([
            python_exe, str(execute_hook_path), '--help'
        ], capture_output=True, text=True, timeout=10)

        if result.returncode == 0:
            print("✅ Hook execution test successful!")
        else:
            print(f"⚠️  Warning: Hook execution test failed (return code: {result.returncode})")
            if result.stderr:
                print(f"   Error: {result.stderr}")

    except subprocess.TimeoutExpired:
        print("⚠️  Warning: Hook execution test timed out")
    except Exception as e:
        print(f"⚠️  Warning: Could not test hook execution: {e}")


def fix_infinite_loop_in_hook():
    """Fix the infinite loop issue in pre_tool_use.py hook."""
    print("\n🔧 Fixing infinite loop in pre_tool_use.py...")

    project_root = find_project_root()
    hook_file = project_root / '.claude' / 'hooks' / 'pre_tool_use.py'

    if not hook_file.exists():
        print(f"⚠️ Hook file not found: {hook_file}")
        return False

    # Read the current hook content
    content = hook_file.read_text()

    # Check if already fixed
    if '_recursion_depth' in content or 'RECURSION_CHECK' in content:
        print("ℹ️ Hook already has recursion protection")
        return True

    # Find line 356 where get_hint_system is imported
    lines = content.split('\n')

    # Add recursion check at the top of the file after imports
    recursion_check = """
# Recursion prevention - add after imports
import os
_RECURSION_CHECK_VAR = 'CLAUDE_HOOK_RECURSION_DEPTH'

def _is_recursive_call():
    \"\"\"Check if we're in a recursive hook call.\"\"\"
    depth = int(os.environ.get(_RECURSION_CHECK_VAR, '0'))
    return depth > 0

def _enter_recursion():
    \"\"\"Mark entering a recursive section.\"\"\"
    depth = int(os.environ.get(_RECURSION_CHECK_VAR, '0'))
    os.environ[_RECURSION_CHECK_VAR] = str(depth + 1)

def _exit_recursion():
    \"\"\"Mark exiting a recursive section.\"\"\"
    depth = int(os.environ.get(_RECURSION_CHECK_VAR, '0'))
    if depth > 0:
        os.environ[_RECURSION_CHECK_VAR] = str(depth - 1)
"""

    # Insert recursion check after the imports section
    import_end_index = 0
    for i, line in enumerate(lines):
        if line.startswith('from utils.unified_hint_system import get_hint_system'):
            # Found the problematic import, insert our fix after it
            lines.insert(i + 1, recursion_check)
            import_end_index = i + 1
            break

    # Now modify the calls to get_hint_system to check for recursion
    for i in range(import_end_index, len(lines)):
        # Line 356 - HintProcessor
        if 'hint_system = get_hint_system()' in lines[i]:
            indent = len(lines[i]) - len(lines[i].lstrip())
            lines[i] = ' ' * indent + 'if not _is_recursive_call():\n' + ' ' * (indent + 4) + 'hint_system = get_hint_system()\n' + ' ' * indent + 'else:\n' + ' ' * (indent + 4) + 'hint_system = None'

        # Line 503 - main execute method
        if 'hint_system = get_hint_system()' in lines[i] and 'unified hint system' in lines[i-1]:
            indent = len(lines[i]) - len(lines[i].lstrip())
            lines[i] = ' ' * indent + 'if not _is_recursive_call():\n' + ' ' * (indent + 4) + '_enter_recursion()\n' + ' ' * (indent + 4) + 'try:\n' + ' ' * (indent + 8) + 'hint_system = get_hint_system()\n' + ' ' * (indent + 4) + 'finally:\n' + ' ' * (indent + 8) + '_exit_recursion()\n' + ' ' * indent + 'else:\n' + ' ' * (indent + 4) + 'hint_system = None'

    # Create backup
    backup_file = hook_file.with_suffix('.py.backup_loop_fix')
    shutil.copy2(hook_file, backup_file)
    print(f"✅ Created backup at: {backup_file}")

    # Write the fixed content
    fixed_content = '\n'.join(lines)
    hook_file.write_text(fixed_content)
    print(f"✅ Fixed infinite loop protection in: {hook_file}")

    return True

def main():
    """Enhanced main setup function with environment detection."""
    print("🚀 Claude Code Hooks Setup (Enhanced)")
    print("=" * 50)

    # Initialize enhanced components if available
    env_detector = None
    dep_manager = None

    if ENHANCED_MODE:
        print("✅ Enhanced mode enabled - using environment detection")
    else:
        print("⚠️  Basic mode - enhanced utilities not available")

    # Find project root
    print("\n🔍 Finding project root...")
    project_root = find_project_root()
    if not project_root:
        print("❌ Error: Could not find project root")
        print("\nTroubleshooting:")
        print("1. Make sure you're running this from within a project directory")
        print("2. Ensure one of these files exists in your project root:")
        print("   - CLAUDE.md, .git, package.json, pyproject.toml, .env")
        print("3. Make sure .claude/hooks/ directory exists")
        sys.exit(1)

    print(f"✅ Found project root: {project_root}")

    # Enhanced environment detection
    if ENHANCED_MODE:
        try:
            env_detector = EnvironmentDetector(project_root)
            dep_manager = DependencyManager(project_root)
            setup_default_fallbacks(dep_manager)

            print("\n🌍 Environment Detection:")
            env_info = env_detector.get_environment_info()

            # Platform info
            platform_info = env_info['platform']
            print(f"   • Platform: {platform_info['system']} {platform_info['release']}")
            print(f"   • Architecture: {platform_info['machine']} ({platform_info['architecture']})")

            # Python info
            python_info = env_info['python']
            print(f"   • Python: {python_info['version_info']['major']}.{python_info['version_info']['minor']}.{python_info['version_info']['micro']}")

            # Virtual environment
            venv_info = env_info['virtual_env']
            if venv_info['is_virtual_env']:
                print(f"   • Virtual Environment: {venv_info['type']} ({venv_info['name']})")
            else:
                print(f"   • Virtual Environment: Not detected")

            # Git info
            git_info = env_info['git']
            if git_info['is_git_repo']:
                print(f"   • Git Repository: {git_info['current_branch']}")
                if git_info['is_submodule']:
                    print(f"   • .claude is a git submodule: Yes")
            else:
                print(f"   • Git Repository: Not detected")

            # Validate environment
            is_valid, issues = env_detector.validate_environment()
            if is_valid:
                print("   ✅ Environment validation passed")
            else:
                print("   ⚠️  Environment issues found:")
                for issue in issues:
                    print(f"      • {issue}")

            # Check dependencies
            print("\n📦 Dependency Check:")
            dep_status = dep_manager.check_dependencies()
            available_count = sum(1 for status in dep_status['available'].values() if status)
            missing_count = len(dep_status['missing'])

            print(f"   • Available packages: {available_count}")
            if missing_count > 0:
                print(f"   • Missing packages: {missing_count} (fallbacks available)")

        except Exception as e:
            print(f"   ⚠️  Error in enhanced detection: {e}")
            print("   Continuing with basic setup...")

    # Cross-platform compatibility check
    print(f"\n🖥️  Platform Compatibility:")
    current_platform = platform.system()
    print(f"   • Detected platform: {current_platform}")

    if current_platform == "Windows":
        print("   • Windows compatibility: Enabled")
        print("   • Path separator: Backslash (\\)")
    elif current_platform == "Darwin":
        print("   • macOS compatibility: Enabled")
        print("   • Path separator: Forward slash (/)")
    elif current_platform == "Linux":
        print("   • Linux compatibility: Enabled")
        print("   • Path separator: Forward slash (/)")
        # Check for WSL
        try:
            with open('/proc/version', 'r') as f:
                if 'microsoft' in f.read().lower():
                    print("   • WSL detected: Yes")
        except (FileNotFoundError, PermissionError):
            pass
    else:
        print(f"   • {current_platform}: Basic support")

    # Python executable detection
    print(f"\n🐍 Python Environment:")
    python_exe = get_recommended_python_executable()
    print(f"   • Recommended executable: {python_exe}")
    print(f"   • Current executable: {sys.executable}")

    # Create settings from template
    print("\n⚙️  Creating settings.json from template...")
    if not create_settings_from_template(project_root, python_exe):
        print("\n❌ Setup failed!")
        print("\nTroubleshooting:")
        print("1. Ensure .claude/settings.json.sample exists and has valid JSON")
        print("2. Check that all referenced hook files exist in .claude/hooks/")
        print("3. Verify you have write permissions in the .claude directory")
        sys.exit(1)

    # Update .gitignore files
    print("\n📝 Updating .gitignore files...")
    update_gitignore(project_root)

    # Untrack settings.json from git
    untrack_settings_from_git(project_root)

    # Untrack hook configuration files from git
    untrack_hook_configs_from_git(project_root)

    # Test hook execution
    test_hook_execution(project_root)

    # Fix infinite loop issue
    print("\n🔐 Checking for infinite loop issues...")
    if fix_infinite_loop_in_hook():
        print("✅ Infinite loop protection is in place")
    else:
        print("⚠️ Could not add infinite loop protection automatically")

    print("\n🎉 Setup completed successfully!")
    print("\n" + "=" * 70)
    print("📋 NEXT STEPS - Configure Your Project Files")
    print("=" * 70)

    print("\n🔧 **STEP 1: Copy Claude Configuration Files**")
    print("-" * 50)

    # Check if files exist in project root
    claude_md_exists = (project_root / 'CLAUDE.md').exists()
    claude_local_md_exists = (project_root / 'CLAUDE.local.md').exists()
    mcp_json_exists = (project_root / '.mcp.json').exists()

    if not claude_md_exists:
        print("\n📄 **1.1 - Create CLAUDE.md (Team AI Instructions)**")
        print("   This file contains shared AI agent behavior rules for your team.")
        print("   ✅ Run this command:")
        print(f"   cp .claude/copy-to-root-project-rename-to:CLAUDE.md ./CLAUDE.md")
        print("   📝 Purpose: Defines how AI agents work in your project (checked into git)")
    else:
        print("\n✅ CLAUDE.md already exists in project root")

    if not claude_local_md_exists:
        print("\n📄 **1.2 - Create CLAUDE.local.md (Your Local Settings)**")
        print("   This file contains YOUR personal AI configuration (not shared).")
        print("   ✅ Run this command:")
        print(f"   cp .claude/copy-to-root-project-rename-to:CLAUDE.local.md ./CLAUDE.local.md")
        print("   📝 Purpose: Your personal AI rules and settings (NOT checked into git)")
    else:
        print("\n✅ CLAUDE.local.md already exists in project root")

    print("\n" + "-" * 50)
    print("🔑 **STEP 2: Configure API Access**")
    print("-" * 50)

    if not mcp_json_exists:
        print("\n📄 **2.1 - Create .mcp.json (API Configuration)**")
        print("   This connects Claude Code to the 4genthub service.")
        print("   ✅ Run these commands:")
        print(f"   cp .claude/.mcp.json.sample .mcp.json")
        print(f"   nano .mcp.json  # or use your favorite editor")
        print("\n   🔐 **2.2 - Add Your API Token:**")
        print("   Replace 'YOUR_API_TOKEN_HERE' with your actual token from 4genthub.com")
        print("   Example:")
        print('   "Authorization": "Bearer YOUR_ACTUAL_TOKEN_12345"')
        print("\n   💡 Get your token at: https://www.4genthub.com/dashboard/api-tokens")
    else:
        print("\n✅ .mcp.json already exists")
        print("   ⚠️  Make sure your API token is configured:")
        print(f"   nano .mcp.json")
        print('   Check that "Authorization" has your actual token, not placeholder')

    print("\n" + "=" * 70)
    print("📝 **File Descriptions:**")
    print("=" * 70)

    print("\n1️⃣  **CLAUDE.md** (Team Shared)")
    print("   • Defines AI agent behavior for entire team")
    print("   • Contains project-wide AI rules and workflows")
    print("   • Checked into git - everyone uses same rules")
    print("   • Location: ./CLAUDE.md (project root)")

    print("\n2️⃣  **CLAUDE.local.md** (Your Personal)")
    print("   • Your personal AI configuration")
    print("   • Local environment settings")
    print("   • NOT checked into git - stays on your machine")
    print("   • Location: ./CLAUDE.local.md (project root)")

    print("\n3️⃣  **.mcp.json** (API Connection)")
    print("   • Connects to 4genthub hosted service")
    print("   • Contains your API authentication token")
    print("   • Required for AI agents to work")
    print("   • Location: ./.mcp.json (project root)")

    print("\n4️⃣  **__claude_hook__allowed_root_files.sample** (Root File Protection)")
    print("   • Template for controlling what files AI can create in project root")
    print("   • Lists allowed files like README.md, package.json, etc.")
    print("   • Copy to __claude_hook__allowed_root_files (without .sample)")
    print("   • Location: ./.claude/hooks/config/")

    print("\n5️⃣  **__claude_hook__valid_test_paths.sample** (Test Directory Protection)")
    print("   • Template defining where test files can be created")
    print("   • Includes paths like src/tests, .claude/hooks/tests, etc.")
    print("   • Copy to __claude_hook__valid_test_paths (without .sample)")
    print("   • Location: ./.claude/hooks/config/")

    print("\n" + "=" * 70)
    print("✨ **Quick Setup Commands (Copy & Run):**")
    print("=" * 70)

    commands = []
    if not claude_md_exists:
        commands.append("cp .claude/copy-to-root-project-rename-to:CLAUDE.md ./CLAUDE.md")
    if not claude_local_md_exists:
        commands.append("cp .claude/copy-to-root-project-rename-to:CLAUDE.local.md ./CLAUDE.local.md")
    if not mcp_json_exists:
        commands.append("cp .claude/.mcp.json.sample .mcp.json")
        commands.append("# Edit .mcp.json to add your API token")

    if commands:
        print("\n# Copy these commands:")
        for cmd in commands:
            print(cmd)
    else:
        print("\n✅ All configuration files already exist!")

    print("\n" + "=" * 70)
    print("🔒 **STEP 3: Configure Hook Protection Files**")
    print("=" * 70)

    # Check hook configuration files
    config_dir = project_root / '.claude' / 'hooks' / 'config'
    allowed_files = config_dir / '__claude_hook__allowed_root_files'
    valid_paths = config_dir / '__claude_hook__valid_test_paths'

    print("\n🛡️  **Hook Protection Files:**")
    print("These files control what Claude Code can create in your project.")
    print("-" * 50)

    if not allowed_files.exists():
        print("\n⚠️  **Missing: __claude_hook__allowed_root_files**")
        print("   This file controls which files can be created in project root.")
        print("   ✅ Create it from sample:")
        print(f"   cp .claude/hooks/config/__claude_hook__allowed_root_files.sample \\")
        print(f"      .claude/hooks/config/__claude_hook__allowed_root_files")
        print("   📝 Then edit to match YOUR project's allowed root files")
    else:
        print("\n✅ __claude_hook__allowed_root_files exists")
        print("   ℹ️  Review it to ensure it matches your project:")
        print(f"   nano .claude/hooks/config/__claude_hook__allowed_root_files")

    if not valid_paths.exists():
        print("\n⚠️  **Missing: __claude_hook__valid_test_paths**")
        print("   This file controls where test files can be created.")
        print("   ✅ Create it from sample:")
        print(f"   cp .claude/hooks/config/__claude_hook__valid_test_paths.sample \\")
        print(f"      .claude/hooks/config/__claude_hook__valid_test_paths")
        print("   📝 Then edit to match YOUR project's test directories")
    else:
        print("\n✅ __claude_hook__valid_test_paths exists")
        print("   ℹ️  Review it to ensure it matches your test structure:")
        print(f"   nano .claude/hooks/config/__claude_hook__valid_test_paths")

    print("\n💡 **Why These Files Matter:**")
    print("   • Prevents AI from creating files in wrong locations")
    print("   • Protects your project structure")
    print("   • Ensures tests go in test directories")
    print("   • Keeps root directory clean")

    # Generate commands if needed
    hook_commands = []
    if not allowed_files.exists():
        hook_commands.append("cp .claude/hooks/config/__claude_hook__allowed_root_files.sample .claude/hooks/config/__claude_hook__allowed_root_files")
    if not valid_paths.exists():
        hook_commands.append("cp .claude/hooks/config/__claude_hook__valid_test_paths.sample .claude/hooks/config/__claude_hook__valid_test_paths")

    if hook_commands:
        print("\n" + "=" * 70)
        print("✨ **Hook Configuration Commands:**")
        print("=" * 70)
        print("\n# Copy these commands to set up hook protection:")
        for cmd in hook_commands:
            print(cmd)
        print("\n# Then edit the files to match your project structure")

    print("\n" + "=" * 70)
    print("🚀 **Final Step: Start Claude Code**")
    print("=" * 70)
    print("Once you've completed the above steps:")
    print("1. Make sure you added your API token to .mcp.json")
    print("2. Review hook protection files (if prompted above)")
    print("3. Run: claude-code .")
    print("4. The AI agents will automatically initialize!")

    print("\n" + "=" * 70)
    print(f"\n✅ Hooks configured at: {project_root}/.claude/settings.json")


if __name__ == "__main__":
    main()