#!/usr/bin/env python3
"""
.claude Configuration Setup Script

This script automates the setup of .claude configuration for new projects or PCs.
It auto-detects Python paths, prompts for user preferences, and generates all
necessary configuration files.

Usage:
    python .claude/setup.py
    # or
    python3 .claude/setup.py
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional, Dict, List


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'


class ClaudeSetup:
    """Main setup orchestrator for .claude configuration"""

    def __init__(self):
        self.claude_dir = Path(__file__).parent.resolve()
        self.project_root = self.claude_dir.parent
        self.python_path: Optional[str] = None
        self.ai_tool_choice: str = ""
        self.token_strategy: str = ""  # 'economic' or 'performance'
        self.use_venv: bool = True  # Use virtual environment by default
        self.venv_path: Optional[Path] = None

    def print_header(self):
        """Print welcome header"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}╔════════════════════════════════════════════╗{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}║   .claude Configuration Setup Wizard      ║{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}╚════════════════════════════════════════════╝{Colors.END}\n")
        print(f"Project root: {Colors.YELLOW}{self.project_root}{Colors.END}\n")

    def detect_python_path(self) -> Optional[str]:
        """
        Auto-detect Python path using multiple strategies.

        Tries in order:
        1. pyenv (if available)
        2. Current Python interpreter
        3. which python3
        4. which python

        Returns:
            str: Full path to Python executable, or None if detection failed
        """
        detection_methods = [
            ("Current interpreter", sys.executable),
            ("pyenv shims", self._check_command("pyenv which python3")),
            ("pyenv shims python", self._check_command("pyenv which python")),
            ("which python3", self._check_command("which python3")),
            ("which python", self._check_command("which python")),
        ]

        print(f"{Colors.BOLD}Detecting Python path...{Colors.END}")

        for method_name, path in detection_methods:
            if path and os.path.isfile(path):
                print(f"  ✓ Found via {method_name}: {Colors.GREEN}{path}{Colors.END}")
                return path
            else:
                print(f"  ✗ {method_name}: not found")

        return None

    def _check_command(self, command: str) -> Optional[str]:
        """Execute a shell command and return output, or None if failed"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except (subprocess.TimeoutExpired, Exception):
            pass
        return None

    def prompt_python_path(self) -> str:
        """
        Prompt user for Python path with auto-detected default.

        Returns:
            str: Validated Python path
        """
        detected = self.detect_python_path()

        if detected:
            print(f"\n{Colors.BOLD}Python path detected:{Colors.END} {Colors.GREEN}{detected}{Colors.END}")
            response = input(f"Use this path? [{Colors.GREEN}Y{Colors.END}/n]: ").strip().lower()

            if response in ('', 'y', 'yes'):
                return detected

        # Manual input
        while True:
            print(f"\n{Colors.YELLOW}Please enter the full path to your Python executable:{Colors.END}")
            print(f"  Examples:")
            print(f"    - /usr/bin/python3")
            print(f"    - /home/user/.pyenv/shims/python3")
            print(f"    - /usr/local/bin/python")

            path = input(f"\nPython path: ").strip()

            if os.path.isfile(path):
                return path
            else:
                print(f"{Colors.RED}✗ File not found: {path}{Colors.END}")
                print(f"  Please enter a valid path to Python executable.\n")

    def prompt_ai_tool_choice(self) -> str:
        """
        Ask user which AI tool they're using.

        Returns:
            str: 'claude', 'codex', or 'both'
        """
        print(f"\n{Colors.BOLD}Which AI coding tool are you using?{Colors.END}")
        print(f"  {Colors.BLUE}[1]{Colors.END} Claude Code (Anthropic)")
        print(f"  {Colors.BLUE}[2]{Colors.END} OpenAI Codex")
        print(f"  {Colors.BLUE}[3]{Colors.END} Both")

        while True:
            choice = input(f"\nChoice [1-3]: ").strip()

            if choice == '1':
                return 'claude'
            elif choice == '2':
                return 'codex'
            elif choice == '3':
                return 'both'
            else:
                print(f"{Colors.RED}Invalid choice. Please enter 1, 2, or 3.{Colors.END}")

    def prompt_token_strategy(self) -> str:
        """
        Ask user which token optimization strategy they prefer.

        Returns:
            str: 'economic' or 'performance'
        """
        print(f"\n{Colors.BOLD}Token Optimization Strategy:{Colors.END}")
        print(f"  {Colors.BLUE}[1]{Colors.END} Economic (Balanced - saves tokens, good performance)")
        print(f"  {Colors.BLUE}[2]{Colors.END} Max Performance (Token burn — maximum context, best for multiple subagent delegation.)")
        print(f"\n  {Colors.YELLOW}Recommendation:{Colors.END} Use Economic for most projects")

        while True:
            choice = input(f"\nChoice [1-2, default: 1]: ").strip() or '1'

            if choice == '1':
                return 'economic'
            elif choice == '2':
                return 'performance'
            else:
                print(f"{Colors.RED}Invalid choice. Please enter 1 or 2.{Colors.END}")

    def prompt_venv_usage(self) -> bool:
        """
        Ask user if they want to use a virtual environment for hooks.

        Returns:
            bool: True to use venv, False to use system Python
        """
        print(f"\n{Colors.BOLD}Python Environment for Hooks:{Colors.END}")
        print(f"  {Colors.BLUE}[1]{Colors.END} Virtual Environment (Recommended - isolated dependencies)")
        print(f"  {Colors.BLUE}[2]{Colors.END} System Python (Use existing Python installation)")
        print(f"\n  {Colors.YELLOW}Recommendation:{Colors.END} Use virtual environment for better isolation")

        while True:
            choice = input(f"\nChoice [1-2, default: 1]: ").strip() or '1'

            if choice == '1':
                return True
            elif choice == '2':
                return False
            else:
                print(f"{Colors.RED}Invalid choice. Please enter 1 or 2.{Colors.END}")

    def detect_project_structure(self) -> Dict[str, List[str]]:
        """
        Auto-detect project structure to suggest test paths.

        Returns:
            dict: Detected paths for tests, etc.
        """
        test_paths = []

        # Common test directory patterns
        test_patterns = [
            'tests',
            'test',
            'src/tests',
            '*/tests',
            '*/src/tests',
            '__tests__',
            'src/__tests__',
        ]

        for pattern in test_patterns:
            matching_dirs = list(self.project_root.glob(pattern))
            for dir_path in matching_dirs:
                if dir_path.is_dir():
                    rel_path = dir_path.relative_to(self.project_root)
                    test_paths.append(str(rel_path))

        return {'test_paths': sorted(set(test_paths))}

    def create_virtual_environment(self) -> bool:
        """
        Create a virtual environment in .claude/.venv

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.use_venv:
            print(f"\n{Colors.BOLD}Skipping virtual environment creation...{Colors.END}")
            return True

        print(f"\n{Colors.BOLD}Creating virtual environment...{Colors.END}")

        venv_path = self.claude_dir / '.venv'
        self.venv_path = venv_path

        if venv_path.exists():
            print(f"  ⊙ Virtual environment already exists at: {venv_path}")
            response = input(f"  Recreate it? [y/N]: ").strip().lower()
            if response in ('y', 'yes'):
                print(f"  Removing existing venv...")
                shutil.rmtree(venv_path)
            else:
                print(f"  Using existing venv")
                return True

        try:
            # Create venv using the detected Python
            print(f"  Creating venv at: {Colors.YELLOW}{venv_path}{Colors.END}")
            result = subprocess.run(
                [self.python_path, '-m', 'venv', str(venv_path)],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                print(f"{Colors.RED}✗ Failed to create virtual environment:{Colors.END}")
                print(f"{result.stderr}")
                return False

            print(f"  ✓ Created: {Colors.GREEN}{venv_path}{Colors.END}")

            # Update python_path to use venv
            if sys.platform == 'win32':
                self.python_path = str(venv_path / 'Scripts' / 'python.exe')
            else:
                self.python_path = str(venv_path / 'bin' / 'python3')

            print(f"  ✓ Updated Python path to venv: {Colors.GREEN}{self.python_path}{Colors.END}")
            return True

        except subprocess.TimeoutExpired:
            print(f"{Colors.RED}✗ Timeout while creating virtual environment{Colors.END}")
            return False
        except Exception as e:
            print(f"{Colors.RED}✗ Error creating virtual environment: {e}{Colors.END}")
            return False

    def install_hook_dependencies(self) -> bool:
        """
        Install required dependencies for hooks in the virtual environment

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.use_venv:
            print(f"\n{Colors.BOLD}Skipping dependency installation (using system Python)...{Colors.END}")
            print(f"  {Colors.YELLOW}⚠  Make sure these packages are installed:{Colors.END}")
            print(f"     - python-dotenv")
            print(f"     - psutil")
            print(f"     - pyyaml")
            return True

        print(f"\n{Colors.BOLD}Installing hook dependencies...{Colors.END}")

        dependencies = ['python-dotenv', 'psutil', 'pyyaml']

        # Determine pip path
        if sys.platform == 'win32':
            pip_path = self.venv_path / 'Scripts' / 'pip.exe'
        else:
            pip_path = self.venv_path / 'bin' / 'pip'

        if not pip_path.exists():
            print(f"{Colors.RED}✗ pip not found in venv: {pip_path}{Colors.END}")
            return False

        try:
            print(f"  Installing: {Colors.YELLOW}{', '.join(dependencies)}{Colors.END}")

            result = subprocess.run(
                [str(pip_path), 'install', '--quiet'] + dependencies,
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode != 0:
                print(f"{Colors.RED}✗ Failed to install dependencies:{Colors.END}")
                print(f"{result.stderr}")
                return False

            print(f"  ✓ Installed: {Colors.GREEN}{', '.join(dependencies)}{Colors.END}")
            return True

        except subprocess.TimeoutExpired:
            print(f"{Colors.RED}✗ Timeout while installing dependencies{Colors.END}")
            return False
        except Exception as e:
            print(f"{Colors.RED}✗ Error installing dependencies: {e}{Colors.END}")
            return False

    def generate_settings_json(self):
        """Generate settings.json from template with user's Python path"""
        template_path = self.claude_dir / 'templates' / 'settings.json.template'
        output_path = self.claude_dir / 'settings.json'

        print(f"\n{Colors.BOLD}Generating settings.json...{Colors.END}")

        if not template_path.exists():
            print(f"{Colors.RED}✗ Template not found: {template_path}{Colors.END}")
            return False

        # Read template
        with open(template_path, 'r') as f:
            template_content = f.read()

        # Replace placeholders
        replacements = {
            '{{PYTHON_PATH}}': self.python_path,
            '{{PROJECT_ROOT}}': str(self.project_root),
            '{{PYTHON_PATH_ENV}}': 'agenthub_main/src',  # This can be customized
        }

        content = template_content
        for placeholder, value in replacements.items():
            content = content.replace(placeholder, value)

        # Validate JSON
        try:
            json.loads(content)
        except json.JSONDecodeError as e:
            print(f"{Colors.RED}✗ Generated invalid JSON: {e}{Colors.END}")
            return False

        # Write settings.json
        with open(output_path, 'w') as f:
            f.write(content)

        print(f"  ✓ Created: {Colors.GREEN}{output_path}{Colors.END}")

        if self.use_venv:
            print(f"  {Colors.BLUE}ℹ  Using virtual environment Python: {self.python_path}{Colors.END}")
        else:
            print(f"  {Colors.BLUE}ℹ  Using system Python: {self.python_path}{Colors.END}")

        return True

    def setup_config_files(self):
        """Copy .sample files to actual config files if they don't exist"""
        config_dir = self.claude_dir / 'hooks' / 'config'

        print(f"\n{Colors.BOLD}Setting up configuration files...{Colors.END}")

        sample_files = [
            '__claude_hook__allowed_root_files.sample',
            '__claude_hook__valid_test_paths.sample',
        ]

        for sample_file in sample_files:
            sample_path = config_dir / sample_file
            target_path = config_dir / sample_file.replace('.sample', '')

            if not sample_path.exists():
                print(f"  ⚠ Sample file not found: {sample_file}")
                continue

            if target_path.exists():
                print(f"  ⊙ Already exists: {target_path.name}")
            else:
                shutil.copy(sample_path, target_path)
                print(f"  ✓ Created: {Colors.GREEN}{target_path.name}{Colors.END}")

        # Detect and suggest test paths
        detected = self.detect_project_structure()
        if detected['test_paths']:
            print(f"\n  {Colors.BLUE}Detected test directories:{Colors.END}")
            for path in detected['test_paths']:
                print(f"    - {path}")
            print(f"  {Colors.YELLOW}Consider adding these to __claude_hook__valid_test_paths{Colors.END}")

    def deploy_rules_files(self):
        """Copy rules files to project root based on user's AI tool choice"""
        print(f"\n{Colors.BOLD}Deploying rules files...{Colors.END}")

        # Determine which version of CLAUDE.md to use based on token strategy
        if self.token_strategy == 'economic':
            claude_main_file = 'RULE_CLAUDECODE_version_economic_token__copy-to-root-project-rename-to:CLAUDE.md'
            codex_file = 'RULE_OPENAICODEX_version_economic_token__copy-to-root-project-rename-to:AGENTS.md'
        else:  # performance
            claude_main_file = 'RULE_CLAUDECODE_version_max_performance_token_burn__copy-to-root-project-rename-to:CLAUDE.md'
            codex_file = 'RULE_OPENAICODEX__copy-to-root-project-rename-to:AGENTS.md'

        rules_map = {
            'claude': [
                (f'claude-rules/{claude_main_file}', 'CLAUDE.md'),
                ('claude-rules/CLAUDE.local.md.placeholder', 'CLAUDE.local.md'),
            ],
            'codex': [
                (f'codex-rules/{codex_file}', 'AGENTS.md'),
            ],
        }

        files_to_copy = []
        if self.ai_tool_choice in ('claude', 'both'):
            files_to_copy.extend(rules_map['claude'])
        if self.ai_tool_choice in ('codex', 'both'):
            files_to_copy.extend(rules_map['codex'])

        for source_rel, target_name in files_to_copy:
            source_path = self.claude_dir / 'templates' / source_rel
            target_path = self.project_root / target_name

            if not source_path.exists():
                print(f"  ⚠ Source file not found: {source_rel}")
                continue

            if target_path.exists():
                response = input(f"  ⊙ {target_name} exists. Overwrite? [y/N]: ").strip().lower()
                if response not in ('y', 'yes'):
                    print(f"    Skipped: {target_name}")
                    continue

            shutil.copy(source_path, target_path)
            print(f"  ✓ Deployed: {Colors.GREEN}{target_name}{Colors.END}")

    def deploy_env_claude(self):
        """Copy .env.claude.sample to project root as .env.claude"""
        print(f"\n{Colors.BOLD}Deploying environment configuration...{Colors.END}")

        source_path = self.claude_dir / 'templates' / '.env.claude.sample'
        target_path = self.project_root / '.env.claude'

        if not source_path.exists():
            print(f"  ⚠ Source file not found: .env.claude.sample")
            print(f"  {Colors.YELLOW}Skipping .env.claude deployment{Colors.END}")
            return

        if target_path.exists():
            response = input(f"  ⊙ .env.claude exists. Overwrite? [y/N]: ").strip().lower()
            if response not in ('y', 'yes'):
                print(f"    Skipped: .env.claude")
                return

        shutil.copy(source_path, target_path)
        print(f"  ✓ Deployed: {Colors.GREEN}.env.claude{Colors.END}")
        print(f"  {Colors.BLUE}ℹ  Edit .env.claude to configure Claude Code environment variables{Colors.END}")

    def deploy_mcp_config(self):
        """Copy .mcp.json.sample to project root as .mcp.json and ensure it's in .gitignore"""
        print(f"\n{Colors.BOLD}Deploying MCP configuration...{Colors.END}")

        source_path = self.claude_dir / 'templates' / '.mcp.json.sample'
        target_path = self.project_root / '.mcp.json'

        if not source_path.exists():
            print(f"  ⚠ Source file not found: .mcp.json.sample")
            print(f"  {Colors.YELLOW}Skipping .mcp.json deployment{Colors.END}")
            return

        if target_path.exists():
            response = input(f"  ⊙ .mcp.json exists. Overwrite? [y/N]: ").strip().lower()
            if response not in ('y', 'yes'):
                print(f"    Skipped: .mcp.json")
                self._ensure_mcp_in_gitignore()
                return

        shutil.copy(source_path, target_path)
        print(f"  ✓ Deployed: {Colors.GREEN}.mcp.json{Colors.END}")
        print(f"  {Colors.BLUE}ℹ  Edit .mcp.json to configure MCP servers and API tokens{Colors.END}")

        # Ensure .mcp.json is in .gitignore
        self._ensure_mcp_in_gitignore()

    def _ensure_mcp_in_gitignore(self):
        """Ensure .mcp.json is listed in .gitignore to prevent committing secrets"""
        gitignore_path = self.project_root / '.gitignore'

        if not gitignore_path.exists():
            # Create .gitignore with .mcp.json entry
            with open(gitignore_path, 'w') as f:
                f.write("# MCP configuration with potential secrets\n")
                f.write(".mcp.json\n")
            print(f"  ✓ Created .gitignore with .mcp.json entry")
            return

        # Check if .mcp.json is already in .gitignore
        with open(gitignore_path, 'r') as f:
            gitignore_content = f.read()

        if '.mcp.json' in gitignore_content:
            print(f"  ✓ .mcp.json already in .gitignore")
        else:
            # Append .mcp.json to .gitignore
            with open(gitignore_path, 'a') as f:
                f.write("\n# MCP configuration with potential secrets\n")
                f.write(".mcp.json\n")
            print(f"  ✓ Added .mcp.json to .gitignore")

    def verify_hooks(self) -> bool:
        """
        Verify that hooks are working by testing a simple hook

        Returns:
            bool: True if verification passed, False otherwise
        """
        print(f"\n{Colors.BOLD}Verifying hook functionality...{Colors.END}")

        # Test notification hook as it's simple and doesn't require much context
        notification_hook = self.claude_dir / 'hooks' / 'notification.py'

        if not notification_hook.exists():
            print(f"  ⚠ notification.py not found, skipping verification")
            return True

        try:
            # Test with empty JSON input
            result = subprocess.run(
                [self.python_path, str(notification_hook)],
                input='{}',
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                print(f"  ✓ {Colors.GREEN}Hook verification passed!{Colors.END}")
                return True
            else:
                print(f"  {Colors.YELLOW}⚠ Hook verification completed with warnings{Colors.END}")
                if result.stderr:
                    print(f"  {Colors.YELLOW}stderr: {result.stderr[:200]}{Colors.END}")
                return True  # Don't fail setup for hook warnings

        except subprocess.TimeoutExpired:
            print(f"  {Colors.YELLOW}⚠ Hook verification timed out{Colors.END}")
            return True  # Don't fail setup for timeout
        except Exception as e:
            print(f"  {Colors.YELLOW}⚠ Hook verification error: {e}{Colors.END}")
            return True  # Don't fail setup for verification errors

    def validate_setup(self) -> bool:
        """Validate that all necessary files exist and are correct"""
        print(f"\n{Colors.BOLD}Validating setup...{Colors.END}")

        checks = [
            (self.claude_dir / 'settings.json', 'settings.json'),
            (self.claude_dir / 'hooks' / 'config' / '__claude_hook__allowed_root_files', 'allowed_root_files config'),
            (self.claude_dir / 'hooks' / 'config' / '__claude_hook__valid_test_paths', 'valid_test_paths config'),
        ]

        all_valid = True
        for path, name in checks:
            if path.exists():
                print(f"  ✓ {Colors.GREEN}{name}{Colors.END}")
            else:
                print(f"  ✗ {Colors.RED}{name} missing{Colors.END}")
                all_valid = False

        # Validate settings.json has correct Python path
        settings_path = self.claude_dir / 'settings.json'
        if settings_path.exists():
            with open(settings_path, 'r') as f:
                settings = json.load(f)

            # Check if Python path is in the settings
            settings_str = json.dumps(settings)
            if self.python_path in settings_str:
                print(f"  ✓ {Colors.GREEN}Python path configured correctly{Colors.END}")
            else:
                print(f"  ✗ {Colors.RED}Python path not found in settings.json{Colors.END}")
                all_valid = False

        return all_valid

    def print_success(self):
        """Print success message and next steps"""
        print(f"\n{Colors.BOLD}{Colors.GREEN}╔════════════════════════════════════════════╗{Colors.END}")
        print(f"{Colors.BOLD}{Colors.GREEN}║          Setup Complete! 🎉                ║{Colors.END}")
        print(f"{Colors.BOLD}{Colors.GREEN}╚════════════════════════════════════════════╝{Colors.END}\n")

        print(f"{Colors.BOLD}Next steps:{Colors.END}")
        print(f"  1. Review generated settings.json")

        if self.use_venv:
            print(f"  2. {Colors.GREEN}✓{Colors.END} Virtual environment created at: .claude/.venv")
            print(f"     {Colors.GREEN}✓{Colors.END} Dependencies installed: python-dotenv, psutil, pyyaml")
        else:
            print(f"  2. {Colors.YELLOW}⚠{Colors.END} Using system Python - ensure these packages are installed:")
            print(f"     {Colors.YELLOW}pip install python-dotenv psutil pyyaml{Colors.END}")

        print(f"  3. Customize config files if needed:")
        print(f"     - .claude/hooks/config/__claude_hook__allowed_root_files")
        print(f"     - .claude/hooks/config/__claude_hook__valid_test_paths")
        print(f"  4. Review rules files in project root")
        print(f"  5. {Colors.BLUE}[IMPORTANT]{Colors.END} Configure MCP servers:")
        print(f"     - Edit .mcp.json with your API tokens")
        print(f"     - Update agenthub_http Authorization Bearer token")
        print(f"  6. {Colors.BLUE}[RECOMMENDED]{Colors.END} Generate project-specific CLAUDE.local.md:")
        print(f"     Run: {Colors.GREEN}/generate-local-rules{Colors.END} or {Colors.GREEN}/init-local{Colors.END}")
        print(f"  7. Start using Claude Code / Codex!\n")

        if self.use_venv:
            print(f"{Colors.BLUE}ℹ  Hook verification: Test manually with:{Colors.END}")
            print(f"   {Colors.GREEN}echo '{{}}' | {self.python_path} .claude/hooks/notification.py{Colors.END}\n")

        print(f"{Colors.YELLOW}To reconfigure, run this script again anytime.{Colors.END}\n")

    def run(self):
        """Main setup workflow"""
        try:
            self.print_header()

            # Step 1: Python path
            self.python_path = self.prompt_python_path()

            # Step 2: AI tool choice
            self.ai_tool_choice = self.prompt_ai_tool_choice()

            # Step 3: Token optimization strategy
            self.token_strategy = self.prompt_token_strategy()

            # Step 4: Virtual environment choice
            self.use_venv = self.prompt_venv_usage()

            # Step 5: Create virtual environment (if chosen)
            if self.use_venv:
                if not self.create_virtual_environment():
                    print(f"\n{Colors.YELLOW}⚠ Failed to create virtual environment. Falling back to system Python.{Colors.END}")
                    self.use_venv = False

            # Step 6: Install dependencies
            if not self.install_hook_dependencies():
                print(f"\n{Colors.YELLOW}⚠ Failed to install dependencies. Please install manually.{Colors.END}")

            # Step 7: Generate settings.json
            if not self.generate_settings_json():
                print(f"\n{Colors.RED}Setup failed during settings.json generation.{Colors.END}")
                return 1

            # Step 8: Setup config files
            self.setup_config_files()

            # Step 9: Deploy rules files
            self.deploy_rules_files()

            # Step 10: Deploy .env.claude
            self.deploy_env_claude()

            # Step 11: Deploy .mcp.json
            self.deploy_mcp_config()

            # Step 12: Verify hooks
            self.verify_hooks()

            # Step 13: Validate
            if not self.validate_setup():
                print(f"\n{Colors.YELLOW}⚠ Setup completed with warnings. Please review.{Colors.END}")
                return 1

            # Step 14: Success!
            self.print_success()
            return 0

        except KeyboardInterrupt:
            print(f"\n\n{Colors.YELLOW}Setup cancelled by user.{Colors.END}\n")
            return 130
        except Exception as e:
            print(f"\n{Colors.RED}✗ Setup failed with error: {e}{Colors.END}\n")
            import traceback
            traceback.print_exc()
            return 1


def main():
    """Entry point"""
    setup = ClaudeSetup()
    sys.exit(setup.run())


if __name__ == '__main__':
    main()
