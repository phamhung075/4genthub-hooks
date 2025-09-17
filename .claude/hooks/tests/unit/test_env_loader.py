"""
Unit tests for environment variable loading and project root detection.

Tests cover:
- Environment variable loading from .env.claude and .env files
- Project root detection algorithms
- Path resolution and directory creation
- Fallback mechanisms and error handling
- Docker vs local environment differences
"""

import os
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, Mock

# Add hooks directory to Python path
import sys
from pathlib import Path
hooks_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(hooks_dir))

# Import the module under test
from utils.env_loader import (
    find_project_root,
    get_ai_data_path,
    get_ai_docs_path,
    get_log_path,
    get_all_paths,
    is_claude_edit_enabled,
    get_project_root,
    PROJECT_ROOT,
    ENV_CLAUDE_PATH
)


class TestProjectRootDetection:
    """Test project root detection functionality."""

    def test_find_project_root_with_env_claude(self, temp_directory):
        """Test finding project root when .env.claude exists."""
        # Create .env.claude file
        env_claude_file = temp_directory / '.env.claude'
        env_claude_file.write_text('AI_DATA=test_data\n')

        with patch('pathlib.Path.cwd', return_value=temp_directory / 'subdir'):
            # Create subdirectory to test upward search
            (temp_directory / 'subdir').mkdir()

            # Mock the function to use our temp directory
            with patch('utils.env_loader.Path.cwd', return_value=temp_directory / 'subdir'):
                root = find_project_root()
                assert root == temp_directory

    def test_find_project_root_with_git(self, temp_directory):
        """Test finding project root when .git directory exists."""
        # Create .git directory
        git_dir = temp_directory / '.git'
        git_dir.mkdir()

        with patch('pathlib.Path.cwd', return_value=temp_directory / 'deep' / 'subdir'):
            # Create deep subdirectory
            (temp_directory / 'deep' / 'subdir').mkdir(parents=True)

            with patch('utils.env_loader.Path.cwd', return_value=temp_directory / 'deep' / 'subdir'):
                from utils.env_loader import find_project_root
                root = find_project_root()
                assert root == temp_directory

    def test_find_project_root_fallback_to_current(self, temp_directory):
        """Test fallback to current directory when no markers found."""
        # No .env.claude or .git directory
        current_dir = temp_directory / 'isolated'
        current_dir.mkdir()

        with patch('pathlib.Path.cwd', return_value=current_dir):
            with patch('utils.env_loader.Path.cwd', return_value=current_dir):
                from utils.env_loader import find_project_root
                root = find_project_root()
                assert root == current_dir

    def test_get_project_root_cached(self):
        """Test that get_project_root returns cached PROJECT_ROOT."""
        # This should return the cached value set at module import
        root = get_project_root()
        assert root == PROJECT_ROOT
        assert isinstance(root, Path)


class TestEnvironmentVariableLoading:
    """Test environment variable loading from different sources."""

    def test_env_claude_loading_with_dotenv(self, temp_directory):
        """Test loading variables from .env.claude file."""
        env_claude_file = temp_directory / '.env.claude'
        env_claude_file.write_text("""
AI_DATA=custom_ai_data
AI_DOCS=custom_ai_docs
LOG_PATH=custom_logs
ENABLE_CLAUDE_EDIT=true
""")

        # Mock the dotenv loading
        with patch('utils.env_loader.load_dotenv') as mock_load_dotenv:
            with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                with patch('utils.env_loader.ENV_CLAUDE_PATH', env_claude_file):
                    # Reload the module to trigger the loading logic
                    import importlib
                    import utils.env_loader
                    importlib.reload(utils.env_loader)

                    mock_load_dotenv.assert_called_with(env_claude_file)

    def test_env_fallback_loading(self, temp_directory):
        """Test fallback to .env when .env.claude doesn't exist."""
        env_file = temp_directory / '.env'
        env_file.write_text("""
AI_DATA=fallback_ai_data
AI_DOCS=fallback_ai_docs
""")

        # No .env.claude file exists
        with patch('utils.env_loader.load_dotenv') as mock_load_dotenv:
            with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                with patch('utils.env_loader.ENV_CLAUDE_PATH', temp_directory / '.env.claude'):
                    import importlib
                    import utils.env_loader
                    importlib.reload(utils.env_loader)

                    mock_load_dotenv.assert_called_with(env_file)

    def test_no_env_files_present(self, temp_directory):
        """Test behavior when neither .env.claude nor .env exist."""
        # No env files exist
        with patch('utils.env_loader.load_dotenv') as mock_load_dotenv:
            with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                with patch('utils.env_loader.ENV_CLAUDE_PATH', temp_directory / '.env.claude'):
                    import importlib
                    import utils.env_loader
                    importlib.reload(utils.env_loader)

                    # load_dotenv should not be called
                    mock_load_dotenv.assert_not_called()


class TestPathResolution:
    """Test path resolution and directory creation functionality."""

    def test_get_ai_data_path_default(self, temp_directory):
        """Test get_ai_data_path with default value."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                path = get_ai_data_path()

                assert path == temp_directory / 'logs'
                assert path.exists()  # Should be created

    def test_get_ai_data_path_custom_relative(self, temp_directory):
        """Test get_ai_data_path with custom relative path."""
        with patch.dict(os.environ, {'AI_DATA': 'custom_data'}):
            with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                path = get_ai_data_path()

                assert path == temp_directory / 'custom_data'
                assert path.exists()  # Should be created

    def test_get_ai_data_path_custom_absolute(self, temp_directory):
        """Test get_ai_data_path with custom absolute path."""
        absolute_path = temp_directory / 'absolute_ai_data'

        with patch.dict(os.environ, {'AI_DATA': str(absolute_path)}):
            path = get_ai_data_path()

            assert path == absolute_path
            assert path.exists()  # Should be created

    def test_get_ai_docs_path_default(self, temp_directory):
        """Test get_ai_docs_path with default value."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                path = get_ai_docs_path()

                assert path == temp_directory / 'ai_docs'
                assert path.exists()  # Should be created

    def test_get_ai_docs_path_custom(self, temp_directory):
        """Test get_ai_docs_path with custom path."""
        with patch.dict(os.environ, {'AI_DOCS': 'custom_docs'}):
            with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                path = get_ai_docs_path()

                assert path == temp_directory / 'custom_docs'
                assert path.exists()  # Should be created

    def test_get_log_path_default(self, temp_directory):
        """Test get_log_path with default value."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                path = get_log_path()

                assert path == temp_directory / 'logs'
                assert path.exists()  # Should be created

    def test_get_log_path_custom(self, temp_directory):
        """Test get_log_path with custom path."""
        with patch.dict(os.environ, {'LOG_PATH': 'custom_logs'}):
            with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                path = get_log_path()

                assert path == temp_directory / 'custom_logs'
                assert path.exists()  # Should be created

    def test_path_creation_failure(self, temp_directory):
        """Test handling of path creation failures."""
        # Create a file where we want to create a directory
        blocking_file = temp_directory / 'blocking_file'
        blocking_file.write_text('blocking content')

        with patch.dict(os.environ, {'AI_DATA': 'blocking_file'}):
            with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                # This should raise an exception due to file blocking directory creation
                with pytest.raises(FileExistsError):
                    get_ai_data_path()


class TestGetAllPaths:
    """Test the get_all_paths convenience function."""

    def test_get_all_paths_structure(self, temp_directory):
        """Test that get_all_paths returns correct structure."""
        with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
            paths = get_all_paths()

            assert isinstance(paths, dict)
            assert 'ai_data' in paths
            assert 'ai_docs' in paths
            assert 'log_path' in paths

            # All should be Path objects
            assert isinstance(paths['ai_data'], Path)
            assert isinstance(paths['ai_docs'], Path)
            assert isinstance(paths['log_path'], Path)

    def test_get_all_paths_custom_values(self, temp_directory):
        """Test get_all_paths with custom environment values."""
        env_vars = {
            'AI_DATA': 'custom_ai_data',
            'AI_DOCS': 'custom_ai_docs',
            'LOG_PATH': 'custom_log_path'
        }

        with patch.dict(os.environ, env_vars):
            with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                paths = get_all_paths()

                assert paths['ai_data'] == temp_directory / 'custom_ai_data'
                assert paths['ai_docs'] == temp_directory / 'custom_ai_docs'
                assert paths['log_path'] == temp_directory / 'custom_log_path'

                # All directories should exist
                assert paths['ai_data'].exists()
                assert paths['ai_docs'].exists()
                assert paths['log_path'].exists()


class TestClaudeEditEnabled:
    """Test the Claude edit enabled functionality."""

    @pytest.mark.parametrize("env_value,expected", [
        ('true', True),
        ('TRUE', True),
        ('True', True),
        ('1', True),
        ('yes', True),
        ('YES', True),
        ('on', True),
        ('ON', True),
        ('false', False),
        ('FALSE', False),
        ('0', False),
        ('no', False),
        ('off', False),
        ('invalid', False),
        ('', False),
    ])
    def test_is_claude_edit_enabled_values(self, env_value, expected):
        """Test is_claude_edit_enabled with various input values."""
        with patch.dict(os.environ, {'ENABLE_CLAUDE_EDIT': env_value}):
            result = is_claude_edit_enabled()
            assert result == expected

    def test_is_claude_edit_enabled_default(self):
        """Test is_claude_edit_enabled with no environment variable set."""
        with patch.dict(os.environ, {}, clear=True):
            result = is_claude_edit_enabled()
            assert result is False


class TestDockerEnvironmentDifferences:
    """Test differences between Docker and local environments."""

    def test_docker_environment_detection(self):
        """Test Docker environment detection via environment variables."""
        docker_env_vars = {
            'DOCKER_CONTAINER': '1',
            'AI_DATA': '/app/data',
            'AI_DOCS': '/app/docs'
        }

        with patch.dict(os.environ, docker_env_vars):
            # In Docker, paths might be absolute
            ai_data = get_ai_data_path()
            ai_docs = get_ai_docs_path()

            # Should handle absolute paths correctly
            assert str(ai_data) == '/app/data'
            assert str(ai_docs) == '/app/docs'

    def test_local_environment_relative_paths(self, temp_directory):
        """Test local environment with relative paths."""
        local_env_vars = {
            'AI_DATA': 'local_data',
            'AI_DOCS': 'local_docs'
        }

        with patch.dict(os.environ, local_env_vars):
            with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                ai_data = get_ai_data_path()
                ai_docs = get_ai_docs_path()

                # Should resolve relative to project root
                assert ai_data == temp_directory / 'local_data'
                assert ai_docs == temp_directory / 'local_docs'

    def test_mixed_absolute_relative_paths(self, temp_directory):
        """Test mixed absolute and relative path configuration."""
        mixed_env_vars = {
            'AI_DATA': '/absolute/path/data',  # Absolute
            'AI_DOCS': 'relative_docs',        # Relative
            'LOG_PATH': '/another/absolute/logs'  # Absolute
        }

        with patch.dict(os.environ, mixed_env_vars):
            with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                ai_data = get_ai_data_path()
                ai_docs = get_ai_docs_path()
                log_path = get_log_path()

                # Absolute paths should remain absolute
                assert str(ai_data) == '/absolute/path/data'
                assert str(log_path) == '/another/absolute/logs'

                # Relative paths should resolve to project root
                assert ai_docs == temp_directory / 'relative_docs'


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_permission_denied_directory_creation(self, temp_directory):
        """Test handling of permission denied during directory creation."""
        # Create a readonly parent directory
        readonly_parent = temp_directory / 'readonly'
        readonly_parent.mkdir()
        readonly_parent.chmod(0o444)  # Read-only

        try:
            with patch.dict(os.environ, {'AI_DATA': 'readonly/subdir'}):
                with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                    # This should raise a PermissionError
                    with pytest.raises(PermissionError):
                        get_ai_data_path()
        finally:
            # Cleanup: restore permissions
            readonly_parent.chmod(0o755)

    def test_path_with_special_characters(self, temp_directory):
        """Test paths with special characters."""
        special_paths = [
            'path with spaces',
            'path-with-dashes',
            'path_with_underscores',
            'path.with.dots'
        ]

        for special_path in special_paths:
            with patch.dict(os.environ, {'AI_DATA': special_path}):
                with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                    path = get_ai_data_path()
                    assert path == temp_directory / special_path
                    assert path.exists()

    def test_very_long_path(self, temp_directory):
        """Test handling of very long paths."""
        # Create a very long path name
        long_name = 'very_' * 50 + 'long_path'

        with patch.dict(os.environ, {'AI_DATA': long_name}):
            with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                path = get_ai_data_path()
                assert path == temp_directory / long_name
                # Should still be able to create it (within filesystem limits)
                assert path.exists()

    def test_empty_environment_variable(self, temp_directory):
        """Test handling of empty environment variables."""
        with patch.dict(os.environ, {'AI_DATA': ''}):
            with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                path = get_ai_data_path()
                # Empty string should resolve to project root
                assert path == temp_directory
                assert path.exists()


class TestModuleReloading:
    """Test module behavior during reloading and imports."""

    def test_module_import_caching(self):
        """Test that PROJECT_ROOT is cached on module import."""
        # The PROJECT_ROOT should be set once at module import
        assert PROJECT_ROOT is not None
        assert isinstance(PROJECT_ROOT, Path)

        # Multiple calls should return the same cached value
        root1 = get_project_root()
        root2 = get_project_root()
        assert root1 == root2
        assert root1 is PROJECT_ROOT

    def test_env_claude_path_setting(self):
        """Test that ENV_CLAUDE_PATH is set correctly on import."""
        assert ENV_CLAUDE_PATH is not None
        assert isinstance(ENV_CLAUDE_PATH, Path)
        assert ENV_CLAUDE_PATH.name == '.env.claude'
        assert ENV_CLAUDE_PATH.parent == PROJECT_ROOT


class TestIntegrationScenarios:
    """Test integration scenarios combining multiple features."""

    def test_complete_configuration_loading(self, temp_directory):
        """Test complete configuration loading scenario."""
        # Create .env.claude with all configuration
        env_claude_content = """
AI_DATA=integration_data
AI_DOCS=integration_docs
LOG_PATH=integration_logs
ENABLE_CLAUDE_EDIT=true
"""
        env_claude_file = temp_directory / '.env.claude'
        env_claude_file.write_text(env_claude_content)

        # Mock environment loading
        with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
            with patch.dict(os.environ, {
                'AI_DATA': 'integration_data',
                'AI_DOCS': 'integration_docs',
                'LOG_PATH': 'integration_logs',
                'ENABLE_CLAUDE_EDIT': 'true'
            }):
                # Test all functions
                ai_data = get_ai_data_path()
                ai_docs = get_ai_docs_path()
                log_path = get_log_path()
                all_paths = get_all_paths()
                edit_enabled = is_claude_edit_enabled()

                # Verify all results
                assert ai_data == temp_directory / 'integration_data'
                assert ai_docs == temp_directory / 'integration_docs'
                assert log_path == temp_directory / 'integration_logs'
                assert edit_enabled is True

                assert all_paths['ai_data'] == ai_data
                assert all_paths['ai_docs'] == ai_docs
                assert all_paths['log_path'] == log_path

                # All directories should exist
                assert ai_data.exists()
                assert ai_docs.exists()
                assert log_path.exists()

    def test_fallback_chain_complete(self, temp_directory):
        """Test complete fallback chain from .env.claude to .env to defaults."""
        # Test scenario 1: .env.claude exists
        env_claude_file = temp_directory / '.env.claude'
        env_claude_file.write_text('AI_DATA=claude_data\n')

        with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
            with patch.dict(os.environ, {'AI_DATA': 'claude_data'}):
                path = get_ai_data_path()
                assert path == temp_directory / 'claude_data'

        # Test scenario 2: Only .env exists
        env_claude_file.unlink()
        env_file = temp_directory / '.env'
        env_file.write_text('AI_DATA=env_data\n')

        with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
            with patch.dict(os.environ, {'AI_DATA': 'env_data'}):
                path = get_ai_data_path()
                assert path == temp_directory / 'env_data'

        # Test scenario 3: No env files, use defaults
        env_file.unlink()

        with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
            with patch.dict(os.environ, {}, clear=True):
                path = get_ai_data_path()
                assert path == temp_directory / 'logs'  # Default value