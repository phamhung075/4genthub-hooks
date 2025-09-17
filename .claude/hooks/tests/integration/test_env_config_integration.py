"""
Integration tests for environment and configuration loading.

Tests cover:
- Integration between env_loader and config_loader
- Complete system initialization scenarios
- Missing file handling across both systems
- Environment variable fallback with configuration loading
- Docker vs local environment integration
- Error propagation and recovery scenarios
"""

import os
import pytest
import tempfile
import yaml
import sys
from pathlib import Path
from unittest.mock import patch, Mock

# Add hooks directory to Python path
hooks_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(hooks_dir))

from utils.env_loader import (
    find_project_root,
    get_ai_data_path,
    get_ai_docs_path,
    get_all_paths,
    is_claude_edit_enabled
)
from config.config_loader import (
    ConfigLoader,
    get_config_loader,
    load_mcp_hints_config
)


class TestEnvironmentConfigurationIntegration:
    """Test integration between environment and configuration loading."""

    def test_complete_system_initialization(self, temp_directory):
        """Test complete system initialization with both env and config files."""
        # Create .env.claude file
        env_claude_content = """
AI_DATA=integration_data
AI_DOCS=integration_docs
LOG_PATH=integration_logs
ENABLE_CLAUDE_EDIT=true
"""
        env_claude_file = temp_directory / '.env.claude'
        env_claude_file.write_text(env_claude_content)

        # Create config directory and files
        config_dir = temp_directory / '.claude' / 'hooks' / 'config'
        config_dir.mkdir(parents=True)

        mcp_hints_config = {
            'hints': [
                {'pattern': 'integration_test', 'message': 'Integration hint'}
            ]
        }
        (config_dir / 'mcp_post_action_hints.yaml').write_text(
            yaml.dump(mcp_hints_config)
        )

        # Mock environment variables
        with patch.dict(os.environ, {
            'AI_DATA': 'integration_data',
            'AI_DOCS': 'integration_docs',
            'LOG_PATH': 'integration_logs',
            'ENABLE_CLAUDE_EDIT': 'true'
        }):
            with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                # Test environment loading
                ai_data = get_ai_data_path()
                ai_docs = get_ai_docs_path()
                all_paths = get_all_paths()
                edit_enabled = is_claude_edit_enabled()

                assert ai_data == temp_directory / 'integration_data'
                assert ai_docs == temp_directory / 'integration_docs'
                assert edit_enabled is True

                # Test configuration loading
                loader = ConfigLoader()
                loader.config_dir = config_dir

                hints_config = loader.get_mcp_post_hints_config()
                assert hints_config == mcp_hints_config

    def test_missing_env_files_with_config_fallback(self, temp_directory):
        """Test behavior when env files are missing but config files exist."""
        # Create config directory and files (no env files)
        config_dir = temp_directory / '.claude' / 'hooks' / 'config'
        config_dir.mkdir(parents=True)

        session_config = {
            'messages': [
                {'type': 'info', 'text': 'Session started without env file'}
            ]
        }
        (config_dir / 'session_start_messages.yaml').write_text(
            yaml.dump(session_config)
        )

        # No environment variables set
        with patch.dict(os.environ, {}, clear=True):
            with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                # Environment should use defaults
                ai_data = get_ai_data_path()
                ai_docs = get_ai_docs_path()
                edit_enabled = is_claude_edit_enabled()

                assert ai_data == temp_directory / 'logs'  # Default
                assert ai_docs == temp_directory / 'ai_docs'  # Default
                assert edit_enabled is False  # Default

                # Configuration should still work
                loader = ConfigLoader()
                loader.config_dir = config_dir

                session_msgs = loader.get_session_start_config()
                assert session_msgs == session_config

    def test_missing_config_files_with_env_fallback(self, temp_directory):
        """Test behavior when config files are missing but env files exist."""
        # Create .env.claude file
        env_claude_content = """
AI_DATA=env_only_data
AI_DOCS=env_only_docs
ENABLE_CLAUDE_EDIT=false
"""
        env_claude_file = temp_directory / '.env.claude'
        env_claude_file.write_text(env_claude_content)

        # Create empty config directory (no config files)
        config_dir = temp_directory / '.claude' / 'hooks' / 'config'
        config_dir.mkdir(parents=True)

        with patch.dict(os.environ, {
            'AI_DATA': 'env_only_data',
            'AI_DOCS': 'env_only_docs',
            'ENABLE_CLAUDE_EDIT': 'false'
        }):
            with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                # Environment should work
                ai_data = get_ai_data_path()
                ai_docs = get_ai_docs_path()
                edit_enabled = is_claude_edit_enabled()

                assert ai_data == temp_directory / 'env_only_data'
                assert ai_docs == temp_directory / 'env_only_docs'
                assert edit_enabled is False

                # Configuration should return None for missing files
                loader = ConfigLoader()
                loader.config_dir = config_dir

                hints_config = loader.get_mcp_post_hints_config()
                session_config = loader.get_session_start_config()

                assert hints_config is None
                assert session_config is None

    def test_both_systems_missing_graceful_degradation(self, temp_directory):
        """Test graceful degradation when both env and config systems have missing files."""
        # No .env.claude, no .env, no config files
        # Only create basic directory structure
        config_dir = temp_directory / '.claude' / 'hooks' / 'config'
        config_dir.mkdir(parents=True)

        with patch.dict(os.environ, {}, clear=True):
            with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                # Environment should use defaults
                ai_data = get_ai_data_path()
                ai_docs = get_ai_docs_path()
                all_paths = get_all_paths()
                edit_enabled = is_claude_edit_enabled()

                # Should get default values
                assert ai_data == temp_directory / 'logs'
                assert ai_docs == temp_directory / 'ai_docs'
                assert edit_enabled is False

                # All paths should be consistent
                assert all_paths['ai_data'] == ai_data
                assert all_paths['ai_docs'] == ai_docs

                # Configuration should handle missing files gracefully
                loader = ConfigLoader()
                loader.config_dir = config_dir

                assert loader.get_mcp_post_hints_config() is None
                assert loader.get_session_start_config() is None
                assert loader.get_hint_message_config('any_type') is None


class TestDockerLocalEnvironmentIntegration:
    """Test integration scenarios for Docker vs local environments."""

    def test_docker_environment_complete_setup(self, temp_directory):
        """Test complete setup in Docker-like environment."""
        # Docker-style absolute paths
        docker_env_vars = {
            'DOCKER_CONTAINER': '1',
            'AI_DATA': '/app/data',
            'AI_DOCS': '/app/docs',
            'LOG_PATH': '/app/logs',
            'ENABLE_CLAUDE_EDIT': 'false'
        }

        # Create Docker-style config directory
        config_dir = temp_directory / 'app' / 'config'
        config_dir.mkdir(parents=True)

        docker_config = {
            'docker_mode': True,
            'container_settings': {
                'mount_points': ['/app/data', '/app/docs', '/app/logs'],
                'permissions': 'restricted'
            }
        }
        (config_dir / 'docker_config.yaml').write_text(
            yaml.dump(docker_config)
        )

        with patch.dict(os.environ, docker_env_vars):
            # Environment paths should be absolute
            ai_data = get_ai_data_path()
            ai_docs = get_ai_docs_path()

            assert str(ai_data) == '/app/data'
            assert str(ai_docs) == '/app/docs'
            assert is_claude_edit_enabled() is False

            # Configuration should work normally
            loader = ConfigLoader()
            loader.config_dir = config_dir

            docker_cfg = loader.load_config('docker_config')
            assert docker_cfg == docker_config
            assert docker_cfg['docker_mode'] is True

    def test_local_development_complete_setup(self, temp_directory):
        """Test complete setup in local development environment."""
        # Local development relative paths
        local_env_vars = {
            'AI_DATA': 'local_data',
            'AI_DOCS': 'local_docs',
            'LOG_PATH': 'local_logs',
            'ENABLE_CLAUDE_EDIT': 'true'
        }

        # Create .env.claude file
        env_claude_content = '\n'.join(f'{k}={v}' for k, v in local_env_vars.items())
        (temp_directory / '.env.claude').write_text(env_claude_content)

        # Create local config directory
        config_dir = temp_directory / '.claude' / 'hooks' / 'config'
        config_dir.mkdir(parents=True)

        local_config = {
            'development_mode': True,
            'local_settings': {
                'auto_reload': True,
                'debug_logging': True,
                'file_watching': True
            }
        }
        (config_dir / 'development_config.yaml').write_text(
            yaml.dump(local_config)
        )

        with patch.dict(os.environ, local_env_vars):
            with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                # Environment paths should be relative to project root
                ai_data = get_ai_data_path()
                ai_docs = get_ai_docs_path()
                all_paths = get_all_paths()

                assert ai_data == temp_directory / 'local_data'
                assert ai_docs == temp_directory / 'local_docs'
                assert all_paths['log_path'] == temp_directory / 'local_logs'
                assert is_claude_edit_enabled() is True

                # All directories should be created
                assert ai_data.exists()
                assert ai_docs.exists()
                assert all_paths['log_path'].exists()

                # Configuration should work
                loader = ConfigLoader()
                loader.config_dir = config_dir

                dev_cfg = loader.load_config('development_config')
                assert dev_cfg == local_config
                assert dev_cfg['development_mode'] is True

    def test_mixed_docker_local_configuration(self, temp_directory):
        """Test mixed Docker and local configuration scenario."""
        # Some paths absolute (Docker-style), some relative (local-style)
        mixed_env_vars = {
            'AI_DATA': '/docker/data',  # Absolute
            'AI_DOCS': 'local_docs',    # Relative
            'LOG_PATH': '/docker/logs', # Absolute
            'ENABLE_CLAUDE_EDIT': 'true'
        }

        # Create mixed config directory structure
        config_dir = temp_directory / '.claude' / 'hooks' / 'config'
        config_dir.mkdir(parents=True)

        mixed_config = {
            'environment_type': 'hybrid',
            'paths': {
                'absolute_paths': ['/docker/data', '/docker/logs'],
                'relative_paths': ['local_docs']
            }
        }
        (config_dir / 'mixed_config.yaml').write_text(
            yaml.dump(mixed_config)
        )

        with patch.dict(os.environ, mixed_env_vars):
            with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                ai_data = get_ai_data_path()
                ai_docs = get_ai_docs_path()

                # Should handle mixed absolute/relative correctly
                assert str(ai_data) == '/docker/data'
                assert ai_docs == temp_directory / 'local_docs'

                # Configuration should be accessible
                loader = ConfigLoader()
                loader.config_dir = config_dir

                mixed_cfg = loader.load_config('mixed_config')
                assert mixed_cfg['environment_type'] == 'hybrid'


class TestErrorPropagationAndRecovery:
    """Test error propagation and recovery between systems."""

    def test_env_error_config_success(self, temp_directory, caplog):
        """Test scenario where env loading fails but config loading succeeds."""
        # Create config that works
        config_dir = temp_directory / '.claude' / 'hooks' / 'config'
        config_dir.mkdir(parents=True)

        working_config = {'status': 'working'}
        (config_dir / 'working_config.yaml').write_text(
            yaml.dump(working_config)
        )

        # Create problematic environment setup
        # Mock permission error on directory creation
        with patch('pathlib.Path.mkdir', side_effect=PermissionError('Permission denied')):
            with patch.dict(os.environ, {'AI_DATA': 'problematic_data'}):
                with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                    # Environment should fail
                    with pytest.raises(PermissionError):
                        get_ai_data_path()

                    # But configuration should still work
                    loader = ConfigLoader()
                    loader.config_dir = config_dir

                    config = loader.load_config('working_config')
                    assert config == working_config

    def test_config_error_env_success(self, temp_directory, caplog):
        """Test scenario where config loading fails but env loading succeeds."""
        # Create working environment
        with patch.dict(os.environ, {'AI_DATA': 'working_data'}):
            with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                # Environment should work
                ai_data = get_ai_data_path()
                assert ai_data == temp_directory / 'working_data'
                assert ai_data.exists()

        # Create problematic config
        config_dir = temp_directory / '.claude' / 'hooks' / 'config'
        config_dir.mkdir(parents=True)

        # Create malformed YAML
        (config_dir / 'broken_config.yaml').write_text('invalid: yaml: [content')

        loader = ConfigLoader()
        loader.config_dir = config_dir

        with caplog.at_level('ERROR'):
            broken_config = loader.load_config('broken_config')

        assert broken_config is None
        assert 'Error parsing YAML file' in caplog.text

    def test_cascading_failures_recovery(self, temp_directory, caplog):
        """Test recovery from cascading failures across both systems."""
        # Start with both systems broken
        config_dir = temp_directory / '.claude' / 'hooks' / 'config'
        config_dir.mkdir(parents=True)

        # Create broken config
        (config_dir / 'broken.yaml').write_text('invalid yaml content [')

        # Mock environment failures
        with patch('pathlib.Path.mkdir', side_effect=OSError('System error')):
            with patch.dict(os.environ, {'AI_DATA': 'failing_data'}):
                with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                    # Both should fail initially
                    with pytest.raises(OSError):
                        get_ai_data_path()

                    loader = ConfigLoader()
                    loader.config_dir = config_dir

                    with caplog.at_level('ERROR'):
                        broken_config = loader.load_config('broken')
                    assert broken_config is None

        # Now fix environment (remove the mock)
        with patch.dict(os.environ, {'AI_DATA': 'recovered_data'}):
            with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                # Environment should recover
                ai_data = get_ai_data_path()
                assert ai_data == temp_directory / 'recovered_data'
                assert ai_data.exists()

        # Fix configuration
        fixed_config = {'status': 'recovered'}
        (config_dir / 'fixed.yaml').write_text(yaml.dump(fixed_config))

        # Both should work now
        loader = ConfigLoader()
        loader.config_dir = config_dir

        config = loader.load_config('fixed')
        assert config == fixed_config

    def test_partial_system_operation(self, temp_directory):
        """Test that systems can operate independently when one is unavailable."""
        # Set up environment only
        with patch.dict(os.environ, {
            'AI_DATA': 'independent_data',
            'AI_DOCS': 'independent_docs',
            'ENABLE_CLAUDE_EDIT': 'true'
        }):
            with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                # Environment functions should work
                ai_data = get_ai_data_path()
                ai_docs = get_ai_docs_path()
                all_paths = get_all_paths()
                edit_enabled = is_claude_edit_enabled()

                assert ai_data == temp_directory / 'independent_data'
                assert ai_docs == temp_directory / 'independent_docs'
                assert edit_enabled is True
                assert len(all_paths) == 3

        # Configuration system without any files should handle gracefully
        empty_config_dir = temp_directory / 'empty_config'
        empty_config_dir.mkdir()

        loader = ConfigLoader()
        loader.config_dir = empty_config_dir

        # Should return None for missing files without crashing
        assert loader.get_mcp_post_hints_config() is None
        assert loader.get_session_start_config() is None
        assert loader.get_hint_message_config('test') is None

        # Should maintain empty cache
        assert loader._cache == {}


class TestComplexIntegrationScenarios:
    """Test complex real-world integration scenarios."""

    def test_full_application_startup_simulation(self, temp_directory):
        """Simulate full application startup with all components."""
        # Create complete project structure
        project_structure = {
            '.env.claude': '''
AI_DATA=app_data
AI_DOCS=app_docs
LOG_PATH=app_logs
ENABLE_CLAUDE_EDIT=true
''',
            '.claude/hooks/config/mcp_post_action_hints.yaml': yaml.dump({
                'hints': [
                    {'pattern': 'startup', 'message': 'Application starting up'},
                    {'pattern': 'ready', 'message': 'Application ready'}
                ]
            }),
            '.claude/hooks/config/session_start_messages.yaml': yaml.dump({
                'messages': [
                    {'type': 'welcome', 'text': 'Welcome to the application'},
                    {'type': 'status', 'text': 'All systems operational'}
                ]
            }),
            '.claude/hooks/config/__hint_message__pre_tool_use.yaml': yaml.dump({
                'pre_hints': [
                    {'condition': 'always', 'message': 'Pre-tool validation'}
                ]
            })
        }

        # Create all files
        for file_path, content in project_structure.items():
            full_path = temp_directory / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)

        # Simulate application startup
        with patch.dict(os.environ, {
            'AI_DATA': 'app_data',
            'AI_DOCS': 'app_docs',
            'LOG_PATH': 'app_logs',
            'ENABLE_CLAUDE_EDIT': 'true'
        }):
            with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                # Phase 1: Environment initialization
                all_paths = get_all_paths()
                edit_enabled = is_claude_edit_enabled()

                assert all_paths['ai_data'] == temp_directory / 'app_data'
                assert all_paths['ai_docs'] == temp_directory / 'app_docs'
                assert all_paths['log_path'] == temp_directory / 'app_logs'
                assert edit_enabled is True

                # All directories should be created
                for path in all_paths.values():
                    assert path.exists()

                # Phase 2: Configuration initialization
                config_dir = temp_directory / '.claude' / 'hooks' / 'config'
                loader = ConfigLoader()
                loader.config_dir = config_dir

                mcp_hints = loader.get_mcp_post_hints_config()
                session_msgs = loader.get_session_start_config()
                pre_hints = loader.get_hint_message_config('pre_tool_use')

                assert len(mcp_hints['hints']) == 2
                assert len(session_msgs['messages']) == 2
                assert len(pre_hints['pre_hints']) == 1

                # Phase 3: Verify all systems operational
                assert len(loader._cache) == 3  # All configs cached
                assert all(path.exists() for path in all_paths.values())

    def test_configuration_hot_reload_with_environment_changes(self, temp_directory):
        """Test hot reloading configuration while environment changes."""
        # Initial setup
        config_dir = temp_directory / '.claude' / 'hooks' / 'config'
        config_dir.mkdir(parents=True)

        initial_config = {
            'app_settings': {
                'data_path': 'initial_data',
                'debug': False
            }
        }
        config_file = config_dir / 'app_config.yaml'
        config_file.write_text(yaml.dump(initial_config))

        loader = ConfigLoader()
        loader.config_dir = config_dir

        # Initial environment and config load
        with patch.dict(os.environ, {'AI_DATA': 'initial_data'}):
            with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                ai_data_initial = get_ai_data_path()
                config_initial = loader.load_config('app_config')

                assert ai_data_initial == temp_directory / 'initial_data'
                assert config_initial['app_settings']['data_path'] == 'initial_data'

        # Change environment
        with patch.dict(os.environ, {'AI_DATA': 'updated_data'}):
            with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                ai_data_updated = get_ai_data_path()
                assert ai_data_updated == temp_directory / 'updated_data'

                # Update configuration file
                updated_config = {
                    'app_settings': {
                        'data_path': 'updated_data',
                        'debug': True,
                        'new_feature': 'enabled'
                    }
                }
                config_file.write_text(yaml.dump(updated_config))

                # Force reload configuration
                config_reloaded = loader.reload_config('app_config')

                assert config_reloaded['app_settings']['data_path'] == 'updated_data'
                assert config_reloaded['app_settings']['debug'] is True
                assert config_reloaded['app_settings']['new_feature'] == 'enabled'

        # Verify both systems reflect the changes
        assert ai_data_updated.exists()
        assert ai_data_updated != ai_data_initial

    def test_multi_environment_configuration_matrix(self, temp_directory):
        """Test configuration matrix across multiple environment types."""
        environments = {
            'development': {
                'env_vars': {
                    'AI_DATA': 'dev_data',
                    'AI_DOCS': 'dev_docs',
                    'ENABLE_CLAUDE_EDIT': 'true'
                },
                'config': {
                    'environment': 'development',
                    'debug': True,
                    'auto_reload': True
                }
            },
            'testing': {
                'env_vars': {
                    'AI_DATA': 'test_data',
                    'AI_DOCS': 'test_docs',
                    'ENABLE_CLAUDE_EDIT': 'false'
                },
                'config': {
                    'environment': 'testing',
                    'debug': False,
                    'test_mode': True
                }
            },
            'production': {
                'env_vars': {
                    'AI_DATA': '/prod/data',
                    'AI_DOCS': '/prod/docs',
                    'ENABLE_CLAUDE_EDIT': 'false'
                },
                'config': {
                    'environment': 'production',
                    'debug': False,
                    'security_enabled': True
                }
            }
        }

        config_dir = temp_directory / '.claude' / 'hooks' / 'config'
        config_dir.mkdir(parents=True)

        # Test each environment configuration
        for env_name, env_setup in environments.items():
            # Create environment-specific config file
            config_file = config_dir / f'{env_name}_config.yaml'
            config_file.write_text(yaml.dump(env_setup['config']))

            # Test with environment variables
            with patch.dict(os.environ, env_setup['env_vars']):
                with patch('utils.env_loader.PROJECT_ROOT', temp_directory):
                    # Test environment loading
                    ai_data = get_ai_data_path()
                    edit_enabled = is_claude_edit_enabled()

                    if env_setup['env_vars']['AI_DATA'].startswith('/'):
                        # Absolute path
                        assert str(ai_data) == env_setup['env_vars']['AI_DATA']
                    else:
                        # Relative path
                        assert ai_data == temp_directory / env_setup['env_vars']['AI_DATA']

                    expected_edit = env_setup['env_vars']['ENABLE_CLAUDE_EDIT'] == 'true'
                    assert edit_enabled == expected_edit

                    # Test configuration loading
                    loader = ConfigLoader()
                    loader.config_dir = config_dir

                    config = loader.load_config(f'{env_name}_config')
                    assert config == env_setup['config']
                    assert config['environment'] == env_name

        # Verify all configurations are independently cached
        final_loader = ConfigLoader()
        final_loader.config_dir = config_dir

        # Load all configs to verify cache independence
        for env_name in environments.keys():
            config = final_loader.load_config(f'{env_name}_config')
            assert config['environment'] == env_name

        assert len(final_loader._cache) == 3  # All three environment configs cached