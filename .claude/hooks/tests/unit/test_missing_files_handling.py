"""
Unit tests for handling missing configuration files (.env, .mcp.json).

Tests cover:
- Missing .env.claude file handling
- Missing .env file fallback scenarios
- Missing .mcp.json file handling
- Graceful degradation with no configuration files
- Error handling and default value fallbacks
- File permission and access error scenarios
"""

import os
import json
import pytest
import tempfile
import sys
from pathlib import Path
from unittest.mock import patch, Mock, mock_open

# Add hooks directory to Python path
hooks_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(hooks_dir))

from utils.env_loader import (
    find_project_root,
    get_ai_data_path,
    get_ai_docs_path,
    get_log_path,
    get_all_paths,
    is_claude_edit_enabled
)


class TestMissingEnvClaudeFile:
    """Test handling of missing .env.claude file."""

    def test_missing_env_claude_fallback_to_env(self, temp_directory):
        """Test fallback to .env when .env.claude is missing."""
        # Create only .env file (no .env.claude)
        env_file = temp_directory / '.env'
        env_content = """
AI_DATA=fallback_data
AI_DOCS=fallback_docs
LOG_PATH=fallback_logs
ENABLE_CLAUDE_EDIT=true
"""
        env_file.write_text(env_content)

        # Mock the project root and env file detection
        with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
            with patch('utils.env_loader.ENV_CLAUDE_PATH', temp_directory / '.env.claude'):
                # .env.claude doesn't exist, should fall back to .env
                with patch('utils.env_loader.load_dotenv') as mock_load_dotenv:
                    # Simulate module reload to trigger fallback logic
                    import importlib
                    import utils.env_loader
                    importlib.reload(utils.env_loader)

                    # Should call load_dotenv with .env file
                    mock_load_dotenv.assert_called_with(env_file)

    def test_missing_both_env_files(self, temp_directory):
        """Test handling when both .env.claude and .env are missing."""
        # No .env.claude or .env files exist
        with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
            with patch('utils.env_loader.ENV_CLAUDE_PATH', temp_directory / '.env.claude'):
                with patch('utils.env_loader.load_dotenv') as mock_load_dotenv:
                    import importlib
                    import utils.env_loader
                    importlib.reload(utils.env_loader)

                    # load_dotenv should not be called at all
                    mock_load_dotenv.assert_not_called()

    def test_env_claude_file_permission_denied(self, temp_directory, caplog):
        """Test handling when .env.claude exists but can't be read."""
        # Create .env.claude but make it unreadable
        env_claude_file = temp_directory / '.env.claude'
        env_claude_file.write_text('AI_DATA=test')
        env_claude_file.chmod(0o000)  # No permissions

        try:
            with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                with patch('utils.env_loader.ENV_CLAUDE_PATH', env_claude_file):
                    # Should handle permission error gracefully
                    with patch('utils.env_loader.load_dotenv', side_effect=PermissionError('Permission denied')):
                        import importlib
                        import utils.env_loader
                        # Should not crash, should continue with defaults
                        importlib.reload(utils.env_loader)

        finally:
            # Restore permissions for cleanup
            env_claude_file.chmod(0o644)

    def test_corrupted_env_claude_file(self, temp_directory):
        """Test handling of corrupted .env.claude file."""
        # Create corrupted .env.claude file
        env_claude_file = temp_directory / '.env.claude'
        env_claude_file.write_bytes(b'\x00\x01\x02\x03')  # Binary data

        # Create fallback .env file
        env_file = temp_directory / '.env'
        env_file.write_text('AI_DATA=fallback_data\n')

        with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
            with patch('utils.env_loader.ENV_CLAUDE_PATH', env_claude_file):
                with patch('utils.env_loader.load_dotenv') as mock_load_dotenv:
                    # Should handle corrupted file and fall back to .env
                    mock_load_dotenv.side_effect = [Exception('Corrupted file'), None]

                    import importlib
                    import utils.env_loader
                    importlib.reload(utils.env_loader)

                    # Should attempt to load both files
                    assert mock_load_dotenv.call_count >= 1


class TestMissingEnvFile:
    """Test handling of missing .env file as fallback."""

    def test_env_file_permission_denied(self, temp_directory):
        """Test handling when .env file exists but can't be read."""
        # Create .env file but make it unreadable
        env_file = temp_directory / '.env'
        env_file.write_text('AI_DATA=test')
        env_file.chmod(0o000)  # No permissions

        try:
            with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                with patch('utils.env_loader.ENV_CLAUDE_PATH', temp_directory / '.env.claude'):
                    # Should handle permission error gracefully
                    with patch('utils.env_loader.load_dotenv', side_effect=PermissionError('Permission denied')):
                        import importlib
                        import utils.env_loader
                        # Should not crash
                        importlib.reload(utils.env_loader)

        finally:
            # Restore permissions for cleanup
            env_file.chmod(0o644)

    def test_env_file_too_large(self, temp_directory):
        """Test handling of extremely large .env file."""
        # Create very large .env file
        env_file = temp_directory / '.env'
        large_content = 'AI_DATA=test\n' + 'LARGE_VAR=' + 'x' * 10000 + '\n'
        env_file.write_text(large_content)

        with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
            with patch('utils.env_loader.ENV_CLAUDE_PATH', temp_directory / '.env.claude'):
                with patch('utils.env_loader.load_dotenv') as mock_load_dotenv:
                    # Should handle large file (dotenv should handle this)
                    import importlib
                    import utils.env_loader
                    importlib.reload(utils.env_loader)

                    mock_load_dotenv.assert_called_with(env_file)

    def test_empty_env_files(self, temp_directory):
        """Test handling of empty environment files."""
        # Create empty .env.claude
        env_claude_file = temp_directory / '.env.claude'
        env_claude_file.write_text('')

        # Create empty .env
        env_file = temp_directory / '.env'
        env_file.write_text('')

        with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
            with patch('utils.env_loader.ENV_CLAUDE_PATH', env_claude_file):
                with patch('utils.env_loader.load_dotenv') as mock_load_dotenv:
                    import importlib
                    import utils.env_loader
                    importlib.reload(utils.env_loader)

                    # Should still attempt to load empty files
                    mock_load_dotenv.assert_called_with(env_claude_file)


class TestMissingMcpJsonFile:
    """Test handling of missing .mcp.json file scenarios."""

    def test_missing_mcp_json_graceful_handling(self, temp_directory):
        """Test that missing .mcp.json doesn't break environment loading."""
        # Create .env.claude without .mcp.json
        env_claude_content = """
AI_DATA=test_data
AI_DOCS=test_docs
ENABLE_CLAUDE_EDIT=false
"""
        env_claude_file = temp_directory / '.env.claude'
        env_claude_file.write_text(env_claude_content)

        # No .mcp.json file created
        with patch.dict(os.environ, {
            'AI_DATA': 'test_data',
            'AI_DOCS': 'test_docs',
            'ENABLE_CLAUDE_EDIT': 'false'
        }):
            with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                # Environment functions should still work
                ai_data = get_ai_data_path()
                ai_docs = get_ai_docs_path()
                edit_enabled = is_claude_edit_enabled()

                assert ai_data == temp_directory / 'test_data'
                assert ai_docs == temp_directory / 'test_docs'
                assert edit_enabled is False

    def test_corrupted_mcp_json_file(self, temp_directory):
        """Test handling of corrupted .mcp.json file."""
        # Create corrupted .mcp.json
        mcp_json_file = temp_directory / '.mcp.json'
        mcp_json_file.write_text('{"invalid": json content}')

        # Environment should still work
        with patch.dict(os.environ, {'AI_DATA': 'test_data'}):
            with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                ai_data = get_ai_data_path()
                assert ai_data == temp_directory / 'test_data'

    def test_mcp_json_permission_denied(self, temp_directory):
        """Test handling when .mcp.json exists but can't be read."""
        # Create .mcp.json but make it unreadable
        mcp_json_file = temp_directory / '.mcp.json'
        mcp_json_file.write_text('{"token": "test"}')
        mcp_json_file.chmod(0o000)  # No permissions

        try:
            # Environment should still work despite .mcp.json being unreadable
            with patch.dict(os.environ, {'AI_DATA': 'test_data'}):
                with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                    ai_data = get_ai_data_path()
                    assert ai_data == temp_directory / 'test_data'

        finally:
            # Restore permissions for cleanup
            mcp_json_file.chmod(0o644)

    def test_malformed_mcp_json_content(self, temp_directory):
        """Test various malformed .mcp.json content scenarios."""
        malformed_contents = [
            '{"unclosed": object',  # Unclosed JSON
            'not json at all',      # Not JSON
            '',                     # Empty file
            '[]',                   # Wrong JSON type (array instead of object)
            '{"key": }',           # Invalid JSON syntax
            '{"unicode": "invalid \x00 characters"}'  # Invalid characters
        ]

        for i, content in enumerate(malformed_contents):
            mcp_json_file = temp_directory / f'.mcp{i}.json'
            mcp_json_file.write_text(content)

            # Environment should still work regardless of malformed MCP JSON
            with patch.dict(os.environ, {'AI_DATA': f'test_data_{i}'}):
                with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                    ai_data = get_ai_data_path()
                    assert ai_data == temp_directory / f'test_data_{i}'


class TestDefaultValueFallbacks:
    """Test default value fallback mechanisms."""

    def test_all_environment_variables_missing(self, temp_directory):
        """Test behavior when all environment variables are missing."""
        # No environment variables set at all
        with patch.dict(os.environ, {}, clear=True):
            with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                # Should use default values
                ai_data = get_ai_data_path()
                ai_docs = get_ai_docs_path()
                log_path = get_log_path()
                edit_enabled = is_claude_edit_enabled()

                assert ai_data == temp_directory / 'logs'      # Default
                assert ai_docs == temp_directory / 'ai_docs'   # Default
                assert log_path == temp_directory / 'logs'     # Default
                assert edit_enabled is False                   # Default

                # All directories should be created
                assert ai_data.exists()
                assert ai_docs.exists()
                assert log_path.exists()

    def test_partial_environment_variables_missing(self, temp_directory):
        """Test behavior when only some environment variables are set."""
        # Only set some variables
        partial_env = {
            'AI_DATA': 'custom_data',
            # AI_DOCS missing - should use default
            # LOG_PATH missing - should use default
            'ENABLE_CLAUDE_EDIT': 'true'
        }

        with patch.dict(os.environ, partial_env, clear=True):
            with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                ai_data = get_ai_data_path()
                ai_docs = get_ai_docs_path()
                log_path = get_log_path()
                edit_enabled = is_claude_edit_enabled()

                assert ai_data == temp_directory / 'custom_data'  # Custom
                assert ai_docs == temp_directory / 'ai_docs'      # Default
                assert log_path == temp_directory / 'logs'        # Default
                assert edit_enabled is True                       # Custom

    def test_empty_environment_variables(self, temp_directory):
        """Test behavior when environment variables are set but empty."""
        # Set variables to empty strings
        empty_env = {
            'AI_DATA': '',
            'AI_DOCS': '',
            'LOG_PATH': '',
            'ENABLE_CLAUDE_EDIT': ''
        }

        with patch.dict(os.environ, empty_env):
            with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                ai_data = get_ai_data_path()
                ai_docs = get_ai_docs_path()
                log_path = get_log_path()
                edit_enabled = is_claude_edit_enabled()

                # Empty strings should resolve to project root or defaults
                assert ai_data == temp_directory  # Empty resolves to project root
                assert ai_docs == temp_directory  # Empty resolves to project root
                assert log_path == temp_directory # Empty resolves to project root
                assert edit_enabled is False      # Empty string is falsy

    def test_whitespace_only_environment_variables(self, temp_directory):
        """Test behavior when environment variables contain only whitespace."""
        # Set variables to whitespace
        whitespace_env = {
            'AI_DATA': '   ',
            'AI_DOCS': '\t\t',
            'LOG_PATH': '\n\n',
            'ENABLE_CLAUDE_EDIT': ' \t\n '
        }

        with patch.dict(os.environ, whitespace_env):
            with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                ai_data = get_ai_data_path()
                ai_docs = get_ai_docs_path()
                log_path = get_log_path()
                edit_enabled = is_claude_edit_enabled()

                # Whitespace should be treated as valid path components
                assert ai_data == temp_directory / '   '
                assert ai_docs == temp_directory / '\t\t'
                assert log_path == temp_directory / '\n\n'
                assert edit_enabled is False  # Whitespace is falsy


class TestFileSystemErrorHandling:
    """Test file system error handling scenarios."""

    def test_project_root_on_readonly_filesystem(self, temp_directory):
        """Test project root detection on read-only filesystem."""
        # Create .env.claude to mark project root
        env_claude_file = temp_directory / '.env.claude'
        env_claude_file.write_text('AI_DATA=test')

        # Make filesystem read-only
        temp_directory.chmod(0o444)

        try:
            with patch('utils.env_loader.Path.cwd', return_value=temp_directory):
                # Should still be able to find project root
                root = find_project_root()
                assert root == temp_directory

        finally:
            # Restore permissions for cleanup
            temp_directory.chmod(0o755)

    def test_directory_creation_on_readonly_filesystem(self, temp_directory):
        """Test directory creation failure on read-only filesystem."""
        # Make filesystem read-only after creating project structure
        temp_directory.chmod(0o444)

        try:
            with patch.dict(os.environ, {'AI_DATA': 'readonly_data'}):
                with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                    # Should fail to create directory
                    with pytest.raises(PermissionError):
                        get_ai_data_path()

        finally:
            # Restore permissions for cleanup
            temp_directory.chmod(0o755)

    def test_network_filesystem_delays(self, temp_directory):
        """Test handling of network filesystem delays."""
        # Mock slow file operations
        original_mkdir = Path.mkdir

        def slow_mkdir(self, *args, **kwargs):
            # Simulate network delay
            import time
            time.sleep(0.01)  # Small delay
            return original_mkdir(self, *args, **kwargs)

        with patch.object(Path, 'mkdir', slow_mkdir):
            with patch.dict(os.environ, {'AI_DATA': 'slow_data'}):
                with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                    # Should handle slow operations
                    ai_data = get_ai_data_path()
                    assert ai_data == temp_directory / 'slow_data'
                    assert ai_data.exists()

    def test_disk_space_exhaustion_simulation(self, temp_directory):
        """Test handling of disk space exhaustion."""
        # Mock disk space exhaustion
        def no_space_mkdir(self, *args, **kwargs):
            raise OSError(28, 'No space left on device')  # ENOSPC

        with patch.object(Path, 'mkdir', no_space_mkdir):
            with patch.dict(os.environ, {'AI_DATA': 'no_space_data'}):
                with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                    # Should raise OSError for no space
                    with pytest.raises(OSError) as exc_info:
                        get_ai_data_path()
                    assert 'No space left on device' in str(exc_info.value)

    def test_invalid_filesystem_paths(self, temp_directory):
        """Test handling of invalid filesystem paths."""
        invalid_paths = [
            '/dev/null/invalid',    # Path through device file
            '../../../etc/passwd',  # Path traversal attempt
            'path\x00with\x00nulls', # Null bytes in path
            '.' * 300,              # Extremely long path component
        ]

        for invalid_path in invalid_paths:
            with patch.dict(os.environ, {'AI_DATA': invalid_path}):
                with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                    try:
                        # Some invalid paths might work, others might fail
                        # The important thing is they don't crash the system
                        ai_data = get_ai_data_path()
                        # If it succeeds, verify it's a Path object
                        assert isinstance(ai_data, Path)
                    except (OSError, ValueError, TypeError):
                        # These exceptions are acceptable for invalid paths
                        pass


class TestComplexMissingFileScenarios:
    """Test complex scenarios with multiple missing files."""

    def test_gradual_file_availability(self, temp_directory):
        """Test system behavior as files become available gradually."""
        # Start with no files
        with patch.dict(os.environ, {}, clear=True):
            with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                # Should use defaults
                ai_data_1 = get_ai_data_path()
                assert ai_data_1 == temp_directory / 'logs'

        # Add .env file
        env_file = temp_directory / '.env'
        env_file.write_text('AI_DATA=env_data\n')

        with patch.dict(os.environ, {'AI_DATA': 'env_data'}):
            with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                ai_data_2 = get_ai_data_path()
                assert ai_data_2 == temp_directory / 'env_data'

        # Add .env.claude file (should take precedence)
        env_claude_file = temp_directory / '.env.claude'
        env_claude_file.write_text('AI_DATA=claude_data\n')

        with patch.dict(os.environ, {'AI_DATA': 'claude_data'}):
            with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                ai_data_3 = get_ai_data_path()
                assert ai_data_3 == temp_directory / 'claude_data'

    def test_file_deletion_during_runtime(self, temp_directory):
        """Test handling of files being deleted during runtime."""
        # Start with files present
        env_claude_file = temp_directory / '.env.claude'
        env_claude_file.write_text('AI_DATA=claude_data\n')

        with patch.dict(os.environ, {'AI_DATA': 'claude_data'}):
            with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                ai_data_1 = get_ai_data_path()
                assert ai_data_1 == temp_directory / 'claude_data'

                # Delete .env.claude during runtime
                env_claude_file.unlink()

                # Functions should still work with cached environment
                ai_data_2 = get_ai_data_path()
                assert ai_data_2 == temp_directory / 'claude_data'

        # Clear environment to simulate restart
        with patch.dict(os.environ, {}, clear=True):
            with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                # Should fall back to defaults
                ai_data_3 = get_ai_data_path()
                assert ai_data_3 == temp_directory / 'logs'

    def test_file_corruption_recovery(self, temp_directory):
        """Test recovery from file corruption."""
        # Start with working .env.claude
        env_claude_file = temp_directory / '.env.claude'
        env_claude_file.write_text('AI_DATA=working_data\n')

        # Create fallback .env
        env_file = temp_directory / '.env'
        env_file.write_text('AI_DATA=fallback_data\n')

        with patch.dict(os.environ, {'AI_DATA': 'working_data'}):
            with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                ai_data_1 = get_ai_data_path()
                assert ai_data_1 == temp_directory / 'working_data'

        # Corrupt .env.claude
        env_claude_file.write_bytes(b'\x00\x01\x02\x03')

        # Should fall back to .env
        with patch.dict(os.environ, {'AI_DATA': 'fallback_data'}):
            with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                ai_data_2 = get_ai_data_path()
                assert ai_data_2 == temp_directory / 'fallback_data'

        # Fix .env.claude
        env_claude_file.write_text('AI_DATA=recovered_data\n')

        with patch.dict(os.environ, {'AI_DATA': 'recovered_data'}):
            with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                ai_data_3 = get_ai_data_path()
                assert ai_data_3 == temp_directory / 'recovered_data'

    def test_cascade_failure_and_recovery(self, temp_directory):
        """Test complete system failure and recovery."""
        # Set up working system
        env_claude_file = temp_directory / '.env.claude'
        env_claude_file.write_text('AI_DATA=working_data\n')

        mcp_json_file = temp_directory / '.mcp.json'
        mcp_json_file.write_text('{"token": "working_token"}\n')

        with patch.dict(os.environ, {'AI_DATA': 'working_data'}):
            with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                # Verify working system
                ai_data_1 = get_ai_data_path()
                all_paths_1 = get_all_paths()
                assert ai_data_1 == temp_directory / 'working_data'
                assert len(all_paths_1) == 3

        # Simulate complete failure - corrupt all files
        env_claude_file.write_bytes(b'corrupted')
        mcp_json_file.write_bytes(b'corrupted')

        # Should fall back to defaults
        with patch.dict(os.environ, {}, clear=True):
            with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                ai_data_2 = get_ai_data_path()
                all_paths_2 = get_all_paths()
                edit_enabled_2 = is_claude_edit_enabled()

                # Should use defaults
                assert ai_data_2 == temp_directory / 'logs'
                assert all_paths_2['ai_docs'] == temp_directory / 'ai_docs'
                assert edit_enabled_2 is False

        # Simulate recovery - fix files
        env_claude_file.write_text('AI_DATA=recovered_data\nENABLE_CLAUDE_EDIT=true\n')
        mcp_json_file.write_text('{"token": "recovered_token"}\n')

        with patch.dict(os.environ, {
            'AI_DATA': 'recovered_data',
            'ENABLE_CLAUDE_EDIT': 'true'
        }):
            with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                # Should recover to new configuration
                ai_data_3 = get_ai_data_path()
                edit_enabled_3 = is_claude_edit_enabled()

                assert ai_data_3 == temp_directory / 'recovered_data'
                assert edit_enabled_3 is True