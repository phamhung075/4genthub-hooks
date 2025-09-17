#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# ///

"""
Refactored Pre-tool use hook with factory pattern and clean architecture.

This hook runs before tool execution and provides:
1. File system protection and validation
2. Documentation enforcement
3. Environment file access protection
4. Dangerous command prevention
5. Tool permission checking
6. Context injection and hint display

Refactored with:
- Factory pattern for component creation
- Single Responsibility Principle
- Dependency injection
- Clean error handling
- Centralized configuration
"""

import json
import sys
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from abc import ABC, abstractmethod

# Add hooks directory to path
sys.path.insert(0, str(Path(__file__).parent))


# ============================================================================
# Abstract Base Classes
# ============================================================================

class Validator(ABC):
    """Base validator interface."""

    @abstractmethod
    def validate(self, tool_name: str, tool_input: Dict) -> Tuple[bool, Optional[str]]:
        """
        Validate the tool call.

        Returns:
            Tuple of (is_valid, error_message)
        """
        pass


class Processor(ABC):
    """Base processor interface."""

    @abstractmethod
    def process(self, tool_name: str, tool_input: Dict) -> Optional[str]:
        """
        Process the tool call and return any output.

        Returns:
            Optional output string
        """
        pass


class Logger(ABC):
    """Abstract logger interface."""

    @abstractmethod
    def log(self, level: str, message: str, data: Optional[Dict] = None):
        """Log a message with optional data."""
        pass


# ============================================================================
# Component Implementations
# ============================================================================

class FileLogger(Logger):
    """File-based logger implementation."""

    def __init__(self, log_dir: Path, log_name: str):
        self.log_dir = log_dir
        self.log_name = log_name
        self.log_path = log_dir / f"{log_name}.json"
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def log(self, level: str, message: str, data: Optional[Dict] = None):
        """Log to JSON file."""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message,
            'data': data
        }

        # Load existing log
        log_data = []
        if self.log_path.exists():
            try:
                with open(self.log_path, 'r') as f:
                    log_data = json.load(f)
            except:
                pass

        # Append and save
        log_data.append(entry)

        # Keep only last 100 entries
        if len(log_data) > 100:
            log_data = log_data[-100:]

        with open(self.log_path, 'w') as f:
            json.dump(log_data, f, indent=2)


class RootFileValidator(Validator):
    """Validates file creation in project root."""

    def __init__(self):
        self.allowed_files = self._load_allowed_files()

    def _load_allowed_files(self) -> List[str]:
        """Load allowed root files from configuration."""
        project_root = Path.cwd()
        config_path = project_root / '.claude' / 'hooks' / 'config' / '__claude_hook__allowed_root_files'

        default_allowed = [
            'README.md', 'CHANGELOG.md', 'TEST-CHANGELOG.md',
            'CLAUDE.md', 'CLAUDE.local.md', '.gitignore',
            'package.json', 'package-lock.json', 'requirements.txt',
            'pyproject.toml', 'poetry.lock', 'Pipfile', 'Pipfile.lock',
            'docker-compose.yml', 'Dockerfile', '.dockerignore',
            'Makefile', 'setup.py', 'setup.cfg'
        ]

        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    lines = [line.strip() for line in f.readlines()
                            if line.strip() and not line.startswith('#')]
                return lines if lines else default_allowed
            except:
                return default_allowed

        return default_allowed

    def validate(self, tool_name: str, tool_input: Dict) -> Tuple[bool, Optional[str]]:
        """Validate file creation in root directory."""
        if tool_name not in ['Write', 'Edit', 'MultiEdit', 'NotebookEdit']:
            return True, None

        file_path = tool_input.get('file_path') or tool_input.get('notebook_path', '')
        if not file_path:
            return True, None

        path_obj = Path(file_path)
        project_root = Path.cwd()

        # Check if trying to create file in root
        try:
            relative_path = path_obj.resolve().relative_to(project_root.resolve())
            if len(relative_path.parts) == 1:  # File in root directory
                filename = relative_path.parts[0]
                if filename not in self.allowed_files:
                    from utils.config_factory import get_error_message
                    return False, get_error_message('root_file_blocked',
                                                  filename=filename,
                                                  allowed_files=', '.join(self.allowed_files))
        except ValueError:
            # Path is outside project root
            pass

        return True, None


class EnvFileValidator(Validator):
    """Validates environment file access."""

    # List of allowed .env example file patterns (exact match only)
    ALLOWED_ENV_EXAMPLES = [
        '.env.sample',
        '.env.example',
        '.env.template',
        '.env.default',
        '.env.dist'
    ]

    def validate(self, tool_name: str, tool_input: Dict) -> Tuple[bool, Optional[str]]:
        """Validate environment file access."""
        if tool_name not in ['Read', 'Write', 'Edit', 'MultiEdit']:
            return True, None

        file_path = tool_input.get('file_path', '')
        if not file_path:
            return True, None

        # Check for .env files
        path_obj = Path(file_path)
        filename = path_obj.name.lower()

        # Block ALL .env* files (including .env, .env.dev, .env.prod, .env.local, etc.)
        if filename.startswith('.env'):
            # Only allow specific example/sample/template files (exact match)
            if filename in [e.lower() for e in self.ALLOWED_ENV_EXAMPLES]:
                return True, None

            # Block all other .env* files including .env.dev, .env.prod, .env.local, etc.
            from utils.config_factory import get_error_message
            return False, get_error_message('env_file_blocked', filename=path_obj.name)

        return True, None


class CommandValidator(Validator):
    """Validates dangerous commands."""

    def validate(self, tool_name: str, tool_input: Dict) -> Tuple[bool, Optional[str]]:
        """Validate bash commands for dangerous operations."""
        if tool_name != 'Bash':
            return True, None

        command = tool_input.get('command', '')
        if not command:
            return True, None

        # Check for dangerous rm commands
        if self._is_dangerous_rm(command):
            from utils.config_factory import get_error_message
            return False, get_error_message('dangerous_rm_blocked', command=command)

        return True, None

    def _is_dangerous_rm(self, command: str) -> bool:
        """Check if command is a dangerous rm operation."""
        dangerous_patterns = [
            r'rm\s+-[rf]*r[rf]*\s+/',
            r'rm\s+-[rf]*f[rf]*\s+/',
            r'rm\s+/\w+',
            r'rm\s+~',
            r'rm\s+\*'
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, command):
                return True

        return False


class DocumentationValidator(Validator):
    """Validates documentation requirements."""

    def validate(self, tool_name: str, tool_input: Dict) -> Tuple[bool, Optional[str]]:
        """Validate documentation requirements."""
        try:
            from utils.docs_indexer import check_documentation_requirement
            from utils.session_tracker import is_file_in_session

            if not check_documentation_requirement or not is_file_in_session:
                return True, None

            file_path = self._extract_file_path(tool_name, tool_input)
            if not file_path:
                return True, None

            # Check documentation requirement
            if check_documentation_requirement(file_path):
                if not is_file_in_session(file_path):
                    from utils.config_factory import get_warning_message
                    return False, get_warning_message('documentation_required', filepath=file_path)

        except Exception:
            # If documentation system fails, don't block
            pass

        return True, None

    def _extract_file_path(self, tool_name: str, tool_input: Dict) -> Optional[str]:
        """Extract file path from tool input."""
        if tool_name in ['Write', 'Edit', 'MultiEdit']:
            return tool_input.get('file_path')
        elif tool_name == 'NotebookEdit':
            return tool_input.get('notebook_path')
        return None


class PermissionValidator(Validator):
    """Validates tool permissions based on agent role."""

    def validate(self, tool_name: str, tool_input: Dict) -> Tuple[bool, Optional[str]]:
        """Validate tool permissions."""
        try:
            from utils.role_enforcer import check_tool_permission

            if not check_tool_permission:
                return True, None

            is_allowed, error_msg = check_tool_permission(tool_name)
            if not is_allowed:
                return False, error_msg

        except Exception:
            # If role enforcer fails, don't block
            pass

        return True, None


class ContextProcessor(Processor):
    """Processes context injection."""

    def process(self, tool_name: str, tool_input: Dict) -> Optional[str]:
        """Inject context if available."""
        try:
            from utils.context_injector import inject_context_sync

            if inject_context_sync:
                context = inject_context_sync(tool_name, tool_input)
                if context and context.strip():
                    return context

        except Exception as e:
            # Log but don't fail
            pass

        return None


class HintProcessor(Processor):
    """Processes hint generation and display."""

    def __init__(self, logger: Logger):
        self.logger = logger

    def process(self, tool_name: str, tool_input: Dict) -> Optional[str]:
        """Generate and display hints."""
        hint_output = []

        try:
            # Get pending hints from post_tool_use
            from utils.unified_hint_system import get_hint_system

            hint_system = get_hint_system()
            pending_hints = hint_system.hint_bridge.retrieve_hints()
            if pending_hints:
                    hint_output.append("📋 Previous Action Insights:")
                    hint_output.append(pending_hints)
                    hint_output.append("")

        except Exception:
            pass

        try:
            # Generate new hints
            # Using unified hint system instead of separate analyzer
            hint_system = get_hint_system()
            new_hints = hint_system.generate_pre_action_hints(tool_name, tool_input)
            if new_hints:
                    hint_output.append("💡 Workflow Guidance:")
                    hint_output.extend(new_hints)

        except Exception:
            pass

        return "\n".join(hint_output) if hint_output else None


class MCPProcessor(Processor):
    """Processes MCP task interception."""

    def process(self, tool_name: str, tool_input: Dict) -> Optional[str]:
        """Process MCP task interception."""
        try:
            from utils.mcp_task_interceptor import get_mcp_interceptor

            if get_mcp_interceptor:
                interceptor = get_mcp_interceptor()
                if interceptor and hasattr(interceptor, 'intercept_pre_tool'):
                    return interceptor.intercept_pre_tool(tool_name, tool_input)

        except Exception:
            pass

        return None


# ============================================================================
# Component Factory
# ============================================================================

class ComponentFactory:
    """Factory for creating hook components."""

    @staticmethod
    def create_logger(log_dir: Path, log_name: str = 'pre_tool_use') -> Logger:
        """Create a logger instance."""
        return FileLogger(log_dir, log_name)

    @staticmethod
    def create_validators() -> List[Validator]:
        """Create all validators."""
        return [
            RootFileValidator(),
            EnvFileValidator(),
            CommandValidator(),
            DocumentationValidator(),
            PermissionValidator()
        ]

    @staticmethod
    def create_processors(logger: Logger) -> List[Processor]:
        """Create all processors."""
        return [
            ContextProcessor(),
            HintProcessor(logger),
            MCPProcessor()
        ]


# ============================================================================
# Main Hook Class
# ============================================================================

class PreToolUseHook:
    """Main pre-tool use hook with clean architecture."""

    def __init__(self):
        """Initialize the hook with all components."""
        # Get paths
        from utils.env_loader import get_ai_data_path

        self.log_dir = get_ai_data_path()

        # Create components using factory
        self.factory = ComponentFactory()
        self.logger = self.factory.create_logger(self.log_dir)

        # Initialize components
        self.validators: List[Validator] = self.factory.create_validators()
        self.processors: List[Processor] = self.factory.create_processors(self.logger)

    def execute(self, data: Dict[str, Any]) -> int:
        """Execute the pre-tool use hook."""
        tool_name = data.get('tool_name', '')
        tool_input = data.get('tool_input', {})

        # Log the execution
        self.logger.log('info', f'Pre-processing: {tool_name}')

        # Run all validators
        for validator in self.validators:
            try:
                is_valid, error_message = validator.validate(tool_name, tool_input)
                if not is_valid and error_message:
                    print(error_message, file=sys.stderr)
                    self.logger.log('warning', f'Validation failed: {validator.__class__.__name__}',
                                  {'tool': tool_name, 'error': error_message})
                    return 1
            except Exception as e:
                self.logger.log('error', f'Validator {validator.__class__.__name__} failed: {e}')

        # Check for MCP hint matrix hints FIRST (use factory)
        output_parts = []
        if tool_name.startswith('mcp__agenthub_http'):
            try:
                # Using unified hint system instead of matrix factory
                hint_system = get_hint_system()
                hints = hint_system.generate_pre_action_hints(tool_name, tool_input)
                if hints:
                    output_parts.append(hints)
            except Exception as e:
                self.logger.log('error', f'MCP hint matrix factory failed: {e}')

        # Run all processors for additional output
        for processor in self.processors:
            try:
                output = processor.process(tool_name, tool_input)
                if output and output.strip():
                    output_parts.append(output)
            except Exception as e:
                self.logger.log('error', f'Processor {processor.__class__.__name__} failed: {e}')

        # Output any processor results
        if output_parts:
            combined_output = "\n\n".join(output_parts)
            print(combined_output)

        self.logger.log('info', 'Pre-processing completed successfully')
        return 0


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Main entry point for the hook."""
    try:
        # Read JSON input from stdin
        input_data = json.load(sys.stdin)

        # Create and execute hook
        hook = PreToolUseHook()
        exit_code = hook.execute(input_data)

        sys.exit(exit_code)

    except json.JSONDecodeError:
        # Handle JSON decode errors gracefully
        sys.exit(0)
    except Exception as e:
        # Log error but exit cleanly
        try:
            from utils.env_loader import get_ai_data_path
            log_dir = get_ai_data_path()
            error_log = log_dir / 'pre_tool_use_errors.log'
            with open(error_log, 'a') as f:
                f.write(f"{datetime.now().isoformat()} - Fatal error: {e}\n")
        except:
            pass
        sys.exit(0)


if __name__ == '__main__':
    main()