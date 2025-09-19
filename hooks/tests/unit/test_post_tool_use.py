"""
Unit tests for post_tool_use.py hook.

Tests the post-tool processing hook functionality including documentation updates,
context synchronization, agent state tracking, and hint generation.
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

from post_tool_use import (
    FileLogger,
    DocumentationUpdater,
    HintGenerator,
    AgentStateTracker,
    ContextSynchronizer,
    ComponentFactory,
    PostToolUseHook,
    main
)


class TestFileLogger:
    """Test file logging functionality for post-tool use."""

    def test_initialization(self, temp_directory):
        """Test FileLogger initializes correctly."""
        log_file = temp_directory / 'post_tool_use.json'
        logger = FileLogger(temp_directory, 'post_tool_use')

        assert logger.log_path == log_file

    def test_log_writes_processing_message(self, temp_directory):
        """Test logging writes processing messages."""
        log_file = temp_directory / 'post_tool_use.json'
        logger = FileLogger(temp_directory, 'post_tool_use')

        test_message = "Processing tool result: Edit"
        logger.log("INFO", test_message)

        assert log_file.exists()
        with open(log_file, 'r') as f:
            log_data = json.load(f)
        assert any(test_message in entry.get('message', '') for entry in log_data)


class TestDocumentationUpdater:
    """Test documentation updating functionality."""

    def setup_method(self):
        """Setup for documentation updater tests."""
        self.ai_docs_path = Path('/project/ai_docs')
        self.updater = DocumentationUpdater(self.ai_docs_path)

    @patch('utils.docs_indexer.update_index')
    def test_process_ai_docs_update(self, mock_update_index):
        """Test processing AI docs update."""
        mock_update_index.return_value = True

        tool_data = {
            'tool_name': 'Write',
            'tool_params': {
                'file_path': '/project/ai_docs/new_guide.md',
                'content': 'Documentation content'
            },
            'tool_result': {'success': True}
        }

        result = self.updater.process(
            tool_data['tool_name'],
            tool_data['tool_params'],
            tool_data['tool_result']
        )

        # Processor returns Optional[str], not dict per architecture
        # DocumentationUpdater returns dict for this specific case (see implementation)
        assert result is not None
        assert isinstance(result, dict)
        assert result.get('updated') is True
        mock_update_index.assert_called_once_with(self.ai_docs_path)

    @patch('utils.docs_indexer.update_index')
    def test_process_non_ai_docs_file(self, mock_update_index):
        """Test processing non-AI docs file."""
        tool_data = {
            'tool_name': 'Write',
            'tool_params': {
                'file_path': '/project/src/main.py',
                'content': 'Python code'
            },
            'tool_result': {'success': True}
        }

        result = self.updater.process(
            tool_data['tool_name'],
            tool_data['tool_params'],
            tool_data.get('tool_result', {})
        )

        assert result is None  # Non-ai_docs files return None
        mock_update_index.assert_not_called()

    @patch('utils.docs_indexer.update_index')
    def test_process_failed_tool_result(self, mock_update_index):
        """Test processing failed tool result - but still updates if ai_docs file."""
        tool_data = {
            'tool_name': 'Write',
            'tool_params': {
                'file_path': '/project/ai_docs/guide.md',
                'content': 'Content'
            },
            'tool_result': {'success': False, 'error': 'Write failed'}
        }

        result = self.updater.process(
            tool_data['tool_name'],
            tool_data['tool_params'],
            tool_data.get('tool_result', {})
        )

        # DocumentationUpdater still processes ai_docs file even if tool failed
        # It only cares if the file path is in ai_docs, not the tool result
        assert result is not None
        assert isinstance(result, dict)
        assert result.get('updated') is True
        mock_update_index.assert_called_once()

    @patch('utils.docs_indexer.update_index')
    def test_process_update_index_failure(self, mock_update_index):
        """Test processing when index update fails."""
        mock_update_index.side_effect = Exception("Index update failed")

        tool_data = {
            'tool_name': 'Write',
            'tool_params': {
                'file_path': '/project/ai_docs/guide.md',
                'content': 'Content'
            },
            'tool_result': {'success': True}
        }

        result = self.updater.process(
            tool_data['tool_name'],
            tool_data['tool_params'],
            tool_data.get('tool_result', {})
        )

        # DocumentationUpdater returns dict on error (see implementation)
        assert result is not None
        assert isinstance(result, dict)
        assert result.get('updated') is False
        assert 'error' in result

    def test_process_non_file_tool(self):
        """Test processing non-file tools."""
        tool_data = {
            'tool_name': 'Bash',
            'tool_params': {'command': 'ls -la'},
            'tool_result': {'success': True}
        }

        result = self.updater.process(
            tool_data['tool_name'],
            tool_data['tool_params'],
            tool_data.get('tool_result', {})
        )

        assert result is None  # Non-ai_docs files return None


class TestHintGenerator:
    """Test hint generation functionality."""

    def setup_method(self):
        """Setup for hint generator tests."""
        self.mock_logger = Mock()
        self.generator = HintGenerator(self.mock_logger)

    @patch('utils.unified_hint_system.store_hint_for_later')
    @patch('utils.unified_hint_system.generate_post_action_hints')
    def test_process_successful_hint_generation(self, mock_generate, mock_store):
        """Test successful hint generation and storage."""
        mock_generate.return_value = "Test hint generated"
        mock_store.return_value = True

        # Use MCP tool name that the HintGenerator actually processes
        tool_data = {
            'tool_name': 'mcp__agenthub_http__manage_task',
            'tool_params': {'action': 'create', 'title': 'Test task'},
            'tool_result': {'success': True}
        }

        result = self.generator.process(
            tool_data.get('tool_name'),
            tool_data.get('tool_params', {}),
            tool_data.get('tool_result')
        )

        # HintGenerator returns Optional[str]
        # It may return hints or None
        assert result is None or isinstance(result, str)
        mock_generate.assert_called_once()
        mock_store.assert_called_once()

    @patch('utils.unified_hint_system.get_hint_system')
    def test_process_no_hints_generated(self, mock_get_system):
        """Test when no hints are generated."""
        mock_system = Mock()
        mock_system.get_post_action_hints.return_value = []
        mock_get_system.return_value = mock_system

        tool_data = {
            'tool_name': 'Read',
            'tool_params': {'file_path': '/project/README.md'},
            'tool_result': {'success': True}
        }

        result = self.generator.process(
            tool_data.get('tool_name'),
            tool_data.get('tool_params', {}),
            tool_data.get('tool_result')
        )

        # HintGenerator returns Optional[str], may be None when no hints
        assert result is None or result == ""

    @patch('utils.unified_hint_system.get_hint_system')
    def test_process_hint_storage_failure(self, mock_get_system):
        """Test hint generation with storage failure."""
        mock_system = Mock()
        mock_system.get_post_action_hints.return_value = ["Test hint"]
        mock_system.hint_bridge.store_hints.return_value = False
        mock_get_system.return_value = mock_system

        tool_data = {
            'tool_name': 'Edit',
            'tool_params': {'file_path': '/project/src/module.py'},
            'tool_result': {'success': True}
        }

        result = self.generator.process(
            tool_data.get('tool_name'),
            tool_data.get('tool_params', {}),
            tool_data.get('tool_result')
        )

        # HintGenerator returns Optional[str]
        # Storage failure is non-critical
        if result is not None:
            assert isinstance(result, str)

    @patch('utils.unified_hint_system.get_hint_system')
    def test_process_hint_generation_exception(self, mock_get_system):
        """Test hint generation with exception."""
        mock_get_system.side_effect = Exception("Hint generation failed")

        tool_data = {
            'tool_name': 'Edit',
            'tool_params': {'file_path': '/project/src/module.py'},
            'tool_result': {'success': True}
        }

        result = self.generator.process(
            tool_data.get('tool_name'),
            tool_data.get('tool_params', {}),
            tool_data.get('tool_result')
        )

        # HintGenerator returns Optional[str]
        # Exception is handled internally, non-critical failure
        assert result is None or isinstance(result, str)

    def test_process_failed_tool_result(self):
        """Test processing failed tool result."""
        tool_data = {
            'tool_name': 'Edit',
            'tool_params': {'file_path': '/project/src/module.py'},
            'tool_result': {'success': False, 'error': 'Edit failed'}
        }

        result = self.generator.process(
            tool_data.get('tool_name'),
            tool_data.get('tool_params', {}),
            tool_data.get('tool_result')
        )

        # HintGenerator returns Optional[str]
        # Failed tool results may not generate hints
        assert result is None or isinstance(result, str)


class TestAgentStateTracker:
    """Test agent state tracking functionality."""

    def setup_method(self):
        """Setup for agent state tracker tests."""
        self.mock_logger = Mock()
        self.tracker = AgentStateTracker(self.mock_logger)

    @patch('utils.agent_state_manager.update_agent_state_from_call_agent')
    def test_process_successful_state_tracking(self, mock_update):
        """Test successful agent state tracking with call_agent tool."""
        mock_update.return_value = True

        tool_name = 'mcp__agenthub_http__call_agent'
        tool_params = {'name_agent': 'coding-agent'}
        tool_result = {'success': True}

        result = self.tracker.process(tool_name, tool_params, tool_result)

        # AgentStateTracker returns dict on successful call_agent processing
        assert result is not None
        assert isinstance(result, dict)
        assert result.get('agent_state_updated') is True
        assert result.get('agent') == 'coding-agent'
        mock_update.assert_called_once_with('default_session', tool_params)

    def test_process_non_call_agent_tool(self):
        """Test processing non-call_agent tool - should return None."""
        tool_name = 'Edit'
        tool_params = {'file_path': '/project/src/module.py'}
        tool_result = {'success': True}

        result = self.tracker.process(tool_name, tool_params, tool_result)

        # AgentStateTracker only processes call_agent tool, returns None for others
        assert result is None

    @patch('utils.agent_state_manager.update_agent_state_from_call_agent')
    def test_process_state_tracking_exception(self, mock_update):
        """Test agent state tracking with exception."""
        mock_update.side_effect = Exception("State tracking failed")

        tool_name = 'mcp__agenthub_http__call_agent'
        tool_params = {'name_agent': 'coding-agent'}
        tool_result = {'success': True}

        result = self.tracker.process(tool_name, tool_params, tool_result)

        # AgentStateTracker returns None on exception
        assert result is None
        self.mock_logger.log.assert_called_with('error', 'Agent state update failed: State tracking failed')

    def test_process_missing_agent_name(self):
        """Test processing call_agent without agent name."""
        tool_name = 'mcp__agenthub_http__call_agent'
        tool_params = {}  # Missing name_agent
        tool_result = {'success': True}

        result = self.tracker.process(tool_name, tool_params, tool_result)

        # Returns None if no agent name provided
        assert result is None


class TestContextSynchronizer:
    """Test context synchronization functionality."""

    def setup_method(self):
        """Setup for context synchronizer tests."""
        self.mock_logger = Mock()
        self.synchronizer = ContextSynchronizer(self.mock_logger)

    @patch('utils.context_updater.update_context_sync')
    def test_process_successful_context_sync(self, mock_sync):
        """Test successful context synchronization."""
        mock_sync.return_value = True

        tool_name = 'Edit'
        tool_params = {'file_path': '/project/src/module.py'}
        tool_result = {'success': True}

        result = self.synchronizer.process(tool_name, tool_params, tool_result)

        # ContextSynchronizer returns dict on success (see implementation)
        assert result is not None
        assert isinstance(result, dict)
        assert result.get('context_synced') is True
        mock_sync.assert_called_once_with(tool_name, tool_params)

    @patch('utils.context_updater.update_context_sync')
    def test_process_context_sync_failure(self, mock_sync):
        """Test context synchronization failure."""
        mock_sync.return_value = False

        tool_name = 'Edit'
        tool_params = {'file_path': '/project/src/module.py'}
        tool_result = {'success': True}

        result = self.synchronizer.process(tool_name, tool_params, tool_result)

        # ContextSynchronizer returns None if update_context_sync returns False
        assert result is None
        mock_sync.assert_called_once_with(tool_name, tool_params)

    @patch('utils.context_updater.update_context_sync')
    def test_process_context_sync_exception(self, mock_sync):
        """Test context synchronization with exception."""
        mock_sync.side_effect = Exception("Context sync failed")

        tool_name = 'Edit'
        tool_params = {'file_path': '/project/src/module.py'}
        tool_result = {'success': True}

        result = self.synchronizer.process(tool_name, tool_params, tool_result)

        # ContextSynchronizer returns None on exception (see implementation)
        assert result is None
        self.mock_logger.log.assert_called_with('error', 'Context sync failed: Context sync failed')

    @patch('utils.context_updater.update_context_sync')
    def test_process_with_non_edit_tool(self, mock_sync):
        """Test processing non-edit tool."""
        mock_sync.return_value = False

        tool_name = 'Bash'
        tool_params = {'command': 'ls -la'}
        tool_result = {'output': 'file list'}

        result = self.synchronizer.process(tool_name, tool_params, tool_result)

        # Returns None if update_context_sync returns False
        assert result is None
        mock_sync.assert_called_once_with(tool_name, tool_params)


class TestComponentFactory:
    """Test component factory functionality."""

    def test_create_components(self):
        """Test factory creates all components."""
        logger = Mock()
        ai_docs_path = Path('/project/ai_docs')

        # ComponentFactory uses static methods for individual components
        factory = ComponentFactory()

        # Create each component using individual static methods
        doc_updater = factory.create_documentation_updater(ai_docs_path)
        hint_gen = factory.create_hint_generator(logger)
        agent_tracker = factory.create_agent_tracker(logger)
        context_sync = factory.create_context_synchronizer(logger)

        components = [doc_updater, hint_gen, agent_tracker, context_sync]

        assert len(components) == 4  # Documentation, Hint, AgentState, Context
        assert isinstance(doc_updater, DocumentationUpdater)
        assert isinstance(hint_gen, HintGenerator)
        assert isinstance(agent_tracker, AgentStateTracker)
        assert isinstance(context_sync, ContextSynchronizer)


class TestPostToolUseHook:
    """Test main post-tool use hook functionality."""

    def setup_method(self):
        """Setup for hook tests."""
        # PostToolUseHook now creates its own factory and logger internally
        self.hook = PostToolUseHook()
        # Mock the internal components if needed
        self.hook.logger = Mock()
        self.hook.factory = Mock()
        self.hook.components = []

    def test_run_successful_processing(self):
        """Test hook execution with successful processing."""
        # Mock components - they need to return Optional[str] per architecture
        mock_component = Mock()
        mock_component.process.return_value = "Processing successful"

        # Directly set components instead of mocking factory.create_components
        self.hook.components = [mock_component]

        tool_data = {
            'tool_name': 'Edit',
            'tool_params': {'file_path': '/project/src/module.py'},
            'tool_result': {'success': True}
        }

        result = self.hook.execute(tool_data)

        assert result == 0  # PostToolUseHook.execute returns exit code
        mock_component.process.assert_called_once_with(
            tool_data['tool_name'],
            tool_data['tool_params'],
            tool_data['tool_result']
        )

    def test_run_with_component_failure(self):
        """Test hook execution with component failure."""
        mock_component = Mock()
        mock_component.process.side_effect = Exception("Component error")

        # Directly set components instead of mocking factory.create_components
        self.hook.components = [mock_component]

        tool_data = {
            'tool_name': 'Edit',
            'tool_params': {'file_path': '/project/src/module.py'},
            'tool_result': {'success': True}
        }

        result = self.hook.execute(tool_data)

        # Should continue processing despite individual component failures
        assert result == 0  # PostToolUseHook still returns 0 even with component errors
        self.hook.logger.log.assert_called()

    def test_run_with_multiple_components(self):
        """Test hook execution with multiple components."""
        mock_doc_updater = Mock()
        mock_doc_updater.process.return_value = "Documentation updated"

        mock_hint_generator = Mock()
        mock_hint_generator.process.return_value = "Test hint generated"

        # Directly set components instead of mocking factory.create_components
        self.hook.components = [mock_doc_updater, mock_hint_generator]

        tool_data = {
            'tool_name': 'Write',
            'tool_params': {'file_path': '/project/ai_docs/guide.md'},
            'tool_result': {'success': True}
        }

        result = self.hook.execute(tool_data)

        assert result == 0  # PostToolUseHook returns exit code
        # Both components should be called
        mock_doc_updater.process.assert_called_once()
        mock_hint_generator.process.assert_called_once()

    def test_run_with_missing_tool_data(self):
        """Test hook execution with missing tool data."""
        result = self.hook.execute({})

        assert result == 1  # PostToolUseHook returns 1 on error
        self.hook.logger.log.assert_called()

    def test_run_with_invalid_tool_data(self):
        """Test hook execution with invalid tool data."""
        result = self.hook.execute({'invalid': 'data'})

        assert result == 1  # PostToolUseHook returns 1 on error
        self.hook.logger.log.assert_called()


class TestMainFunction:
    """Test main function integration."""

    @patch('post_tool_use.PostToolUseHook')
    @patch('post_tool_use.ComponentFactory')
    @patch('sys.exit')
    @patch('post_tool_use.FileLogger')
    @patch('sys.stdin.read')
    def test_main_function_success(self, mock_stdin, mock_logger, mock_exit, mock_factory, mock_hook):
        """Test main function executes successfully."""
        # Mock stdin input
        tool_data = {
            'tool_name': 'Edit',
            'tool_params': {'file_path': '/project/src/module.py'},
            'tool_result': {'success': True}
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

    @patch('post_tool_use.PostToolUseHook')
    @patch('post_tool_use.ComponentFactory')
    @patch('sys.exit')
    @patch('post_tool_use.FileLogger')
    @patch('sys.stdin.read')
    def test_main_function_with_invalid_json(self, mock_stdin, mock_logger, mock_exit, mock_factory, mock_hook):
        """Test main function with invalid JSON input."""
        mock_stdin.return_value = "invalid json"

        main()

        # main() calls sys.exit, check it was called with error code
        mock_exit.assert_called_once_with(1)

    @patch('post_tool_use.PostToolUseHook')
    @patch('post_tool_use.ComponentFactory')
    @patch('sys.exit')
    @patch('post_tool_use.FileLogger')
    @patch('sys.stdin.read')
    def test_main_function_with_exception(self, mock_stdin, mock_logger, mock_exit, mock_factory, mock_hook):
        """Test main function handles exceptions."""
        mock_stdin.return_value = '{"tool_name": "Edit"}'
        mock_hook.side_effect = Exception("Hook initialization failed")

        main()

        # main() calls sys.exit on exception
        mock_exit.assert_called_once_with(1)

    @patch('post_tool_use.PostToolUseHook')
    @patch('post_tool_use.ComponentFactory')
    @patch('sys.exit')
    @patch('post_tool_use.FileLogger')
    @patch('sys.stdin.read')
    def test_main_function_comprehensive_processing(self, mock_stdin, mock_logger, mock_exit, mock_factory, mock_hook):
        """Test main function with comprehensive processing results."""
        tool_data = {
            'tool_name': 'Write',
            'tool_params': {
                'file_path': '/project/ai_docs/api-guide.md',
                'content': 'API documentation content'
            },
            'tool_result': {'success': True}
        }
        mock_stdin.return_value = json.dumps(tool_data)

        mock_hook_instance = Mock()
        mock_hook_instance.execute.return_value = 0  # Success
        mock_hook.return_value = mock_hook_instance

        main()

        # main() calls sys.exit(0) on success
        mock_exit.assert_called_once_with(0)


# Integration tests
class TestPostToolUseIntegration:
    """Integration tests for post-tool use hook."""

    @pytest.mark.integration
    @patch('utils.docs_indexer.update_documentation_index')
    @patch('utils.unified_hint_system.get_hint_system')
    def test_full_processing_flow(self, mock_get_system, mock_docs):
        """Test complete processing flow with mocked dependencies."""
        mock_docs.return_value = True
        mock_system = Mock()
        mock_system.get_post_action_hints.return_value = ['Test hint']
        mock_get_system.return_value = mock_system

        tool_data = {
            'tool_name': 'Write',
            'tool_params': {
                'file_path': '/project/ai_docs/test_guide.md',
                'content': 'Test documentation'
            },
            'tool_result': {'success': True}
        }

        with patch('sys.stdin.read', return_value=json.dumps(tool_data)):
            result = main()

        assert result['success'] is True
        assert 'processing_results' in result

    @pytest.mark.integration
    def test_post_tool_use_in_test_mode(self, mock_env_vars):
        """Test post-tool use in test mode."""
        tool_data = {
            'tool_name': 'Read',
            'tool_params': {'file_path': '/test/file.py'},
            'tool_result': {'success': True}
        }

        with patch('sys.stdin.read', return_value=json.dumps(tool_data)):
            result = main()

        # Should work in test mode
        assert isinstance(result, dict)
        assert 'success' in result

    @pytest.mark.integration
    def test_processing_chain_resilience(self):
        """Test that processing chain is resilient to individual failures."""
        tool_data = {
            'tool_name': 'Edit',
            'tool_params': {'file_path': '/project/src/test.py'},
            'tool_result': {'success': True}
        }

        # Even with component failures, the hook should continue
        with patch('sys.stdin.read', return_value=json.dumps(tool_data)):
            result = main()

        assert isinstance(result, dict)
        assert 'success' in result


# Fixture-based tests
@pytest.mark.hooks
class TestPostToolUseWithFixtures:
    """Test post-tool use using shared fixtures."""

    def test_component_chain(self):
        """Test component chain execution."""
        logger = Mock()
        factory = ComponentFactory(logger)

        components = factory.create_components()
        assert len(components) > 0

        # Each component should have a process method
        for component in components:
            assert hasattr(component, 'process')
            assert callable(component.process)

    def test_robust_error_handling(self):
        """Test robust error handling across components."""
        logger = Mock()
        factory = ComponentFactory(logger)

        # Test with minimal setup - should not crash
        hook = PostToolUseHook(factory, logger)

        # Should handle gracefully even if components fail
        result = hook.run({
            'tool_name': 'Test',
            'tool_params': {},
            'tool_result': {'success': True}
        })

        assert isinstance(result, dict)
        assert 'success' in result


if __name__ == '__main__':
    pytest.main([__file__, '-v'])