"""
Unit tests for configuration loading functionality.

Tests cover:
- YAML configuration file loading and parsing
- Configuration caching mechanisms
- Error handling for missing/malformed files
- Specific configuration type loading
- Configuration reloading and cache management
- Global instance management
"""

import pytest
import yaml
import tempfile
from pathlib import Path
from unittest.mock import patch, Mock, mock_open
import logging

# Import the module under test
from config.config_loader import (
    ConfigLoader,
    get_config_loader,
    load_mcp_hints_config,
    load_session_messages_config,
    load_hint_messages_config
)


class TestConfigLoaderInitialization:
    """Test ConfigLoader initialization and setup."""

    def test_config_loader_init(self):
        """Test ConfigLoader initialization."""
        loader = ConfigLoader()

        assert loader.config_dir.name == 'config'
        assert loader.config_dir.is_dir()
        assert loader._cache == {}

    def test_config_dir_resolution(self):
        """Test that config directory is resolved correctly."""
        loader = ConfigLoader()

        # Should be the config directory relative to the config_loader.py file
        expected_config_dir = Path(__file__).parent.parent.parent / 'config'
        assert loader.config_dir == expected_config_dir


class TestConfigFileLoading:
    """Test configuration file loading functionality."""

    def test_load_config_success(self, temp_directory):
        """Test successful configuration loading."""
        # Create a test config file
        config_data = {
            'test_setting': 'test_value',
            'nested': {
                'key': 'value',
                'number': 42
            }
        }

        config_file = temp_directory / 'test_config.yaml'
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)

        # Create loader with custom config directory
        loader = ConfigLoader()
        loader.config_dir = temp_directory

        result = loader.load_config('test_config')

        assert result == config_data
        assert 'test_config' in loader._cache

    def test_load_config_file_not_found(self, temp_directory, caplog):
        """Test loading non-existent configuration file."""
        loader = ConfigLoader()
        loader.config_dir = temp_directory

        with caplog.at_level(logging.WARNING):
            result = loader.load_config('nonexistent_config')

        assert result is None
        assert 'Configuration file not found' in caplog.text

    def test_load_config_invalid_yaml(self, temp_directory, caplog):
        """Test loading configuration file with invalid YAML."""
        # Create invalid YAML file
        config_file = temp_directory / 'invalid_config.yaml'
        config_file.write_text('invalid: yaml: content: [unclosed')

        loader = ConfigLoader()
        loader.config_dir = temp_directory

        with caplog.at_level(logging.ERROR):
            result = loader.load_config('invalid_config')

        assert result is None
        assert 'Error parsing YAML file' in caplog.text

    def test_load_config_file_read_error(self, temp_directory, caplog):
        """Test handling file read errors."""
        loader = ConfigLoader()
        loader.config_dir = temp_directory

        # Create the file so it passes the existence check
        config_file = temp_directory / 'test_config.yaml'
        config_file.write_text('test: value')

        # Mock open to raise an exception
        with patch('builtins.open', side_effect=IOError('Read error')):
            with caplog.at_level(logging.ERROR):
                result = loader.load_config('test_config')

        assert result is None
        assert 'Error loading configuration' in caplog.text

    def test_load_config_empty_file(self, temp_directory):
        """Test loading empty configuration file."""
        config_file = temp_directory / 'empty_config.yaml'
        config_file.write_text('')

        loader = ConfigLoader()
        loader.config_dir = temp_directory

        result = loader.load_config('empty_config')

        assert result is None

    def test_load_config_yaml_comments(self, temp_directory):
        """Test loading YAML file with comments."""
        config_content = """
# This is a comment
test_setting: test_value  # Inline comment
nested:
  # Another comment
  key: value
  number: 42
"""
        config_file = temp_directory / 'commented_config.yaml'
        config_file.write_text(config_content)

        loader = ConfigLoader()
        loader.config_dir = temp_directory

        result = loader.load_config('commented_config')

        expected = {
            'test_setting': 'test_value',
            'nested': {
                'key': 'value',
                'number': 42
            }
        }
        assert result == expected


class TestConfigCaching:
    """Test configuration caching functionality."""

    def test_cache_usage(self, temp_directory):
        """Test that cache is used on subsequent loads."""
        config_data = {'test': 'value'}
        config_file = temp_directory / 'cached_config.yaml'

        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)

        loader = ConfigLoader()
        loader.config_dir = temp_directory

        # First load - should read from file
        result1 = loader.load_config('cached_config')
        assert result1 == config_data
        assert 'cached_config' in loader._cache

        # Modify file content
        new_data = {'modified': 'data'}
        with open(config_file, 'w') as f:
            yaml.dump(new_data, f)

        # Second load with cache enabled - should return cached data
        result2 = loader.load_config('cached_config', use_cache=True)
        assert result2 == config_data  # Should be original, not modified

        # Third load with cache disabled - should read new content
        result3 = loader.load_config('cached_config', use_cache=False)
        assert result3 == new_data  # Should be modified data

    def test_cache_disabled_loading(self, temp_directory):
        """Test loading with caching disabled."""
        config_data = {'test': 'value'}
        config_file = temp_directory / 'no_cache_config.yaml'

        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)

        loader = ConfigLoader()
        loader.config_dir = temp_directory

        # Load with cache disabled
        result = loader.load_config('no_cache_config', use_cache=False)
        assert result == config_data
        assert 'no_cache_config' not in loader._cache

    def test_clear_cache(self, temp_directory):
        """Test cache clearing functionality."""
        config_data = {'test': 'value'}
        config_file = temp_directory / 'cache_clear_config.yaml'

        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)

        loader = ConfigLoader()
        loader.config_dir = temp_directory

        # Load and cache
        loader.load_config('cache_clear_config')
        assert 'cache_clear_config' in loader._cache

        # Clear cache
        loader.clear_cache()
        assert loader._cache == {}

    def test_reload_config(self, temp_directory, caplog):
        """Test force reloading configuration."""
        config_data = {'original': 'value'}
        config_file = temp_directory / 'reload_config.yaml'

        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)

        loader = ConfigLoader()
        loader.config_dir = temp_directory

        # Initial load
        result1 = loader.load_config('reload_config')
        assert result1 == config_data

        # Modify file
        new_data = {'reloaded': 'value'}
        with open(config_file, 'w') as f:
            yaml.dump(new_data, f)

        # Force reload
        with caplog.at_level(logging.DEBUG):
            result2 = loader.reload_config('reload_config')

        assert result2 == new_data
        assert 'Loaded configuration: reload_config' in caplog.text


class TestSpecificConfigurationTypes:
    """Test loading specific configuration types."""

    def test_get_mcp_post_hints_config(self, temp_directory):
        """Test loading MCP post-action hints configuration."""
        hints_config = {
            'hints': [
                {'pattern': 'test', 'message': 'Test hint'}
            ]
        }

        config_file = temp_directory / 'mcp_post_action_hints.yaml'
        with open(config_file, 'w') as f:
            yaml.dump(hints_config, f)

        loader = ConfigLoader()
        loader.config_dir = temp_directory

        result = loader.get_mcp_post_hints_config()
        assert result == hints_config

    def test_get_session_start_config(self, temp_directory):
        """Test loading session start messages configuration."""
        session_config = {
            'messages': [
                {'type': 'welcome', 'text': 'Welcome message'}
            ]
        }

        config_file = temp_directory / 'session_start_messages.yaml'
        with open(config_file, 'w') as f:
            yaml.dump(session_config, f)

        loader = ConfigLoader()
        loader.config_dir = temp_directory

        result = loader.get_session_start_config()
        assert result == session_config

    def test_get_hint_message_config(self, temp_directory):
        """Test loading hint message configuration for specific types."""
        hint_config = {
            'pre_tool_hints': [
                {'condition': 'test', 'message': 'Pre-tool hint'}
            ]
        }

        config_file = temp_directory / '__hint_message__pre_tool_use.yaml'
        with open(config_file, 'w') as f:
            yaml.dump(hint_config, f)

        loader = ConfigLoader()
        loader.config_dir = temp_directory

        result = loader.get_hint_message_config('pre_tool_use')
        assert result == hint_config

    def test_get_nonexistent_specific_config(self, temp_directory):
        """Test loading non-existent specific configuration types."""
        loader = ConfigLoader()
        loader.config_dir = temp_directory

        assert loader.get_mcp_post_hints_config() is None
        assert loader.get_session_start_config() is None
        assert loader.get_hint_message_config('nonexistent') is None


class TestGlobalConfigLoaderInstance:
    """Test global configuration loader instance management."""

    def test_get_config_loader_singleton(self):
        """Test that get_config_loader returns singleton instance."""
        loader1 = get_config_loader()
        loader2 = get_config_loader()

        assert loader1 is loader2
        assert isinstance(loader1, ConfigLoader)

    @patch('config.config_loader._config_loader', None)
    def test_get_config_loader_initialization(self):
        """Test that get_config_loader initializes the global instance."""
        # Reset global instance
        import config.config_loader
        config.config_loader._config_loader = None

        loader = get_config_loader()
        assert loader is not None
        assert isinstance(loader, ConfigLoader)
        assert config.config_loader._config_loader is loader


class TestConvenienceFunctions:
    """Test convenience functions for loading specific configurations."""

    def test_load_mcp_hints_config_convenience(self, temp_directory):
        """Test load_mcp_hints_config convenience function."""
        hints_config = {'test': 'hints'}
        config_file = temp_directory / 'mcp_post_action_hints.yaml'

        with open(config_file, 'w') as f:
            yaml.dump(hints_config, f)

        with patch.object(ConfigLoader, '__init__', lambda self: None):
            with patch.object(ConfigLoader, 'config_dir', temp_directory):
                with patch.object(ConfigLoader, '_cache', {}):
                    with patch.object(ConfigLoader, 'get_mcp_post_hints_config', return_value=hints_config):
                        result = load_mcp_hints_config()
                        assert result == hints_config

    def test_load_session_messages_config_convenience(self, temp_directory):
        """Test load_session_messages_config convenience function."""
        session_config = {'test': 'session'}
        config_file = temp_directory / 'session_start_messages.yaml'

        with open(config_file, 'w') as f:
            yaml.dump(session_config, f)

        with patch.object(ConfigLoader, '__init__', lambda self: None):
            with patch.object(ConfigLoader, 'config_dir', temp_directory):
                with patch.object(ConfigLoader, '_cache', {}):
                    with patch.object(ConfigLoader, 'get_session_start_config', return_value=session_config):
                        result = load_session_messages_config()
                        assert result == session_config

    def test_load_hint_messages_config_convenience(self, temp_directory):
        """Test load_hint_messages_config convenience function."""
        hint_config = {'test': 'hint'}

        with patch.object(ConfigLoader, '__init__', lambda self: None):
            with patch.object(ConfigLoader, 'config_dir', temp_directory):
                with patch.object(ConfigLoader, '_cache', {}):
                    with patch.object(ConfigLoader, 'get_hint_message_config', return_value=hint_config):
                        result = load_hint_messages_config('test_type')
                        assert result == hint_config


class TestComplexConfigurationFiles:
    """Test loading complex configuration files with various YAML features."""

    def test_load_config_with_nested_structures(self, temp_directory):
        """Test loading configuration with deeply nested structures."""
        complex_config = {
            'level1': {
                'level2': {
                    'level3': {
                        'list_items': [
                            {'name': 'item1', 'value': 100},
                            {'name': 'item2', 'value': 200}
                        ],
                        'nested_dict': {
                            'key1': 'value1',
                            'key2': ['a', 'b', 'c']
                        }
                    }
                }
            },
            'root_list': [1, 2, 3, 4, 5]
        }

        config_file = temp_directory / 'complex_config.yaml'
        with open(config_file, 'w') as f:
            yaml.dump(complex_config, f)

        loader = ConfigLoader()
        loader.config_dir = temp_directory

        result = loader.load_config('complex_config')
        assert result == complex_config

    def test_load_config_with_yaml_types(self, temp_directory):
        """Test loading configuration with various YAML data types."""
        typed_config = {
            'string_value': 'hello world',
            'integer_value': 42,
            'float_value': 3.14159,
            'boolean_true': True,
            'boolean_false': False,
            'null_value': None,
            'list_mixed': [1, 'two', 3.0, True, None],
            'multiline_string': 'Line 1\nLine 2\nLine 3'
        }

        config_file = temp_directory / 'typed_config.yaml'
        with open(config_file, 'w') as f:
            yaml.dump(typed_config, f)

        loader = ConfigLoader()
        loader.config_dir = temp_directory

        result = loader.load_config('typed_config')
        assert result == typed_config

    def test_load_config_with_yaml_anchors_references(self, temp_directory):
        """Test loading configuration with YAML anchors and references."""
        yaml_content = """
defaults: &defaults
  timeout: 30
  retries: 3
  debug: false

development:
  <<: *defaults
  debug: true
  host: localhost

production:
  <<: *defaults
  host: prod.example.com
  timeout: 60
"""

        config_file = temp_directory / 'anchored_config.yaml'
        config_file.write_text(yaml_content)

        loader = ConfigLoader()
        loader.config_dir = temp_directory

        result = loader.load_config('anchored_config')

        expected = {
            'defaults': {
                'timeout': 30,
                'retries': 3,
                'debug': False
            },
            'development': {
                'timeout': 30,
                'retries': 3,
                'debug': True,
                'host': 'localhost'
            },
            'production': {
                'timeout': 60,
                'retries': 3,
                'debug': False,
                'host': 'prod.example.com'
            }
        }

        assert result == expected


class TestErrorHandlingAndEdgeCases:
    """Test error handling and edge cases."""

    def test_load_config_with_unicode_content(self, temp_directory):
        """Test loading configuration with Unicode content."""
        unicode_config = {
            'unicode_string': 'Hello 世界 🌍',
            'emoji_key_🔑': 'emoji value 🎉',
            'accented_text': 'café résumé naïve'
        }

        config_file = temp_directory / 'unicode_config.yaml'
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(unicode_config, f, allow_unicode=True)

        loader = ConfigLoader()
        loader.config_dir = temp_directory

        result = loader.load_config('unicode_config')
        assert result == unicode_config

    def test_load_config_large_file(self, temp_directory):
        """Test loading large configuration file."""
        # Create a large configuration with many items
        large_config = {
            f'item_{i}': {
                'value': i,
                'description': f'Description for item {i}',
                'data': list(range(i, i + 10))
            }
            for i in range(1000)  # 1000 items
        }

        config_file = temp_directory / 'large_config.yaml'
        with open(config_file, 'w') as f:
            yaml.dump(large_config, f)

        loader = ConfigLoader()
        loader.config_dir = temp_directory

        result = loader.load_config('large_config')
        assert result == large_config
        assert len(result) == 1000

    def test_load_config_malformed_yaml_variations(self, temp_directory, caplog):
        """Test various malformed YAML scenarios."""
        malformed_yamls = [
            'key: [unclosed list',
            'key: {unclosed dict',
            'invalid\nkey without colon',
            'key: value\n\tinvalid indentation',
            'key: |\n  multiline\nno proper indentation'
        ]

        loader = ConfigLoader()
        loader.config_dir = temp_directory

        for i, malformed_yaml in enumerate(malformed_yamls):
            config_file = temp_directory / f'malformed_{i}.yaml'
            config_file.write_text(malformed_yaml)

            with caplog.at_level(logging.ERROR):
                result = loader.load_config(f'malformed_{i}')

            assert result is None
            assert 'Error parsing YAML file' in caplog.text

    def test_load_config_permission_denied(self, temp_directory, caplog):
        """Test handling of permission denied errors."""
        config_file = temp_directory / 'protected_config.yaml'
        config_file.write_text('test: value')
        config_file.chmod(0o000)  # No permissions

        loader = ConfigLoader()
        loader.config_dir = temp_directory

        try:
            with caplog.at_level(logging.ERROR):
                result = loader.load_config('protected_config')

            assert result is None
            assert 'Error loading configuration' in caplog.text
        finally:
            # Restore permissions for cleanup
            config_file.chmod(0o644)

    def test_config_loader_with_readonly_directory(self, temp_directory):
        """Test ConfigLoader behavior with read-only config directory."""
        # Create a config file first
        config_file = temp_directory / 'readonly_test.yaml'
        config_file.write_text('test: readonly')

        # Make directory read-only
        temp_directory.chmod(0o444)

        try:
            loader = ConfigLoader()
            loader.config_dir = temp_directory

            # Should still be able to read existing files
            result = loader.load_config('readonly_test')
            assert result == {'test': 'readonly'}
        finally:
            # Restore permissions for cleanup
            temp_directory.chmod(0o755)


class TestIntegrationScenarios:
    """Test integration scenarios combining multiple features."""

    def test_complete_configuration_workflow(self, temp_directory):
        """Test complete configuration loading workflow."""
        # Create multiple configuration files
        configs = {
            'mcp_post_action_hints': {
                'hints': [
                    {'pattern': 'test', 'message': 'Test hint'}
                ]
            },
            'session_start_messages': {
                'messages': [
                    {'type': 'welcome', 'text': 'Welcome!'}
                ]
            },
            '__hint_message__pre_tool_use': {
                'pre_hints': [
                    {'condition': 'always', 'message': 'Pre-tool hint'}
                ]
            }
        }

        for config_name, config_data in configs.items():
            config_file = temp_directory / f'{config_name}.yaml'
            with open(config_file, 'w') as f:
                yaml.dump(config_data, f)

        loader = ConfigLoader()
        loader.config_dir = temp_directory

        # Test all specific configuration methods
        mcp_hints = loader.get_mcp_post_hints_config()
        session_config = loader.get_session_start_config()
        hint_config = loader.get_hint_message_config('pre_tool_use')

        assert mcp_hints == configs['mcp_post_action_hints']
        assert session_config == configs['session_start_messages']
        assert hint_config == configs['__hint_message__pre_tool_use']

        # Test caching
        assert len(loader._cache) == 3
        assert 'mcp_post_action_hints' in loader._cache
        assert 'session_start_messages' in loader._cache
        assert '__hint_message__pre_tool_use' in loader._cache

    def test_configuration_hot_reloading(self, temp_directory, caplog):
        """Test configuration hot reloading scenario."""
        # Initial configuration
        initial_config = {'setting': 'initial_value'}
        config_file = temp_directory / 'hot_reload_config.yaml'

        with open(config_file, 'w') as f:
            yaml.dump(initial_config, f)

        loader = ConfigLoader()
        loader.config_dir = temp_directory

        # Load initial configuration
        result1 = loader.load_config('hot_reload_config')
        assert result1 == initial_config

        # Update configuration file
        updated_config = {'setting': 'updated_value', 'new_setting': 'new_value'}
        with open(config_file, 'w') as f:
            yaml.dump(updated_config, f)

        # Normal load should return cached version
        result2 = loader.load_config('hot_reload_config')
        assert result2 == initial_config  # Still cached

        # Force reload should return updated version
        with caplog.at_level(logging.DEBUG):
            result3 = loader.reload_config('hot_reload_config')

        assert result3 == updated_config
        assert 'Configuration cache cleared' not in caplog.text  # reload doesn't clear entire cache

        # Subsequent loads should now return updated version
        result4 = loader.load_config('hot_reload_config')
        assert result4 == updated_config

    def test_multiple_loader_instances_independence(self, temp_directory):
        """Test that multiple ConfigLoader instances are independent."""
        config_data = {'test': 'value'}
        config_file = temp_directory / 'independence_test.yaml'

        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)

        # Create two separate loader instances
        loader1 = ConfigLoader()
        loader2 = ConfigLoader()

        loader1.config_dir = temp_directory
        loader2.config_dir = temp_directory

        # Load with first loader
        result1 = loader1.load_config('independence_test')
        assert result1 == config_data
        assert 'independence_test' in loader1._cache
        assert 'independence_test' not in loader2._cache

        # Clear cache on first loader
        loader1.clear_cache()
        assert loader1._cache == {}

        # Load with second loader (should have its own cache)
        result2 = loader2.load_config('independence_test')
        assert result2 == config_data
        assert 'independence_test' in loader2._cache
        assert loader1._cache == {}  # Should still be empty