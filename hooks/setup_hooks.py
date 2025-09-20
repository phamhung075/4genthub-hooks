#!/usr/bin/env python3
"""
Setup Hooks - Portable hooks configuration setup for Claude Code

This script automatically detects the project root and creates a properly
configured settings.json file from the settings.json.sample template.

Features:
- Auto-detects project root directory
- Replaces {{PROJECT_ROOT}} placeholder with actual absolute path
- Validates that all hook files exist
- Creates settings.json that's gitignored (local to each environment)
- Provides clear success/error messages and troubleshooting guidance

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
"""

import sys
import os
import json
from pathlib import Path


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


def create_settings_from_template(project_root):
    """
    Create settings.json from settings.json.sample template.

    Args:
        project_root: Path to the project root directory

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

        # Replace placeholder with actual project root path
        project_root_str = str(project_root).replace('\\', '/')  # Normalize path separators
        settings_content = template_content.replace('{{PROJECT_ROOT}}', project_root_str)

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

    # Entries to add
    entries_to_add = [
        '.claude/settings.json',
        '# Local Claude Code settings (auto-generated)',
    ]

    # Check and update root .gitignore
    try:
        if gitignore_path.exists():
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                content = f.read()

            if '.claude/settings.json' not in content:
                with open(gitignore_path, 'a', encoding='utf-8') as f:
                    f.write('\n# Local Claude Code settings (auto-generated)\n')
                    f.write('.claude/settings.json\n')
                print(f"✅ Added .claude/settings.json to {gitignore_path}")
            else:
                print(f"ℹ️  .claude/settings.json already in {gitignore_path}")
    except Exception as e:
        print(f"⚠️  Warning: Could not update .gitignore: {e}")

    # Check and update .claude/.gitignore
    try:
        if claude_gitignore_path.exists():
            with open(claude_gitignore_path, 'r', encoding='utf-8') as f:
                content = f.read()

            if 'settings.json' not in content:
                with open(claude_gitignore_path, 'a', encoding='utf-8') as f:
                    f.write('\n# Local settings (auto-generated)\n')
                    f.write('settings.json\n')
                print(f"✅ Added settings.json to {claude_gitignore_path}")
            else:
                print(f"ℹ️  settings.json already in {claude_gitignore_path}")
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
        result = subprocess.run([
            sys.executable, str(execute_hook_path), '--help'
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


def main():
    """Main setup function."""
    print("🚀 Claude Code Hooks Setup")
    print("=" * 50)

    # Find project root
    print("🔍 Finding project root...")
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

    # Create settings from template
    print("\n⚙️  Creating settings.json from template...")
    if not create_settings_from_template(project_root):
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

    # Test hook execution
    test_hook_execution(project_root)

    print("\n🎉 Setup completed successfully!")
    print("\n" + "=" * 70)
    print("📋 NEXT STEPS - Configure Your Project Files")
    print("=" * 70)

    print("\n🔧 **STEP 1: Copy Claude Configuration Files**")
    print("-" * 50)

    # Check if files exist in project root
    claude_md_exists = (project_root / 'CLAUDE.md').exists()
    claude_local_md_exists = (project_root / 'CLAUDE.local.md').exists()
    mcp_json_exists = (project_root / '.claude' / '.mcp.json').exists()

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
        print(f"   cp .claude/.mcp.json.sample .claude/.mcp.json")
        print(f"   nano .claude/.mcp.json  # or use your favorite editor")
        print("\n   🔐 **2.2 - Add Your API Token:**")
        print("   Replace 'YOUR_API_TOKEN_HERE' with your actual token from 4genthub.com")
        print("   Example:")
        print('   "Authorization": "Bearer YOUR_ACTUAL_TOKEN_12345"')
        print("\n   💡 Get your token at: https://www.4genthub.com/dashboard/api-tokens")
    else:
        print("\n✅ .mcp.json already exists")
        print("   ⚠️  Make sure your API token is configured:")
        print(f"   nano .claude/.mcp.json")
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
    print("   • Location: ./.claude/.mcp.json")

    print("\n" + "=" * 70)
    print("✨ **Quick Setup Commands (Copy & Run):**")
    print("=" * 70)

    commands = []
    if not claude_md_exists:
        commands.append("cp .claude/copy-to-root-project-rename-to:CLAUDE.md ./CLAUDE.md")
    if not claude_local_md_exists:
        commands.append("cp .claude/copy-to-root-project-rename-to:CLAUDE.local.md ./CLAUDE.local.md")
    if not mcp_json_exists:
        commands.append("cp .claude/.mcp.json.sample .claude/.mcp.json")
        commands.append("# Edit .claude/.mcp.json to add your API token")

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
    print("1. Make sure you added your API token to .claude/.mcp.json")
    print("2. Review hook protection files (if prompted above)")
    print("3. Run: claude-code .")
    print("4. The AI agents will automatically initialize!")

    print("\n" + "=" * 70)
    print(f"\n✅ Hooks configured at: {project_root}/.claude/settings.json")


if __name__ == "__main__":
    main()