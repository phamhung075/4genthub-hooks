#!/usr/bin/env python3
"""
Centralized Configuration Factory for Claude Hook System.

This factory provides unified access to all configuration data, messages,
and settings across the entire hook system using a consistent YAML-based
configuration approach with intelligent caching and fallback mechanisms.
"""

import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional, Union
from datetime import datetime
import logging

# Set up logging
logger = logging.getLogger(__name__)

class ConfigFactory:
    """
    Centralized configuration factory for the entire hook system.

    Features:
    - Unified YAML configuration loading
    - Intelligent caching with TTL
    - Fallback mechanisms for reliability
    - Type-safe message formatting
    - Performance optimized with lazy loading
    """

    def __init__(self):
        """Initialize the configuration factory."""
        self.config_dir = Path(__file__).parent.parent / 'config'
        self._cache = {}
        self._cache_timestamps = {}
        self._cache_ttl = 300  # 5 minutes cache TTL

        # Ensure config directory exists
        self.config_dir.mkdir(exist_ok=True)

    def _is_cache_valid(self, key: str) -> bool:
        """Check if cached item is still valid based on TTL."""
        if key not in self._cache_timestamps:
            return False

        cache_time = self._cache_timestamps[key]
        current_time = datetime.now()
        return (current_time - cache_time).total_seconds() < self._cache_ttl

    def _load_yaml_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Load a YAML file with error handling.

        Args:
            file_path: Path to the YAML file

        Returns:
            Dictionary with file contents or None on error
        """
        if not file_path.exists():
            logger.warning(f"Configuration file not found: {file_path}")
            return None

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                logger.debug(f"Loaded configuration: {file_path.name}")
                return data
        except yaml.YAMLError as e:
            logger.error(f"YAML parsing error in {file_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")
            return None

    def _get_config(self, config_name: str, use_cache: bool = True) -> Optional[Dict[str, Any]]:
        """
        Get configuration data with caching.

        Args:
            config_name: Name of the configuration (without .yaml extension)
            use_cache: Whether to use cached version if available

        Returns:
            Configuration dictionary or None if not found
        """
        # Check cache first
        if use_cache and config_name in self._cache and self._is_cache_valid(config_name):
            return self._cache[config_name]

        # Load from file
        config_path = self.config_dir / f"{config_name}.yaml"
        data = self._load_yaml_file(config_path)

        # Cache the result if successful
        if data is not None:
            self._cache[config_name] = data
            self._cache_timestamps[config_name] = datetime.now()

        return data

    def get_error_messages(self) -> Dict[str, Any]:
        """Get all error messages configuration."""
        return self._get_config('error_messages') or {}

    def get_warning_messages(self) -> Dict[str, Any]:
        """Get all warning messages configuration."""
        return self._get_config('warning_messages') or {}

    def get_info_messages(self) -> Dict[str, Any]:
        """Get all info messages configuration."""
        return self._get_config('info_messages') or {}

    def get_hint_messages(self) -> Dict[str, Any]:
        """Get all hint messages configuration."""
        return self._get_config('hint_messages') or {}

    def get_session_messages(self) -> Dict[str, Any]:
        """Get session-related messages configuration."""
        return self._get_config('session_messages') or {}

    def get_system_config(self) -> Dict[str, Any]:
        """Get system-wide configuration settings."""
        return self._get_config('system_config') or {}

    def get_pre_tool_messages(self) -> Dict[str, Any]:
        """Get pre-tool hook messages configuration."""
        return self._get_config('pre_tool_messages') or {}

    def get_post_tool_messages(self) -> Dict[str, Any]:
        """Get post-tool hook messages configuration."""
        return self._get_config('post_tool_messages') or {}

    def get_docs_messages(self) -> Dict[str, Any]:
        """Get documentation indexer messages configuration."""
        return self._get_config('docs_messages') or {}

    def get_status_line_messages(self) -> Dict[str, Any]:
        """Get status line messages configuration."""
        return self._get_config('status_line_messages') or {}

    def format_message(self, message_category: str, message_key: str, **kwargs) -> str:
        """
        Format a message with parameters using template substitution.

        Args:
            message_category: Category of message (error, warning, info, etc.)
            message_key: Key identifying the specific message
            **kwargs: Parameters to substitute into the message template

        Returns:
            Formatted message string with fallback if not found
        """
        # Get the appropriate message collection
        message_collections = {
            'error': self.get_error_messages(),
            'warning': self.get_warning_messages(),
            'info': self.get_info_messages(),
            'hint': self.get_hint_messages(),
            'session': self.get_session_messages(),
            'pre_tool': self.get_pre_tool_messages(),
            'post_tool': self.get_post_tool_messages(),
            'docs': self.get_docs_messages(),
            'status_line': self.get_status_line_messages()
        }

        messages = message_collections.get(message_category, {})

        if message_key not in messages:
            logger.warning(f"Message not found: {message_category}.{message_key}")
            return f"Unknown {message_category}: {message_key}"

        message_config = messages[message_key]

        # Handle simple string messages
        if isinstance(message_config, str):
            try:
                return message_config.format(**kwargs)
            except KeyError as e:
                logger.error(f"Missing parameter {e} for message {message_category}.{message_key}")
                return message_config

        # Handle complex message objects
        if isinstance(message_config, dict):
            result = []

            # Format main message
            if 'message' in message_config:
                try:
                    main_message = message_config['message'].format(**kwargs)
                    result.append(main_message)
                except KeyError as e:
                    logger.error(f"Missing parameter {e} for message {message_category}.{message_key}")
                    result.append(message_config['message'])

            # Add hint if present
            if 'hint' in message_config:
                try:
                    hint = message_config['hint'].format(**kwargs)
                    result.append(hint)
                except KeyError:
                    result.append(message_config['hint'])

            # Add examples if present
            for field in ['examples', 'valid_examples', 'invalid_examples', 'valid_paths']:
                if field in message_config:
                    field_label = field.replace('_', ' ').title()
                    items = message_config[field]
                    if isinstance(items, list):
                        result.append(f"{field_label}: " + ", ".join(items))
                    else:
                        result.append(f"{field_label}: {items}")

            # Add action if present
            if 'action' in message_config:
                try:
                    action = message_config['action'].format(**kwargs)
                    result.append(action)
                except KeyError:
                    result.append(message_config['action'])

            return "\n".join(result)

        # Fallback for unexpected message format
        return str(message_config)

    def get_setting(self, setting_key: str, default_value: Any = None) -> Any:
        """
        Get a system setting with fallback to default value.

        Args:
            setting_key: Key identifying the setting (dot notation supported)
            default_value: Default value if setting not found

        Returns:
            Setting value or default_value if not found
        """
        config = self.get_system_config()

        # Support dot notation for nested settings (e.g., "cache.ttl")
        keys = setting_key.split('.')
        current = config

        try:
            for key in keys:
                current = current[key]
            return current
        except (KeyError, TypeError):
            logger.debug(f"Setting not found: {setting_key}, using default: {default_value}")
            return default_value

    def clear_cache(self):
        """Clear all cached configuration data."""
        self._cache.clear()
        self._cache_timestamps.clear()
        logger.debug("Configuration cache cleared")

    def reload_config(self, config_name: str) -> Optional[Dict[str, Any]]:
        """
        Force reload a specific configuration, bypassing cache.

        Args:
            config_name: Name of the configuration to reload

        Returns:
            Reloaded configuration data
        """
        return self._get_config(config_name, use_cache=False)

# Global factory instance
_config_factory = None

def get_config_factory() -> ConfigFactory:
    """
    Get the global configuration factory instance.

    Returns:
        ConfigFactory instance (singleton)
    """
    global _config_factory
    if _config_factory is None:
        _config_factory = ConfigFactory()
    return _config_factory

# Convenience functions for common operations
def get_error_message(message_key: str, **kwargs) -> str:
    """Get formatted error message."""
    factory = get_config_factory()
    return factory.format_message('error', message_key, **kwargs)

def get_warning_message(message_key: str, **kwargs) -> str:
    """Get formatted warning message."""
    factory = get_config_factory()
    return factory.format_message('warning', message_key, **kwargs)

def get_info_message(message_key: str, **kwargs) -> str:
    """Get formatted info message."""
    factory = get_config_factory()
    return factory.format_message('info', message_key, **kwargs)

def get_hint_message(message_key: str, **kwargs) -> str:
    """Get formatted hint message."""
    factory = get_config_factory()
    return factory.format_message('hint', message_key, **kwargs)

def get_system_setting(setting_key: str, default_value: Any = None) -> Any:
    """Get system setting with default fallback."""
    factory = get_config_factory()
    return factory.get_setting(setting_key, default_value)