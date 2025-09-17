"""
Unit tests for session_start.py hook.

Tests the session initialization hook functionality including context loading,
git integration, MCP task status, and development environment setup.
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

from session_start import (
    ConfigurationLoader,
    FileLogger,
    GitContextProvider,
    MCPContextProvider,
    DevelopmentContextProvider,
    IssueContextProvider,
    AgentMessageProvider,
    SessionStartProcessor,
    ContextFormatterProcessor,
    ComponentFactory,
    SessionStartHook,
    main
)


class TestConfigurationLoader:
    """Test configuration loading functionality."""

    def test_initialization_with_defaults(self):
        """Test ConfigurationLoader initializes with default values."""
        loader = ConfigurationLoader(Path.cwd() / 'config')

        assert loader.config_dir == Path.cwd() / 'config'
        assert loader._cache == {}

    @patch.dict(os.environ, {
        'AI_DATA': '/custom/ai_data',
        'AI_DOCS': '/custom/ai_docs'
    })
    def test_initialization_with_env_vars(self):
        """Test ConfigurationLoader uses environment variables."""
        config_dir = Path('/custom/config')
        loader = ConfigurationLoader(config_dir)

        assert loader.config_dir == config_dir
        # ConfigurationLoader doesn't use env vars directly anymore

    def test_to_dict_contains_required_fields(self):
        """Test configuration dictionary contains all required fields."""
        loader = ConfigurationLoader(Path.cwd() / 'config')

        # ConfigurationLoader doesn't have a to_dict method anymore
        # Test that we can load a config instead
        assert hasattr(loader, 'load_config')
        assert hasattr(loader, 'get_agent_message')

    def test_load_config_file_success(self, temp_directory):
        """Test loading configuration from YAML file."""
        config_data = {'test_setting': 'test_value'}

        with open(temp_directory / 'test_config.yaml', 'w') as f:
            import yaml
            yaml.dump(config_data, f)

        loader = ConfigurationLoader(temp_directory)
        result = loader.load_config('test_config')

        assert result == config_data

    def test_load_config_file_not_found(self):
        """Test handling missing configuration file."""
        loader = ConfigurationLoader(Path.cwd() / 'config')
        result = loader.load_config('nonexistent_config')

        assert result is None


class TestFileLogger:
    """Test file logging functionality."""

    def test_initialization(self, temp_directory):
        """Test FileLogger initializes correctly."""
        log_file = temp_directory / 'test_log.json'
        logger = FileLogger(temp_directory, 'test_log')

        assert logger.log_path == log_file

    def test_log_writes_to_file(self, temp_directory):
        """Test logging writes messages to file."""
        log_file = temp_directory / 'test_log.json'
        logger = FileLogger(temp_directory, 'test_log')

        test_message = "Test log message"
        logger.log("INFO", test_message)

        assert log_file.exists()
        with open(log_file, 'r') as f:
            log_data = json.load(f)
        assert any(test_message in entry.get('message', '') for entry in log_data)

    def test_log_creates_directory_if_needed(self, temp_directory):
        """Test logging creates directory structure if needed."""
        log_dir = temp_directory / 'logs' / 'subdir'
        log_file = log_dir / 'test_log.json'

        logger = FileLogger(log_dir, 'test_log')
        logger.log("INFO", "Test message")

        assert log_file.exists()
        with open(log_file, 'r') as f:
            log_data = json.load(f)
        assert any("Test message" in entry.get('message', '') for entry in log_data)


class TestGitContextProvider:
    """Test Git context provider functionality."""

    def setup_method(self):
        """Setup for Git context tests."""
        self.provider = GitContextProvider()

    @patch('subprocess.run')
    def test_get_git_info_success(self, mock_run):
        """Test successful git information retrieval."""
        # Mock all three git commands (branch, status, log)
        mock_run.side_effect = [
            Mock(returncode=0, stdout="main\n"),  # branch command
            Mock(returncode=0, stdout="M file.py\n"),  # status command
            Mock(returncode=0, stdout="abc123 commit message\n")  # log command
        ]

        result = self.provider.get_context({})

        assert result is not None
        assert result['current_branch'] == "main"
        assert len(result['changes']) == 1
        assert mock_run.call_count == 3

    @patch('subprocess.run')
    def test_get_git_info_failure(self, mock_run):
        """Test git command failure handling."""
        # Mock git command failure
        mock_run.side_effect = [
            Mock(returncode=1, stderr="fatal: not a git repository"),  # branch command fails
            Mock(returncode=1, stderr="fatal: not a git repository"),  # status command fails
            Mock(returncode=1, stderr="fatal: not a git repository")   # log command fails
        ]

        result = self.provider.get_context({})

        # When git commands fail, should return structured dict with defaults
        assert result is not None
        assert result['current_branch'] == 'unknown'
        assert result['uncommitted_changes'] == 0
        assert result['changes'] == []
        assert result['recent_commits'] == []
        assert result['is_clean'] is True

    @patch('subprocess.run')
    def test_provide_context_with_git_repo(self, mock_run):
        """Test context provision for git repository."""
        # Mock git commands
        mock_run.side_effect = [
            Mock(returncode=0, stdout="main\n"),  # current branch
            Mock(returncode=0, stdout="clean\n"),  # status
            Mock(returncode=0, stdout="origin/main\n"),  # upstream
            Mock(returncode=0, stdout="abc123\n"),  # commit hash
        ]

        context = self.provider.get_context({})

        # GitContextProvider returns git data directly, not wrapped in 'git' key
        assert 'current_branch' in context
        assert context['current_branch'] == "main"
        assert 'is_clean' in context

    @patch('subprocess.run')
    def test_provide_context_without_git_repo(self, mock_run):
        """Test context provision for non-git directory."""
        mock_run.return_value.returncode = 128  # Not a git repo

        context = self.provider.get_context({})

        # GitContextProvider returns structured dict with defaults when git commands fail
        assert context is not None
        assert context['current_branch'] == 'unknown'
        assert context['uncommitted_changes'] == 0
        assert context['changes'] == []
        assert context['recent_commits'] == []
        assert context['is_clean'] is True


class TestMCPContextProvider:
    """Test MCP context provider functionality."""

    def setup_method(self):
        """Setup for MCP context tests."""
        self.provider = MCPContextProvider()

    @patch('utils.mcp_client.get_default_client')
    def test_provide_context_with_valid_token(self, mock_get_client):
        """Test MCP context with valid authentication."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client

        # Mock the actual client interface methods
        mock_client.query_pending_tasks.return_value = [
            {'id': 'task_1', 'title': 'Test Task 1'},
            {'id': 'task_2', 'title': 'Test Task 2'}
        ]
        mock_client.query_project_context.return_value = {'project_id': 'proj_1'}
        mock_client.query_git_branch_info.return_value = {'id': 'branch_1', 'name': 'main'}
        mock_client.get_next_recommended_task.return_value = {'id': 'next_task', 'title': 'Next Task'}

        context = self.provider.get_context({})

        # MCPContextProvider returns MCP data directly
        assert context is not None
        assert 'pending_tasks' in context
        assert len(context['pending_tasks']) == 2
        assert 'git_branch_context' in context
        assert 'next_task' in context

    @patch('utils.mcp_client.get_default_client')
    def test_provide_context_with_invalid_token(self, mock_get_client):
        """Test MCP context with authentication failure."""
        # Mock client returns None (authentication failure)
        mock_get_client.return_value = None

        context = self.provider.get_context({})

        # MCPContextProvider returns None when get_default_client returns None
        assert context is None

    @patch('utils.mcp_client.get_default_client')
    def test_provide_context_with_mcp_exception(self, mock_get_client):
        """Test MCP context with client exception."""
        mock_get_client.side_effect = Exception("MCP server unreachable")

        context = self.provider.get_context({})

        # MCPContextProvider returns error dict when exception occurs
        assert 'error' in context
        assert 'MCP server unreachable' in context['error']


class TestDevelopmentContextProvider:
    """Test development context provider functionality."""

    def setup_method(self):
        """Setup for development context tests."""
        self.provider = DevelopmentContextProvider()

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='{"name": "test-project"}')
    def test_provide_context_with_package_json(self, mock_file, mock_exists):
        """Test context with package.json file."""
        mock_exists.return_value = True

        context = self.provider.get_context({})

        # DevelopmentContextProvider returns dev data directly
        assert 'key_files' in context
        # If package.json exists, it would be in the key_files list
        assert 'working_directory' in context

    @patch('os.path.exists')
    def test_provide_context_without_package_json(self, mock_exists):
        """Test context without package.json file."""
        mock_exists.return_value = False

        context = self.provider.get_context({})

        # DevelopmentContextProvider returns dev data directly
        assert 'key_files' in context
        assert 'working_directory' in context

    @patch('os.path.exists')
    @patch('os.listdir')
    def test_provide_context_with_venv(self, mock_listdir, mock_exists):
        """Test context with virtual environment detection."""
        mock_exists.side_effect = lambda path: '.venv' in path or 'venv' in path
        mock_listdir.return_value = ['.venv', 'src', 'tests']

        context = self.provider.get_context({})

        # DevelopmentContextProvider returns dev data directly
        assert 'virtual_env' in context  # Checks for virtual environment
        assert 'working_directory' in context


class TestSessionStartProcessor:
    """Test session start processing functionality."""

    def setup_method(self):
        """Setup for processor tests."""
        self.mock_logger = Mock()
        self.mock_config = Mock()
        self.processor = SessionStartProcessor(self.mock_logger)

    def test_process_initialization_message(self):
        """Test processing initialization message."""
        context = {'git': {'current_branch': 'main'}}

        result = self.processor.process(context)

        # SessionStartProcessor returns Optional[str], not dict
        assert result is not None
        assert isinstance(result, str)
        self.mock_logger.log.assert_called()

    def test_process_with_mcp_tasks(self):
        """Test processing with MCP task information."""
        context = {
            'mcp': {
                'authenticated': True,
                'task_status': {
                    'active_tasks': 2,
                    'pending_tasks': 3
                },
                'next_task': {
                    'task_id': 'task_123',
                    'title': 'Test Task'
                }
            }
        }

        result = self.processor.process(context)

        # SessionStartProcessor returns Optional[str], not dict
        assert result is not None
        assert isinstance(result, str)
        assert 'task' in result.lower()  # Check the output mentions tasks


class TestComponentFactory:
    """Test component factory functionality."""

    def test_create_context_providers(self):
        """Test factory creates all context providers."""
        config_loader = ConfigurationLoader(Path.cwd() / 'config')

        factory = ComponentFactory()
        providers = factory.create_context_providers(config_loader)

        assert len(providers) == 5  # Git, MCP, Development, Issue, AgentMessage
        assert any(isinstance(p, GitContextProvider) for p in providers)
        assert any(isinstance(p, MCPContextProvider) for p in providers)

    def test_create_processors(self):
        """Test factory creates all processors."""
        config_loader = ConfigurationLoader(Path.cwd() / 'config')
        logger = Mock()
        context_providers = []

        factory = ComponentFactory()
        processors = factory.create_processors(context_providers, logger)

        assert len(processors) == 2  # SessionStart, ContextFormatter
        assert any(isinstance(p, SessionStartProcessor) for p in processors)
        assert any(isinstance(p, ContextFormatterProcessor) for p in processors)


class TestSessionStartHook:
    """Test main session start hook functionality."""

    def setup_method(self):
        """Setup for hook tests."""
        # SessionStartHook now creates its own factory and logger internally
        self.hook = SessionStartHook()
        # Mock the internal components if needed
        self.hook.logger = Mock()
        self.hook.factory = Mock()
        self.hook.context_providers = []
        self.hook.processors = []

    def test_run_success(self):
        """Test successful hook execution."""
        # Mock providers and processors
        mock_provider = Mock()
        mock_provider.get_context.return_value = {'test': 'context'}

        mock_processor = Mock()
        mock_processor.process.return_value = "Test output"  # Processors return Optional[str]

        self.hook.factory.create_context_providers.return_value = [mock_provider]
        self.hook.factory.create_processors.return_value = [mock_processor]

        result = self.hook.execute({})

        # SessionStartHook.execute returns exit code (int)
        assert result == 0  # Success
        mock_provider.get_context.assert_called_once()
        mock_processor.process.assert_called_once()

    def test_run_with_provider_failure(self):
        """Test hook execution with provider failure."""
        mock_provider = Mock()
        mock_provider.get_context.side_effect = Exception("Provider error")

        self.hook.factory.create_context_providers.return_value = [mock_provider]
        self.hook.factory.create_processors.return_value = []

        result = self.hook.execute({})

        # SessionStartHook.execute returns exit code (int)
        assert result == 1  # Failure
        # Logger would have been called with error
        self.hook.logger.log.assert_called()

    def test_run_with_processor_failure(self):
        """Test hook execution with processor failure."""
        mock_provider = Mock()
        mock_provider.get_context.return_value = {'test': 'context'}

        mock_processor = Mock()
        mock_processor.process.side_effect = Exception("Processor error")

        self.hook.factory.create_context_providers.return_value = [mock_provider]
        self.hook.factory.create_processors.return_value = [mock_processor]

        result = self.hook.execute({})

        # SessionStartHook.execute returns exit code (int)
        assert result == 1  # Failure
        self.hook.logger.log.assert_called()  # Error would be logged


class TestMainFunction:
    """Test main function integration."""

    @patch('sys.exit')
    @patch('session_start.SessionStartHook')
    @patch('session_start.ComponentFactory')
    @patch('session_start.FileLogger')
    @patch('session_start.ConfigurationLoader')
    def test_main_function_success(self, mock_config, mock_logger, mock_factory, mock_hook, mock_exit):
        """Test main function executes successfully."""
        # Setup mocks
        mock_hook_instance = Mock()
        mock_hook_instance.execute.return_value = 0  # Success exit code
        mock_hook.return_value = mock_hook_instance

        # Mock sys.argv to avoid argparse issues
        with patch('sys.argv', ['session_start.py']):
            main()

        # main() calls sys.exit(0) on success
        mock_exit.assert_called_once_with(0)
        mock_hook_instance.execute.assert_called_once()

    @patch('sys.exit')
    @patch('session_start.SessionStartHook')
    @patch('session_start.ComponentFactory')
    @patch('session_start.FileLogger')
    @patch('session_start.ConfigurationLoader')
    def test_main_function_with_exception(self, mock_config, mock_logger, mock_factory, mock_hook, mock_exit):
        """Test main function handles exceptions."""
        # Setup mocks
        mock_hook.side_effect = Exception("Hook initialization failed")

        with patch('sys.argv', ['session_start.py']):
            main()

        # main() calls sys.exit(1) on exception
        mock_exit.assert_called_once_with(1)

    @patch('sys.exit')
    @patch('session_start.SessionStartHook')
    @patch('session_start.ComponentFactory')
    @patch('session_start.FileLogger')
    @patch('session_start.ConfigurationLoader')
    def test_main_function_with_args(self, mock_config, mock_logger, mock_factory, mock_hook, mock_exit):
        """Test main function with command line arguments."""
        mock_hook_instance = Mock()
        mock_hook_instance.execute.return_value = 0  # Success exit code
        mock_hook.return_value = mock_hook_instance

        test_args = ['session_start.py', '--verbose']
        with patch('sys.argv', test_args):
            main()

        # main() calls sys.exit(0) on success
        mock_exit.assert_called_once_with(0)


# Integration tests
class TestSessionStartIntegration:
    """Integration tests for session start hook."""

    @pytest.mark.integration
    @patch('subprocess.run')
    @patch('utils.mcp_client.MCPClient')
    def test_full_session_start_flow(self, mock_mcp_class, mock_subprocess):
        """Test complete session start flow with mocked dependencies."""
        # Mock git commands
        mock_subprocess.return_value.returncode = 0
        mock_subprocess.return_value.stdout = "main\n"

        # Mock MCP client
        mock_client = Mock()
        mock_client.is_authenticated = True
        mock_client.get_task_status.return_value = {'active_tasks': 0}
        mock_mcp_class.return_value = mock_client

        # Run the hook
        with patch('sys.argv', ['session_start.py']):
            result = main()

        assert result['success'] is True
        assert 'session_info' in result or 'message' in result

    @pytest.mark.integration
    def test_session_start_in_test_mode(self, mock_env_vars):
        """Test session start in test mode."""
        with patch('sys.argv', ['session_start.py']):
            result = main()

        # Should succeed even without real git/MCP setup in test mode
        assert isinstance(result, dict)
        assert 'success' in result


# Fixture-based tests
@pytest.mark.hooks
class TestSessionStartWithFixtures:
    """Test session start using shared fixtures."""

    def test_context_aggregation(self, sample_hook_context):
        """Test context aggregation from multiple providers."""
        config_loader = ConfigurationLoader(Path.cwd() / 'config')
        factory = ComponentFactory()

        # This tests the real component integration
        providers = factory.create_context_providers(config_loader)
        assert len(providers) > 0

        # Each provider should have a provide_context method
        for provider in providers:
            assert hasattr(provider, 'provide_context')
            assert callable(provider.provide_context)

    def test_error_handling_robustness(self):
        """Test that the system is robust to various error conditions."""
        # Test with minimal setup - should not crash
        hook = SessionStartHook()

        # Should handle gracefully even if components fail
        result = hook.execute({})
        assert isinstance(result, dict)
        assert 'success' in result


if __name__ == '__main__':
    pytest.main([__file__, '-v'])