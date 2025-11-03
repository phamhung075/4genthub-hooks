#!/usr/bin/env python3
"""
Configuration validator for Claude Code hooks.
Checks that all required configuration files exist before hook execution.
"""

import sys
from pathlib import Path
from typing import List, Tuple, Dict


class ConfigurationValidator:
    """Validates that all required configuration files exist."""

    def __init__(self):
        """Initialize validator with project root and required files."""
        # Find project root and hook directory
        self.project_root = self._find_project_root()
        self.claude_dir = self.project_root / '.claude'
        self.hook_dir = self.project_root / 'scripts' / 'claude-hooks'
        self.config_dir = self.hook_dir / 'config'

        # Define required files with their descriptions and fix instructions
        self.required_files = {
            self.config_dir / '__claude_hook__allowed_root_files': {
                'description': 'Root file protection configuration',
                'fix': (
                    "1. Copy the sample file:\n"
                    f"   cp {self.config_dir}/__claude_hook__allowed_root_files.sample \\\n"
                    f"      {self.config_dir}/__claude_hook__allowed_root_files\n"
                    "2. Edit the file to match your project's allowed root files"
                ),
                'purpose': 'Controls which files AI can create in project root'
            },
            self.config_dir / '__claude_hook__valid_test_paths': {
                'description': 'Test directory protection configuration',
                'fix': (
                    "1. Copy the sample file:\n"
                    f"   cp {self.config_dir}/__claude_hook__valid_test_paths.sample \\\n"
                    f"      {self.config_dir}/__claude_hook__valid_test_paths\n"
                    "2. Edit the file to match your project's test directory structure"
                ),
                'purpose': 'Defines where test files can be created'
            },
            self.claude_dir / 'settings.json': {
                'description': 'Claude Code hook settings',
                'fix': (
                    "1. Run the setup script:\n"
                    f"   python3 {self.hook_dir}/setup_hooks.py\n"
                    "2. This will create settings.json from the template"
                ),
                'purpose': 'Configures Claude Code hooks and permissions'
            },
            self.project_root / '.mcp.json': {
                'description': 'MCP API configuration',
                'fix': (
                    "1. Copy the sample file:\n"
                    f"   cp {self.claude_dir}/.mcp.json.sample {self.project_root}/.mcp.json\n"
                    "2. Edit the file and replace 'YOUR_API_TOKEN_HERE' with your actual token\n"
                    "3. Get your token at: https://www.4genthub.com/dashboard/api-tokens"
                ),
                'purpose': 'Connects Claude Code to 4genthub service'
            },
            self.project_root / 'CLAUDE.md': {
                'description': 'Project AI rules configuration',
                'fix': (
                    "1. Copy from template:\n"
                    f"   cp {self.claude_dir}/copy-to-root-project-rename-to:CLAUDE.md \\\n"
                    f"      {self.project_root}/CLAUDE.md\n"
                    "2. Edit to define your project's AI behavior"
                ),
                'purpose': 'Defines AI agent behavior for your project'
            }
        }

    def _find_project_root(self) -> Path:
        """Find the project root directory."""
        # Start from utils directory (scripts/claude-hooks/utils) and go up 3 levels
        # scripts/claude-hooks/utils/__file__ -> scripts/claude-hooks/utils -> scripts/claude-hooks -> scripts -> project_root
        current = Path(__file__).resolve().parent  # utils/
        hook_dir = current.parent  # scripts/claude-hooks/
        scripts_dir = hook_dir.parent  # scripts/
        project_root = scripts_dir.parent  # project root

        # Verify by checking for .claude directory
        if (project_root / '.claude').exists():
            return project_root

        # Fallback: traverse up to find .claude directory
        current = project_root
        while current.parent != current:
            if (current / '.claude').exists() and (current / '.claude').is_dir():
                return current
            current = current.parent

        # Last fallback
        return project_root

    def validate(self) -> Tuple[bool, List[Dict]]:
        """
        Validate all required configuration files.

        Returns:
            Tuple of (success: bool, errors: List[Dict])
            Each error dict contains: file, description, fix, purpose
        """
        errors = []

        for file_path, info in self.required_files.items():
            if not file_path.exists():
                errors.append({
                    'file': str(file_path),
                    'description': info['description'],
                    'fix': info['fix'],
                    'purpose': info['purpose']
                })

        return len(errors) == 0, errors

    def format_error_message(self, errors: List[Dict]) -> str:
        """
        Format validation errors into a clear error message.

        Args:
            errors: List of error dictionaries

        Returns:
            Formatted error message string
        """
        lines = [
            "",
            "=" * 70,
            "❌ CLAUDE CODE CONFIGURATION ERROR",
            "=" * 70,
            "",
            "The following required configuration files are missing:",
            ""
        ]

        for i, error in enumerate(errors, 1):
            lines.extend([
                f"{i}. {error['description']}",
                f"   📁 Missing file: {error['file']}",
                f"   📝 Purpose: {error['purpose']}",
                f"   ✅ To fix:",
                ""
            ])

            # Add fix instructions with proper indentation
            for line in error['fix'].split('\n'):
                if line.strip():
                    lines.append(f"      {line}")

            lines.append("")

        lines.extend([
            "=" * 70,
            "⚠️  CLAUDE CODE CANNOT START WITHOUT THESE FILES",
            "=" * 70,
            "",
            "Please follow the fix instructions above to create the missing files.",
            "For complete setup instructions, run:",
            f"   python3 {self.claude_dir}/hooks/setup_hooks.py",
            "",
            "Need help? Check the documentation:",
            f"   cat {self.claude_dir}/README.md",
            ""
        ])

        return '\n'.join(lines)

    def check_and_report(self) -> bool:
        """
        Check configuration and report errors if found.

        Returns:
            True if configuration is valid, False otherwise
        """
        is_valid, errors = self.validate()

        if not is_valid:
            error_message = self.format_error_message(errors)
            print(error_message, file=sys.stderr)

            # Also write to error log for debugging
            try:
                error_log = self.claude_dir / 'hooks' / 'data' / 'config_errors.log'
                error_log.parent.mkdir(parents=True, exist_ok=True)
                with open(error_log, 'w') as f:
                    f.write(error_message)
            except:
                pass

        return is_valid


def validate_configuration() -> bool:
    """
    Main validation function to be called by hooks.

    Returns:
        True if all required files exist, False otherwise
    """
    validator = ConfigurationValidator()
    return validator.check_and_report()


if __name__ == '__main__':
    # For testing: run directly to check configuration
    validator = ConfigurationValidator()
    is_valid, errors = validator.validate()

    if is_valid:
        print("✅ All required configuration files are present!")
    else:
        print(validator.format_error_message(errors), file=sys.stderr)
        sys.exit(1)