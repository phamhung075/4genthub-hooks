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
        print(f"  {Colors.BLUE}[2]{Colors.END} Max Performance (Token burn - maximum context, best for learning)")
        print(f"\n  {Colors.YELLOW}Recommendation:{Colors.END} Use Economic for most projects")

        while True:
            choice = input(f"\nChoice [1-2, default: 1]: ").strip() or '1'

            if choice == '1':
                return 'economic'
            elif choice == '2':
                return 'performance'
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
        print(f"  2. Customize config files if needed:")
        print(f"     - .claude/hooks/config/__claude_hook__allowed_root_files")
        print(f"     - .claude/hooks/config/__claude_hook__valid_test_paths")
        print(f"  3. Review rules files in project root")
        print(f"  4. {Colors.BLUE}[RECOMMENDED]{Colors.END} Generate project-specific CLAUDE.local.md:")
        print(f"     Run: {Colors.GREEN}/generate-local-rules{Colors.END} or {Colors.GREEN}/init-local{Colors.END}")
        print(f"  5. Start using Claude Code / Codex!\n")

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

            # Step 4: Generate settings.json
            if not self.generate_settings_json():
                print(f"\n{Colors.RED}Setup failed during settings.json generation.{Colors.END}")
                return 1

            # Step 5: Setup config files
            self.setup_config_files()

            # Step 6: Deploy rules files
            self.deploy_rules_files()

            # Step 6.5: Deploy .env.claude
            self.deploy_env_claude()

            # Step 7: Validate
            if not self.validate_setup():
                print(f"\n{Colors.YELLOW}⚠ Setup completed with warnings. Please review.{Colors.END}")
                return 1

            # Step 8: Success!
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
