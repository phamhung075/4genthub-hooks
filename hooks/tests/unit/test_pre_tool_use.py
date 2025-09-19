"""
Unit tests for pre_tool_use.py hook.

Tests the pre-tool validation hook functionality including file system protection,
documentation enforcement, environment file protection, and permission checking.
"""

import pytest
import json
import os
import sys
from unittest.mock import Mock, patch, MagicMock, mock_open
from pathlib import Path

# Add hooks directory to Python path
hooks_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(hooks_dir))

from pre_tool_use import (
    FileLogger,
    RootFileValidator,
    EnvFileValidator,
    CommandValidator,
    DocumentationValidator,
    PermissionValidator,
    ContextProcessor,
    HintProcessor,
    MCPProcessor,
    ComponentFactory,
    PreToolUseHook,
    main
)


class TestFileLogger:
    """Test file logging functionality for pre-tool use."""

    def test_initialization(self, temp_directory):
        """Test FileLogger initializes correctly."""
        log_file = temp_directory / 'pre_tool_use.json'
        logger = FileLogger(temp_directory, 'pre_tool_use')

        assert logger.log_path == log_file

    def test_log_writes_validation_message(self, temp_directory):
        """Test logging writes validation messages."""
        log_file = temp_directory / 'pre_tool_use.json'
        logger = FileLogger(temp_directory, 'pre_tool_use')

        test_message = "Validating tool: Edit"
        logger.log("INFO", test_message)

        assert log_file.exists()
        with open(log_file, 'r') as f:
            log_data = json.load(f)
        assert any(test_message in entry.get('message', '') for entry in log_data)


class TestRootFileValidator:
    """Test root file validation functionality."""

    def setup_method(self):
        """Setup for root file validator tests."""
        self.validator = RootFileValidator()

    @patch('pathlib.Path.read_text')
    def test_validate_allowed_root_file(self, mock_read_text):
        """Test validation allows permitted root files."""
        mock_read_text.return_value = "README.md\nCHANGELOG.md\n"

        tool_params = {
            'file_path': 'README.md',
            'content': 'New readme content'
        }

        is_valid, error_msg = self.validator.validate('Write', tool_params)

        assert is_valid is True
        assert error_msg is None

    @patch('pathlib.Path.read_text')
    def test_validate_forbidden_root_file(self, mock_read_text):
        """Test validation blocks forbidden root files."""
        mock_read_text.return_value = "README.md\nCHANGELOG.md\n"

        # Use relative path or current directory path
        tool_params = {
            'file_path': 'forbidden.txt',  # This will be in root
            'content': 'Forbidden content'
        }

        is_valid, error_msg = self.validator.validate('Write', tool_params)

        assert is_valid is False
        assert error_msg is not None
        assert "not allowed" in error_msg.lower()

    @patch('pathlib.Path.read_text')
    def test_validate_non_root_file(self, mock_read_text):
        """Test validation allows non-root files."""
        tool_params = {
            'file_path': 'src/main.py',
            'content': 'Python code'
        }

        is_valid, error_msg = self.validator.validate('Write', tool_params)

        assert is_valid is True
        assert error_msg is None  # No error when valid
        # Old expectation: assert error_msg == "Non-root file allowed"

    @patch('pathlib.Path.exists')
    def test_validate_missing_config_file(self, mock_exists):
        """Test validation when allowed_root_files is missing."""
        mock_exists.return_value = False

        tool_params = {
            'file_path': 'test.txt',
            'content': 'Test content'
        }

        is_valid, error_msg = self.validator.validate('Write', tool_params)

        assert is_valid is False
        assert "not allowed" in error_msg  # Changed message

    def test_validate_non_file_tool(self):
        """Test validation skips non-file tools."""
        tool_params = {'command': 'ls -la'}

        is_valid, error_msg = self.validator.validate('Bash', tool_params)

        assert is_valid is True
        assert error_msg is None  # No error when valid
        # Old expectation: assert error_msg == "Non-file operation allowed"


class TestEnvFileValidator:
    """Test environment file validation functionality."""

    def setup_method(self):
        """Setup for env file validator tests."""
        self.validator = EnvFileValidator()

    def test_validate_env_file_blocked(self):
        """Test validation blocks .env file access."""
        tool_params = {
            'file_path': '.env',
        }

        is_valid, error_msg = self.validator.validate('Read', tool_params)

        assert is_valid is False
        assert "BLOCKED" in error_msg
        assert ".env" in error_msg

    def test_validate_env_local_file_blocked(self):
        """Test validation blocks .env.local file access."""
        tool_params = {
            'file_path': '.env.local',
        }

        is_valid, error_msg = self.validator.validate('Read', tool_params)

        assert is_valid is False
        assert "BLOCKED" in error_msg
        assert ".env" in error_msg

    def test_validate_env_production_file_blocked(self):
        """Test validation blocks .env.production file access."""
        tool_params = {
            'file_path': '.env.production',
        }

        is_valid, error_msg = self.validator.validate('Read', tool_params)

        assert is_valid is False
        assert "BLOCKED" in error_msg
        assert ".env" in error_msg

    def test_validate_non_env_file_allowed(self):
        """Test validation allows non-environment files."""
        tool_params = {
            'file_path': 'config.json',
        }

        is_valid, error_msg = self.validator.validate('Read', tool_params)

        assert is_valid is True
        assert error_msg is None  # No error when valid
        # Old expectation: assert error_msg == "Non-environment file allowed"

    def test_validate_env_in_filename_allowed(self):
        """Test validation allows files with 'env' in name but not .env files."""
        tool_params = {
            'file_path': 'environment_config.py',
        }

        is_valid, error_msg = self.validator.validate('Read', tool_params)

        assert is_valid is True
        assert error_msg is None  # No error when valid
        # Old expectation: assert error_msg == "Non-environment file allowed"


class TestCommandValidator:
    """Test command validation functionality."""

    def setup_method(self):
        """Setup for command validator tests."""
        self.validator = CommandValidator()

    def test_validate_dangerous_rm_command(self):
        """Test validation blocks dangerous rm commands."""
        tool_params = {
            'command': 'rm -rf /'
        }

        is_valid, error_msg = self.validator.validate('Bash', tool_params)

        assert is_valid is False
        assert "BLOCKED" in error_msg  # Message changed to include BLOCKED

    def test_validate_dangerous_dd_command(self):
        """Test validation blocks dangerous dd commands."""
        tool_params = {
            'command': 'dd if=/dev/zero of=/dev/sda'
        }

        is_valid, error_msg = self.validator.validate('Bash', tool_params)

        assert is_valid is False
        assert error_msg is not None
        assert "dangerous" in error_msg.lower() or "blocked" in error_msg.lower()

    def test_validate_format_command(self):
        """Test validation blocks format commands."""
        tool_params = {
            'command': 'mkfs.ext4 /dev/sdb1'
        }

        is_valid, error_msg = self.validator.validate('Bash', tool_params)

        assert is_valid is False
        assert error_msg is not None
        assert "dangerous" in error_msg.lower() or "blocked" in error_msg.lower()

    def test_validate_safe_command(self):
        """Test validation allows safe commands."""
        tool_params = {
            'command': 'ls -la'
        }

        is_valid, error_msg = self.validator.validate('Bash', tool_params)

        assert is_valid is True
        assert error_msg is None  # No error when valid
        # Old expectation: assert error_msg == "Safe command allowed"

    def test_validate_git_command(self):
        """Test validation allows git commands."""
        tool_params = {
            'command': 'git status'
        }

        is_valid, error_msg = self.validator.validate('Bash', tool_params)

        assert is_valid is True
        assert error_msg is None  # No error when valid
        # Old expectation: assert error_msg == "Safe command allowed"

    def test_validate_non_bash_tool(self):
        """Test validation skips non-bash tools."""
        tool_params = {
            'file_path': 'test.py'
        }

        is_valid, error_msg = self.validator.validate('Read', tool_params)

        assert is_valid is True
        assert error_msg is None  # No error when valid
        # Old expectation: assert error_msg == "Non-command operation allowed"


class TestDocumentationValidator:
    """Test documentation validation functionality."""

    def setup_method(self):
        """Setup for documentation validator tests."""
        self.validator = DocumentationValidator()

    @patch('utils.session_tracker.is_file_in_session')
    @patch('utils.docs_indexer.check_documentation_requirement')
    def test_validate_with_existing_documentation(self, mock_check_doc, mock_session):
        """Test validation with existing documentation."""
        mock_check_doc.return_value = True  # Documentation required
        mock_session.return_value = False  # File not in session

        tool_params = {
            'file_path': 'src/important_module.py'
        }

        is_valid, error_msg = self.validator.validate('Edit', tool_params)

        # Should block on first access in new session
        assert is_valid is False
        # The actual error message comes from config_factory.get_warning_message
        assert error_msg is not None  # Some warning message

    @patch('utils.session_tracker.is_file_in_session')
    @patch('utils.docs_indexer.check_documentation_requirement')
    def test_validate_with_recent_session_activity(self, mock_check_doc, mock_session):
        """Test validation allows continued work in same session."""
        mock_check_doc.return_value = True  # Documentation required
        mock_session.return_value = True  # File already in session

        tool_params = {
            'file_path': 'src/important_module.py'
        }

        is_valid, error_msg = self.validator.validate('Edit', tool_params)

        assert is_valid is True
        assert error_msg is None  # No error when valid
        # Old expectation: assert error_msg == "Session continuation allowed"

    @patch('utils.docs_indexer.check_documentation_requirement')
    def test_validate_without_documentation(self, mock_check_doc):
        """Test validation allows files without documentation."""
        mock_check_doc.return_value = False  # No documentation required

        tool_params = {
            'file_path': 'src/new_module.py'
        }

        is_valid, error_msg = self.validator.validate('Edit', tool_params)

        assert is_valid is True
        assert error_msg is None  # No error when valid
        # Old expectation: assert error_msg == "No documentation enforcement"

    def test_validate_non_file_tool(self):
        """Test validation skips non-file tools."""
        tool_params = {
            'command': 'pytest'
        }

        is_valid, error_msg = self.validator.validate('Bash', tool_params)

        assert is_valid is True
        assert error_msg is None  # No error when valid
        # Old expectation: assert error_msg == "Non-file operation allowed"


class TestPermissionValidator:
    """Test permission validation functionality."""

    def setup_method(self):
        """Setup for permission validator tests."""
        self.validator = PermissionValidator()

    @patch('utils.role_enforcer.check_tool_permission')
    def test_validate_with_permission(self, mock_check_permission):
        """Test validation with proper tool permission."""
        mock_check_permission.return_value = (True, None)

        tool_params = {
            'file_path': 'src/test.py'
        }

        is_valid, error_msg = self.validator.validate('Edit', tool_params)

        assert is_valid is True
        assert error_msg is None  # No error when valid
        # Old expectation: assert error_msg == "Tool permission granted"

    @patch('utils.role_enforcer.check_tool_permission')
    def test_validate_without_permission(self, mock_check_permission):
        """Test validation without proper tool permission."""
        mock_check_permission.return_value = (False, "Tool not allowed for current agent")

        tool_params = {
            'file_path': 'src/test.py'
        }

        is_valid, error_msg = self.validator.validate('Edit', tool_params)

        assert is_valid is False
        assert error_msg is not None

    @patch('utils.role_enforcer.check_tool_permission')
    def test_validate_permission_check_failure(self, mock_check_permission):
        """Test validation when permission check fails."""
        mock_check_permission.side_effect = Exception("Permission system error")

        tool_params = {
            'file_path': 'src/test.py'
        }

        is_valid, error_msg = self.validator.validate('Edit', tool_params)

        assert is_valid is True  # Fail open for safety
        assert error_msg is None  # No error when valid
        # Old expectation: assert error_msg == "Permission check failed, allowing operation"


class TestContextProcessor:
    """Test context processing functionality."""

    def setup_method(self):
        """Setup for context processor tests."""
        self.processor = ContextProcessor()

    @patch('utils.context_injector.inject_context_sync')
    def test_process_successful_context_injection(self, mock_inject):
        """Test successful context injection."""
        mock_inject.return_value = "Injected context data"

        tool_name = 'Edit'
        tool_params = {'file_path': '/test.py'}

        result_output = self.processor.process(tool_name, tool_params)

        # ContextProcessor returns Optional[str] with context
        assert result_output is not None
        assert isinstance(result_output, str)
        assert "injected context" in result_output.lower()
        mock_inject.assert_called_once_with(tool_name, tool_params)

    @patch('utils.context_injector.inject_context_sync')
    def test_process_failed_context_injection(self, mock_inject):
        """Test failed context injection."""
        mock_inject.return_value = False

        tool_name = 'Edit'
        tool_params = {'file_path': '/test.py'}

        result_output = self.processor.process(tool_name, tool_params)

        # ContextProcessor returns None if no context available
        assert result_output is None
        mock_inject.assert_called_once_with(tool_name, tool_params)

    @patch('utils.context_injector.inject_context_sync')
    def test_process_context_injection_exception(self, mock_inject):
        """Test context injection with exception."""
        mock_inject.side_effect = Exception("Context injection failed")

        tool_name = 'Edit'
        tool_params = {'file_path': '/test.py'}

        result_output = self.processor.process(tool_name, tool_params)

        # ContextProcessor returns None on exception
        assert result_output is None


class TestHintProcessor:
    """Test hint processing functionality."""

    def setup_method(self):
        """Setup for hint processor tests."""
        # HintProcessor now requires a logger parameter
        self.mock_logger = Mock()
        self.processor = HintProcessor(self.mock_logger)

    @patch('utils.unified_hint_system.get_hint_system')
    def test_process_successful_hint_generation(self, mock_get_system):
        """Test successful hint generation."""
        # Mock the hint system and its methods
        mock_system = Mock()
        mock_system.hint_bridge.retrieve_hints.return_value = None
        mock_system.generate_pre_action_hints.return_value = [
            "Remember to test your changes",
            "Consider code review guidelines"
        ]
        mock_get_system.return_value = mock_system

        tool_name = 'Edit'
        tool_params = {'file_path': '/test.py'}

        result_output = self.processor.process(tool_name, tool_params)

        # HintProcessor returns Optional[str], not dict
        if result_output is not None:
            assert isinstance(result_output, str)
        # Verify hint system was queried (called twice: once for retrieve_hints, once for generate_pre_action_hints)
        assert mock_get_system.call_count == 2

    @patch('utils.unified_hint_system.get_hint_system')
    def test_process_no_hints_generated(self, mock_get_system):
        """Test when no hints are generated."""
        mock_system = Mock()
        mock_system.hint_bridge.retrieve_hints.return_value = None
        mock_system.generate_pre_action_hints.return_value = []
        mock_get_system.return_value = mock_system

        tool_data = {
            'tool_name': 'Bash',
            'tool_params': {'command': 'ls'}
        }

        result_output = self.processor.process(
            tool_data['tool_name'],
            tool_data['tool_params']
        )

        # When no hints, may return None or empty
        if result_output is not None:
            assert isinstance(result_output, str)

    @patch('utils.unified_hint_system.get_hint_system')
    def test_process_hint_generation_exception(self, mock_get_system):
        """Test hint generation with exception."""
        mock_get_system.side_effect = Exception("Hint generation failed")

        tool_name = 'Edit'
        tool_params = {'file_path': '/test.py'}

        result_output = self.processor.process(tool_name, tool_params)

        # When hint generation fails, HintProcessor returns None (no hints available)
        assert result_output is None


class TestMCPProcessor:
    """Test MCP processing functionality."""

    def setup_method(self):
        """Setup for MCP processor tests."""
        self.processor = MCPProcessor()

    @patch('utils.mcp_task_interceptor.get_mcp_interceptor')
    def test_process_successful_mcp_notification(self, mock_get_interceptor):
        """Test successful MCP notification."""
        mock_interceptor = Mock()
        mock_interceptor.intercept_pre_tool.return_value = "MCP notification sent"
        mock_get_interceptor.return_value = mock_interceptor

        tool_name = 'Edit'
        tool_params = {'file_path': '/test.py'}

        result_output = self.processor.process(tool_name, tool_params)

        # MCPProcessor returns Optional[str]
        assert result_output == "MCP notification sent"
        mock_interceptor.intercept_pre_tool.assert_called_once_with(tool_name, tool_params)

    @patch('utils.mcp_task_interceptor.get_mcp_interceptor')
    def test_process_failed_mcp_notification(self, mock_get_interceptor):
        """Test failed MCP notification."""
        mock_interceptor = Mock()
        mock_interceptor.intercept_pre_tool.return_value = None
        mock_get_interceptor.return_value = mock_interceptor

        tool_name = 'Edit'
        tool_params = {'file_path': '/test.py'}

        result_output = self.processor.process(tool_name, tool_params)

        # MCPProcessor returns None when interceptor returns None
        assert result_output is None

    @patch('utils.mcp_task_interceptor.get_mcp_interceptor')
    def test_process_mcp_exception(self, mock_get_interceptor):
        """Test MCP processing with exception."""
        mock_get_interceptor.side_effect = Exception("MCP interceptor error")

        tool_name = 'Edit'
        tool_params = {'file_path': '/test.py'}

        result_output = self.processor.process(tool_name, tool_params)

        # MCPProcessor returns None on exception (caught and suppressed)
        assert result_output is None


class TestComponentFactory:
    """Test component factory functionality."""

    def test_create_validators(self):
        """Test factory creates all validators."""
        logger = Mock()
        factory = ComponentFactory()  # No arguments needed
        validators = factory.create_validators()

        assert len(validators) == 5  # Root, Env, Command, Doc, Permission
        assert any(isinstance(v, RootFileValidator) for v in validators)
        assert any(isinstance(v, EnvFileValidator) for v in validators)
        assert any(isinstance(v, CommandValidator) for v in validators)
        assert any(isinstance(v, DocumentationValidator) for v in validators)
        assert any(isinstance(v, PermissionValidator) for v in validators)

    def test_create_processors(self):
        """Test factory creates all processors."""
        logger = Mock()
        factory = ComponentFactory()  # No arguments needed
        processors = factory.create_processors(logger)

        assert len(processors) == 3  # Context, Hint, MCP
        assert any(isinstance(p, ContextProcessor) for p in processors)
        assert any(isinstance(p, HintProcessor) for p in processors)
        assert any(isinstance(p, MCPProcessor) for p in processors)


class TestPreToolUseHook:
    """Test main pre-tool use hook functionality."""

    def setup_method(self):
        """Setup for hook tests."""
        # PreToolUseHook now creates its own factory and logger internally
        self.hook = PreToolUseHook()
        # Mock the internal components if needed
        self.hook.logger = Mock()
        self.hook.factory = Mock()
        self.hook.validators = []
        self.hook.processors = []

    def test_run_with_validation_success(self):
        """Test hook execution with successful validation."""
        # Mock validators
        mock_validator = Mock()
        # Validators return Tuple[bool, Optional[str]]
        mock_validator.validate.return_value = (True, None)

        # Mock processors
        mock_processor = Mock()
        # Processors return Optional[str]
        mock_processor.process.return_value = None  # No output

        # Set validators and processors directly since they're created in __init__
        self.hook.validators = [mock_validator]
        self.hook.processors = [mock_processor]

        tool_data = {
            'tool_name': 'Edit',
            'tool_params': {'file_path': '/test.py'}
        }

        result = self.hook.execute(tool_data)

        # PreToolUseHook.execute() returns exit code: 0 for success, 1 for failure
        assert result == 0
        mock_validator.validate.assert_called_once()
        mock_processor.process.assert_called_once()

    def test_run_with_validation_failure(self):
        """Test hook execution with validation failure."""
        mock_validator = Mock()
        # Validators return Tuple[bool, Optional[str]]
        mock_validator.validate.return_value = (False, 'Validation failed')

        # Set validators directly since they're created in __init__
        self.hook.validators = [mock_validator]
        self.hook.processors = []

        tool_data = {
            'tool_name': 'Write',
            'tool_params': {'file_path': '/forbidden.txt'}
        }

        result = self.hook.execute(tool_data)

        # PreToolUseHook.execute() returns exit code: 1 for validation failure
        assert result == 1
        # Validation should be called
        mock_validator.validate.assert_called_once()

    def test_run_with_processor_failure(self):
        """Test hook execution with processor failure."""
        # Mock successful validation
        mock_validator = Mock()
        # Validators return Tuple[bool, Optional[str]]
        mock_validator.validate.return_value = (True, None)

        # Mock failing processor
        mock_processor = Mock()
        mock_processor.process.side_effect = Exception("Processor error")

        # Set validators and processors directly since they're created in __init__
        self.hook.validators = [mock_validator]
        self.hook.processors = [mock_processor]

        tool_data = {
            'tool_name': 'Edit',
            'tool_params': {'file_path': '/test.py'}
        }

        exit_code = self.hook.execute(tool_data)

        # Validation should succeed, processor errors are logged but don't fail the hook
        assert exit_code == 0
        self.hook.logger.log.assert_called()

    def test_run_with_missing_tool_data(self):
        """Test hook execution with missing tool data."""
        exit_code = self.hook.execute({})

        # Empty data is handled gracefully, returns success
        # (no validators fail for empty tool_name/tool_input)
        assert exit_code == 0

    def test_run_with_invalid_tool_data(self):
        """Test hook execution with invalid tool data."""
        exit_code = self.hook.execute({'invalid': 'data'})

        # Invalid data is handled gracefully, returns success
        # (no validators fail for missing tool_name/tool_input)
        assert exit_code == 0


class TestMainFunction:
    """Test main function integration."""

    @patch('pre_tool_use.PreToolUseHook')
    @patch('pre_tool_use.ComponentFactory')
    @patch('pre_tool_use.FileLogger')
    @patch('sys.stdin.read')
    @patch('sys.exit')
    def test_main_function_success(self, mock_exit, mock_stdin, mock_logger, mock_factory, mock_hook):
        """Test main function executes successfully."""
        # Mock stdin input
        tool_data = {
            'tool_name': 'Edit',
            'tool_params': {'file_path': '/test.py'}
        }
        mock_stdin.return_value = json.dumps(tool_data)

        # Mock hook response
        mock_hook_instance = Mock()
        mock_hook_instance.execute.return_value = 0  # Success
        mock_hook.return_value = mock_hook_instance

        main()

        # main() calls sys.exit(0) on success
        mock_exit.assert_called_once_with(0)
        mock_hook_instance.execute.assert_called_once_with(tool_data)

    @patch('pre_tool_use.PreToolUseHook')
    @patch('pre_tool_use.ComponentFactory')
    @patch('pre_tool_use.FileLogger')
    @patch('sys.stdin.read')
    @patch('sys.exit')
    def test_main_function_with_invalid_json(self, mock_exit, mock_stdin, mock_logger, mock_factory, mock_hook):
        """Test main function with invalid JSON input."""
        mock_stdin.return_value = "invalid json"

        main()

        # main() gracefully handles JSON parse errors with exit(0)
        mock_exit.assert_called_once_with(0)

    @patch('pre_tool_use.PreToolUseHook')
    @patch('pre_tool_use.ComponentFactory')
    @patch('pre_tool_use.FileLogger')
    @patch('sys.stdin.read')
    @patch('sys.exit')
    def test_main_function_with_exception(self, mock_exit, mock_stdin, mock_logger, mock_factory, mock_hook):
        """Test main function handles exceptions."""
        mock_stdin.return_value = '{"tool_name": "Edit"}'
        mock_hook.side_effect = Exception("Hook initialization failed")

        main()

        # main() gracefully handles all exceptions with exit(0)
        mock_exit.assert_called_once_with(0)


# Integration tests
class TestPreToolUseIntegration:
    """Integration tests for pre-tool use hook."""

    @pytest.mark.integration
    @patch('sys.exit')
    @patch('pathlib.Path.read_text')
    @patch('utils.role_enforcer.check_tool_permission')
    def test_full_validation_flow(self, mock_permission, mock_read_text, mock_exit):
        """Test complete validation flow with mocked dependencies."""
        # Mock configuration
        mock_read_text.return_value = "README.md\nCHANGELOG.md\n"
        mock_permission.return_value = (True, None)  # Tuple return

        tool_data = {
            'tool_name': 'Edit',
            'tool_input': {  # Use tool_input instead of tool_params
                'file_path': 'src/main.py',
                'old_string': 'old code',
                'new_string': 'new code'
            }
        }

        # Run the hook
        with patch('sys.stdin.read', return_value=json.dumps(tool_data)):
            main()

        # main() should exit with 0 for successful validation
        mock_exit.assert_called_once_with(0)

    @pytest.mark.integration
    @patch('sys.exit')
    def test_pre_tool_use_in_test_mode(self, mock_exit, mock_env_vars):
        """Test pre-tool use in test mode."""
        tool_data = {
            'tool_name': 'Read',
            'tool_input': {'file_path': '/test/file.py'}  # Use tool_input
        }

        with patch('sys.stdin.read', return_value=json.dumps(tool_data)):
            main()

        # Should work in test mode and exit with success
        mock_exit.assert_called_once_with(0)


# Fixture-based tests
@pytest.mark.hooks
class TestPreToolUseWithFixtures:
    """Test pre-tool use using shared fixtures."""

    def test_validation_chain(self):
        """Test validation chain execution."""
        logger = Mock()
        factory = ComponentFactory()  # No arguments needed

        validators = factory.create_validators()
        assert len(validators) > 0

        # Each validator should have a validate method
        for validator in validators:
            assert hasattr(validator, 'validate')
            assert callable(validator.validate)

    def test_processor_chain(self):
        """Test processor chain execution."""
        logger = Mock()
        factory = ComponentFactory()  # No arguments needed

        processors = factory.create_processors(logger)
        assert len(processors) > 0

        # Each processor should have a process method
        for processor in processors:
            assert hasattr(processor, 'process')
            assert callable(processor.process)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])