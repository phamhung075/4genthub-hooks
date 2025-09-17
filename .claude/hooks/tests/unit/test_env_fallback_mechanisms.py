"""
Unit tests for environment variable fallback mechanisms.

Tests cover:
- Environment variable precedence and fallback chains
- Default value resolution when variables are missing
- Validation of fallback behavior across different scenarios
- Edge cases in environment variable processing
- Priority handling between different configuration sources
"""

import os
import pytest
import sys
from pathlib import Path
from unittest.mock import patch

# Add hooks directory to Python path
hooks_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(hooks_dir))

from utils.env_loader import (
    get_ai_data_path,
    get_ai_docs_path,
    get_log_path,
    get_all_paths,
    is_claude_edit_enabled
)


class TestEnvironmentVariablePrecedence:
    """Test environment variable precedence and override behavior."""

    def test_env_variable_overrides_default(self, temp_directory):
        """Test that environment variables override default values."""
        custom_values = {
            'AI_DATA': 'custom_ai_data',
            'AI_DOCS': 'custom_ai_docs',
            'LOG_PATH': 'custom_log_path',
            'ENABLE_CLAUDE_EDIT': 'true'
        }

        with patch.dict(os.environ, custom_values):
            with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                ai_data = get_ai_data_path()
                ai_docs = get_ai_docs_path()
                log_path = get_log_path()
                edit_enabled = is_claude_edit_enabled()

                # Should use custom values, not defaults
                assert ai_data == temp_directory / 'custom_ai_data'
                assert ai_docs == temp_directory / 'custom_ai_docs'
                assert log_path == temp_directory / 'custom_log_path'
                assert edit_enabled is True

    def test_partial_overrides_with_defaults(self, temp_directory):
        """Test mixing custom environment variables with defaults."""
        partial_env = {
            'AI_DATA': 'custom_data',
            # AI_DOCS not set - should use default
            'LOG_PATH': 'custom_logs',
            # ENABLE_CLAUDE_EDIT not set - should use default
        }

        with patch.dict(os.environ, partial_env, clear=True):
            with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                ai_data = get_ai_data_path()
                ai_docs = get_ai_docs_path()
                log_path = get_log_path()
                edit_enabled = is_claude_edit_enabled()

                # Custom values should be used
                assert ai_data == temp_directory / 'custom_data'
                assert log_path == temp_directory / 'custom_logs'

                # Defaults should be used for missing variables
                assert ai_docs == temp_directory / 'ai_docs'  # Default
                assert edit_enabled is False  # Default

    def test_environment_variable_case_sensitivity(self, temp_directory):
        """Test that environment variable names are case-sensitive."""
        # Try different cases
        case_variations = {
            'ai_data': 'lowercase_data',      # Wrong case
            'AI_data': 'mixed_case_data',     # Wrong case
            'Ai_Data': 'title_case_data',     # Wrong case
            'AI_DATA': 'correct_case_data'    # Correct case
        }

        with patch.dict(os.environ, case_variations):
            with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                ai_data = get_ai_data_path()

                # Only the correctly cased variable should be used
                assert ai_data == temp_directory / 'correct_case_data'

    def test_environment_variable_value_precedence(self, temp_directory):
        """Test that last set environment variable value takes precedence."""
        with patch.dict(os.environ, {'AI_DATA': 'first_value'}):
            with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                ai_data_1 = get_ai_data_path()
                assert ai_data_1 == temp_directory / 'first_value'

        # Update environment variable
        with patch.dict(os.environ, {'AI_DATA': 'second_value'}):
            with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                ai_data_2 = get_ai_data_path()
                assert ai_data_2 == temp_directory / 'second_value'


class TestDefaultValueResolution:
    """Test default value resolution when environment variables are missing."""

    def test_all_defaults_when_no_env_vars(self, temp_directory):
        """Test that all default values are used when no environment variables are set."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                ai_data = get_ai_data_path()
                ai_docs = get_ai_docs_path()
                log_path = get_log_path()
                edit_enabled = is_claude_edit_enabled()

                # All should use default values
                assert ai_data == temp_directory / 'logs'      # Default for AI_DATA
                assert ai_docs == temp_directory / 'ai_docs'   # Default for AI_DOCS
                assert log_path == temp_directory / 'logs'     # Default for LOG_PATH
                assert edit_enabled is False                   # Default for ENABLE_CLAUDE_EDIT

    def test_default_values_consistency(self, temp_directory):
        """Test that default values are consistent across multiple calls."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                # Call functions multiple times
                ai_data_calls = [get_ai_data_path() for _ in range(3)]
                ai_docs_calls = [get_ai_docs_path() for _ in range(3)]
                log_path_calls = [get_log_path() for _ in range(3)]
                edit_enabled_calls = [is_claude_edit_enabled() for _ in range(3)]

                # All calls should return the same values
                assert all(path == temp_directory / 'logs' for path in ai_data_calls)
                assert all(path == temp_directory / 'ai_docs' for path in ai_docs_calls)
                assert all(path == temp_directory / 'logs' for path in log_path_calls)
                assert all(enabled is False for enabled in edit_enabled_calls)

    def test_default_value_types(self, temp_directory):
        """Test that default values have correct types."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                ai_data = get_ai_data_path()
                ai_docs = get_ai_docs_path()
                log_path = get_log_path()
                edit_enabled = is_claude_edit_enabled()

                # Path functions should return Path objects
                assert isinstance(ai_data, Path)
                assert isinstance(ai_docs, Path)
                assert isinstance(log_path, Path)

                # Boolean function should return boolean
                assert isinstance(edit_enabled, bool)

    def test_get_all_paths_default_structure(self, temp_directory):
        """Test that get_all_paths returns correct structure with defaults."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                all_paths = get_all_paths()

                # Should be a dictionary with expected keys
                assert isinstance(all_paths, dict)
                assert set(all_paths.keys()) == {'ai_data', 'ai_docs', 'log_path'}

                # All values should be Path objects with default values
                assert all_paths['ai_data'] == temp_directory / 'logs'
                assert all_paths['ai_docs'] == temp_directory / 'ai_docs'
                assert all_paths['log_path'] == temp_directory / 'logs'


class TestFallbackChainBehavior:
    """Test the complete fallback chain behavior."""

    def test_complete_fallback_chain_simulation(self, temp_directory):
        """Test complete fallback chain from custom to defaults."""
        # Stage 1: Full custom configuration
        full_custom = {
            'AI_DATA': 'stage1_data',
            'AI_DOCS': 'stage1_docs',
            'LOG_PATH': 'stage1_logs',
            'ENABLE_CLAUDE_EDIT': 'true'
        }

        with patch.dict(os.environ, full_custom):
            with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                stage1_paths = get_all_paths()
                stage1_edit = is_claude_edit_enabled()

                assert stage1_paths['ai_data'] == temp_directory / 'stage1_data'
                assert stage1_paths['ai_docs'] == temp_directory / 'stage1_docs'
                assert stage1_paths['log_path'] == temp_directory / 'stage1_logs'
                assert stage1_edit is True

        # Stage 2: Partial custom configuration
        partial_custom = {
            'AI_DATA': 'stage2_data',
            'ENABLE_CLAUDE_EDIT': 'false'
            # AI_DOCS and LOG_PATH missing
        }

        with patch.dict(os.environ, partial_custom, clear=True):
            with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                stage2_paths = get_all_paths()
                stage2_edit = is_claude_edit_enabled()

                assert stage2_paths['ai_data'] == temp_directory / 'stage2_data'  # Custom
                assert stage2_paths['ai_docs'] == temp_directory / 'ai_docs'      # Default
                assert stage2_paths['log_path'] == temp_directory / 'logs'        # Default
                assert stage2_edit is False  # Custom

        # Stage 3: No custom configuration (all defaults)
        with patch.dict(os.environ, {}, clear=True):
            with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                stage3_paths = get_all_paths()
                stage3_edit = is_claude_edit_enabled()

                assert stage3_paths['ai_data'] == temp_directory / 'logs'      # Default
                assert stage3_paths['ai_docs'] == temp_directory / 'ai_docs'   # Default
                assert stage3_paths['log_path'] == temp_directory / 'logs'     # Default
                assert stage3_edit is False  # Default

    def test_fallback_with_invalid_values(self, temp_directory):
        """Test fallback behavior with invalid environment variable values."""
        # Test with various invalid/edge case values
        invalid_values = {
            'AI_DATA': '',           # Empty string
            'AI_DOCS': '   ',        # Whitespace only
            'LOG_PATH': '\n\t',      # Whitespace characters
            'ENABLE_CLAUDE_EDIT': 'maybe'  # Invalid boolean
        }

        with patch.dict(os.environ, invalid_values):
            with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                ai_data = get_ai_data_path()
                ai_docs = get_ai_docs_path()
                log_path = get_log_path()
                edit_enabled = is_claude_edit_enabled()

                # Empty string should resolve to project root
                assert ai_data == temp_directory

                # Whitespace should be treated as valid path components
                assert ai_docs == temp_directory / '   '
                assert log_path == temp_directory / '\n\t'

                # Invalid boolean should be falsy
                assert edit_enabled is False

    def test_fallback_with_none_values(self, temp_directory):
        """Test behavior when environment variables are set to None-like values."""
        # Note: os.environ can't actually contain None values, but we can test
        # the getenv behavior with default values
        with patch('os.getenv') as mock_getenv:
            def getenv_side_effect(key, default=None):
                if key == 'AI_DATA':
                    return None  # Simulate missing variable
                elif key == 'AI_DOCS':
                    return default  # Use provided default
                elif key == 'LOG_PATH':
                    return 'custom_logs'  # Valid value
                elif key == 'ENABLE_CLAUDE_EDIT':
                    return None  # Simulate missing variable
                return default

            mock_getenv.side_effect = getenv_side_effect

            with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                ai_data = get_ai_data_path()
                ai_docs = get_ai_docs_path()
                log_path = get_log_path()
                edit_enabled = is_claude_edit_enabled()

                # None should trigger default behavior
                assert ai_data == temp_directory / 'logs'      # Default
                assert ai_docs == temp_directory / 'ai_docs'   # Default
                assert log_path == temp_directory / 'custom_logs'  # Custom
                assert edit_enabled is False  # Default


class TestBooleanFallbackBehavior:
    """Test boolean environment variable fallback behavior."""

    @pytest.mark.parametrize("env_value,expected", [
        # Valid true values
        ('true', True),
        ('TRUE', True),
        ('True', True),
        ('1', True),
        ('yes', True),
        ('YES', True),
        ('Yes', True),
        ('on', True),
        ('ON', True),
        ('On', True),

        # Valid false values
        ('false', False),
        ('FALSE', False),
        ('False', False),
        ('0', False),
        ('no', False),
        ('NO', False),
        ('No', False),
        ('off', False),
        ('OFF', False),
        ('Off', False),

        # Invalid/edge case values (should be falsy)
        ('', False),
        ('invalid', False),
        ('maybe', False),
        ('2', False),
        ('-1', False),
        ('TRUE_BUT_NOT_RECOGNIZED', False),
        ('yes please', False),
        ('true false', False),
    ])
    def test_boolean_environment_variable_parsing(self, env_value, expected):
        """Test parsing of boolean environment variables."""
        with patch.dict(os.environ, {'ENABLE_CLAUDE_EDIT': env_value}):
            result = is_claude_edit_enabled()
            assert result == expected

    def test_boolean_environment_variable_missing(self):
        """Test boolean environment variable when missing."""
        with patch.dict(os.environ, {}, clear=True):
            result = is_claude_edit_enabled()
            assert result is False  # Should default to False

    def test_boolean_environment_variable_case_insensitive(self):
        """Test that boolean parsing is case-insensitive for recognized values."""
        case_variations = [
            ('true', True),
            ('TRUE', True),
            ('True', True),
            ('tRuE', True),
            ('yes', True),
            ('YES', True),
            ('Yes', True),
            ('yEs', True),
        ]

        for env_value, expected in case_variations:
            with patch.dict(os.environ, {'ENABLE_CLAUDE_EDIT': env_value}):
                result = is_claude_edit_enabled()
                assert result == expected


class TestPathResolutionFallbacks:
    """Test path resolution fallback mechanisms."""

    def test_relative_path_fallback_to_absolute(self, temp_directory):
        """Test that relative paths are resolved relative to project root."""
        relative_paths = {
            'AI_DATA': 'relative/data/path',
            'AI_DOCS': '../docs',
            'LOG_PATH': './logs/app'
        }

        with patch.dict(os.environ, relative_paths):
            with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                ai_data = get_ai_data_path()
                ai_docs = get_ai_docs_path()
                log_path = get_log_path()

                # All should be resolved relative to project root
                assert ai_data == temp_directory / 'relative/data/path'
                assert ai_docs == temp_directory / '../docs'
                assert log_path == temp_directory / './logs/app'

                # All should be absolute paths
                assert ai_data.is_absolute()
                assert ai_docs.is_absolute()
                assert log_path.is_absolute()

    def test_absolute_path_no_fallback(self, temp_directory):
        """Test that absolute paths are used as-is without fallback."""
        absolute_paths = {
            'AI_DATA': '/absolute/data/path',
            'AI_DOCS': '/home/user/docs',
            'LOG_PATH': '/var/log/app'
        }

        with patch.dict(os.environ, absolute_paths):
            with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                ai_data = get_ai_data_path()
                ai_docs = get_ai_docs_path()
                log_path = get_log_path()

                # Should use absolute paths exactly as provided
                assert str(ai_data) == '/absolute/data/path'
                assert str(ai_docs) == '/home/user/docs'
                assert str(log_path) == '/var/log/app'

    def test_mixed_path_types_fallback(self, temp_directory):
        """Test mixing absolute and relative paths."""
        mixed_paths = {
            'AI_DATA': '/absolute/data',     # Absolute
            'AI_DOCS': 'relative/docs',      # Relative
            'LOG_PATH': './local/logs'       # Relative with current dir
        }

        with patch.dict(os.environ, mixed_paths):
            with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                ai_data = get_ai_data_path()
                ai_docs = get_ai_docs_path()
                log_path = get_log_path()

                # Absolute should remain absolute
                assert str(ai_data) == '/absolute/data'

                # Relative should be resolved to project root
                assert ai_docs == temp_directory / 'relative/docs'
                assert log_path == temp_directory / './local/logs'

    def test_special_path_characters_fallback(self, temp_directory):
        """Test handling of special characters in paths."""
        special_paths = {
            'AI_DATA': 'path with spaces',
            'AI_DOCS': 'path-with-dashes_and_underscores',
            'LOG_PATH': 'path.with.dots'
        }

        with patch.dict(os.environ, special_paths):
            with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                ai_data = get_ai_data_path()
                ai_docs = get_ai_docs_path()
                log_path = get_log_path()

                # Should handle special characters correctly
                assert ai_data == temp_directory / 'path with spaces'
                assert ai_docs == temp_directory / 'path-with-dashes_and_underscores'
                assert log_path == temp_directory / 'path.with.dots'

                # All directories should be created successfully
                assert ai_data.exists()
                assert ai_docs.exists()
                assert log_path.exists()


class TestEdgeCaseFallbacks:
    """Test edge case fallback scenarios."""

    def test_extremely_long_environment_values(self, temp_directory):
        """Test handling of extremely long environment variable values."""
        # Create very long path names
        long_path = 'very' + '_long' * 100 + '_path'
        long_env = {
            'AI_DATA': long_path,
            'ENABLE_CLAUDE_EDIT': 'true' * 50  # Long boolean value
        }

        with patch.dict(os.environ, long_env):
            with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                ai_data = get_ai_data_path()
                edit_enabled = is_claude_edit_enabled()

                # Should handle long paths
                assert ai_data == temp_directory / long_path

                # Long boolean value should still be parsed correctly
                assert edit_enabled is True

    def test_unicode_environment_values(self, temp_directory):
        """Test handling of Unicode characters in environment variables."""
        unicode_paths = {
            'AI_DATA': 'data_世界',
            'AI_DOCS': 'docs_🌍',
            'LOG_PATH': 'logs_café'
        }

        with patch.dict(os.environ, unicode_paths):
            with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                ai_data = get_ai_data_path()
                ai_docs = get_ai_docs_path()
                log_path = get_log_path()

                # Should handle Unicode correctly
                assert ai_data == temp_directory / 'data_世界'
                assert ai_docs == temp_directory / 'docs_🌍'
                assert log_path == temp_directory / 'logs_café'

                # Should be able to create directories with Unicode names
                assert ai_data.exists()
                assert ai_docs.exists()
                assert log_path.exists()

    def test_environment_variable_with_newlines(self, temp_directory):
        """Test handling of environment variables containing newlines."""
        newline_paths = {
            'AI_DATA': 'data\nwith\nnewlines',
            'AI_DOCS': 'docs\twith\ttabs',
            'LOG_PATH': 'logs\r\nwith\r\nwindows\r\nnewlines'
        }

        with patch.dict(os.environ, newline_paths):
            with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                ai_data = get_ai_data_path()
                ai_docs = get_ai_docs_path()
                log_path = get_log_path()

                # Should preserve whitespace characters in paths
                assert ai_data == temp_directory / 'data\nwith\nnewlines'
                assert ai_docs == temp_directory / 'docs\twith\ttabs'
                assert log_path == temp_directory / 'logs\r\nwith\r\nwindows\r\nnewlines'

    def test_recursive_environment_variable_references(self, temp_directory):
        """Test handling of environment variables that might reference others."""
        # Note: Python's os.environ doesn't expand variables automatically
        # but we test that our code doesn't break with such values
        recursive_env = {
            'BASE_PATH': '/base',
            'AI_DATA': '$BASE_PATH/data',  # Shell-style reference
            'AI_DOCS': '${HOME}/docs',     # Shell-style reference
            'LOG_PATH': '%USERPROFILE%\\logs'  # Windows-style reference
        }

        with patch.dict(os.environ, recursive_env):
            with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                ai_data = get_ai_data_path()
                ai_docs = get_ai_docs_path()
                log_path = get_log_path()

                # Should treat these as literal path components (no expansion)
                assert ai_data == temp_directory / '$BASE_PATH/data'
                assert ai_docs == temp_directory / '${HOME}/docs'
                assert log_path == temp_directory / '%USERPROFILE%\\logs'