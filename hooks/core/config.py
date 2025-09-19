"""
Configuration management system for the Claude hooks framework.

This module provides centralized configuration loading, caching, validation,
and management with support for multiple configuration sources, environment
variable overrides, and real-time configuration updates.
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional, List, Union, Callable
from datetime import datetime, timedelta
import logging
from functools import wraps
import threading

from .interfaces import IConfigurable, ICache, IHealthCheck
from .exceptions import ConfigurationError, CacheError, HookException


class ConfigCache:
    """In-memory cache with TTL support for configuration data."""

    def __init__(self, default_ttl: int = 300):  # 5 minutes default TTL
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._timestamps: Dict[str, datetime] = {}
        self._ttl: Dict[str, int] = {}
        self._default_ttl = default_ttl
        self._lock = threading.RLock()
        self._hits = 0
        self._misses = 0

    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache with TTL checking."""
        with self._lock:
            if key not in self._cache:
                self._misses += 1
                return default

            # Check TTL
            if self._is_expired(key):
                self._remove(key)
                self._misses += 1
                return default

            self._hits += 1
            return self._cache[key]

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with optional TTL."""
        with self._lock:
            self._cache[key] = value
            self._timestamps[key] = datetime.now()
            self._ttl[key] = ttl or self._default_ttl

    def invalidate(self, pattern: Optional[str] = None) -> None:
        """Invalidate cache entries matching pattern."""
        with self._lock:
            if pattern is None:
                # Clear all
                self._cache.clear()
                self._timestamps.clear()
                self._ttl.clear()
            else:
                # Pattern matching (simple wildcard support)
                keys_to_remove = []
                if pattern.endswith('*'):
                    prefix = pattern[:-1]
                    keys_to_remove = [k for k in self._cache.keys() if k.startswith(prefix)]
                elif pattern.startswith('*'):
                    suffix = pattern[1:]
                    keys_to_remove = [k for k in self._cache.keys() if k.endswith(suffix)]
                else:
                    keys_to_remove = [k for k in self._cache.keys() if pattern in k]

                for key in keys_to_remove:
                    self._remove(key)

    def get_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        with self._lock:
            return {
                'hits': self._hits,
                'misses': self._misses,
                'entries': len(self._cache),
                'expired': sum(1 for k in self._cache.keys() if self._is_expired(k))
            }

    def _is_expired(self, key: str) -> bool:
        """Check if cache entry is expired."""
        if key not in self._timestamps:
            return True

        expiry_time = self._timestamps[key] + timedelta(seconds=self._ttl[key])
        return datetime.now() > expiry_time

    def _remove(self, key: str) -> None:
        """Remove entry from cache."""
        self._cache.pop(key, None)
        self._timestamps.pop(key, None)
        self._ttl.pop(key, None)

    def cleanup_expired(self) -> int:
        """Remove expired entries and return count removed."""
        with self._lock:
            expired_keys = [k for k in self._cache.keys() if self._is_expired(k)]
            for key in expired_keys:
                self._remove(key)
            return len(expired_keys)


class ConfigValidator:
    """Configuration validation with schema support."""

    def __init__(self):
        self._schemas: Dict[str, Dict[str, Any]] = {}
        self._validators: Dict[str, Callable] = {}

    def register_schema(self, section: str, schema: Dict[str, Any]):
        """Register configuration schema for validation."""
        self._schemas[section] = schema

    def register_validator(self, name: str, validator_func: Callable[[Any], bool]):
        """Register custom validator function."""
        self._validators[name] = validator_func

    def validate(self, section: str, config: Dict[str, Any]) -> List[str]:
        """
        Validate configuration against registered schema.

        Returns:
            List of validation errors (empty if valid)
        """
        if section not in self._schemas:
            return []  # No schema to validate against

        schema = self._schemas[section]
        errors = []

        # Check required fields
        required = schema.get('required', [])
        for field in required:
            if field not in config:
                errors.append(f"Required field '{field}' missing in section '{section}'")

        # Validate field types and values
        properties = schema.get('properties', {})
        for field, field_schema in properties.items():
            if field not in config:
                continue

            value = config[field]
            field_errors = self._validate_field(field, value, field_schema)
            errors.extend([f"Section '{section}', field '{field}': {err}" for err in field_errors])

        return errors

    def _validate_field(self, field: str, value: Any, schema: Dict[str, Any]) -> List[str]:
        """Validate individual field against schema."""
        errors = []

        # Type validation
        expected_type = schema.get('type')
        if expected_type:
            if not self._check_type(value, expected_type):
                errors.append(f"Expected type {expected_type}, got {type(value).__name__}")

        # Custom validator
        validator_name = schema.get('validator')
        if validator_name and validator_name in self._validators:
            try:
                if not self._validators[validator_name](value):
                    errors.append(f"Failed custom validation '{validator_name}'")
            except Exception as e:
                errors.append(f"Validator '{validator_name}' error: {str(e)}")

        # Range validation for numbers
        if isinstance(value, (int, float)):
            min_val = schema.get('minimum')
            max_val = schema.get('maximum')
            if min_val is not None and value < min_val:
                errors.append(f"Value {value} below minimum {min_val}")
            if max_val is not None and value > max_val:
                errors.append(f"Value {value} above maximum {max_val}")

        # Enum validation
        enum_values = schema.get('enum')
        if enum_values and value not in enum_values:
            errors.append(f"Value '{value}' not in allowed values: {enum_values}")

        return errors

    def _check_type(self, value: Any, expected_type: str) -> bool:
        """Check if value matches expected type."""
        type_mapping = {
            'string': str,
            'integer': int,
            'number': (int, float),
            'boolean': bool,
            'array': list,
            'object': dict
        }

        expected = type_mapping.get(expected_type)
        if expected is None:
            return True  # Unknown type, skip validation

        return isinstance(value, expected)


class Config(IConfigurable, IHealthCheck):
    """
    Centralized configuration management with caching and validation.

    Provides hierarchical configuration loading, environment variable overrides,
    real-time updates, and comprehensive validation.
    """

    def __init__(self, config_dir: Optional[Path] = None, cache_ttl: int = 300):
        """
        Initialize configuration manager.

        Args:
            config_dir: Directory containing configuration files
            cache_ttl: Cache time-to-live in seconds
        """
        self.config_dir = config_dir or Path(__file__).parent.parent / 'config'
        self._cache = ConfigCache(cache_ttl)
        self._validator = ConfigValidator()
        self._config_data: Dict[str, Any] = {}
        self._file_timestamps: Dict[str, datetime] = {}
        self._watchers: List[Callable[[str, Dict[str, Any]], None]] = []
        self._logger = logging.getLogger(__name__)
        self._lock = threading.RLock()

        # Core configuration sections
        self._sections = [
            'main', 'messages', 'validators', 'processors',
            'hint_providers', 'loggers', 'features', 'security'
        ]

        # Environment variable prefix
        self._env_prefix = 'CLAUDE_HOOKS_'

        # Initialize configuration
        self._setup_default_schemas()
        self._load_all_configs()

    def _setup_default_schemas(self):
        """Setup default configuration schemas."""
        # Main configuration schema
        self._validator.register_schema('main', {
            'type': 'object',
            'properties': {
                'debug': {'type': 'boolean'},
                'cache_ttl': {'type': 'integer', 'minimum': 30, 'maximum': 3600},
                'max_workers': {'type': 'integer', 'minimum': 1, 'maximum': 100}
            }
        })

        # Validator configuration schema
        self._validator.register_schema('validators', {
            'type': 'object',
            'patternProperties': {
                '.*': {
                    'type': 'object',
                    'properties': {
                        'enabled': {'type': 'boolean'},
                        'priority': {'type': 'integer'},
                        'config': {'type': 'object'}
                    },
                    'required': ['enabled']
                }
            }
        })

    def _load_all_configs(self):
        """Load all configuration files."""
        with self._lock:
            for section in self._sections:
                try:
                    self._load_section(section)
                except Exception as e:
                    self._logger.warning(f"Failed to load config section '{section}': {e}")
                    self._config_data[section] = {}

    def _load_section(self, section: str, force_reload: bool = False):
        """Load configuration section from file."""
        cache_key = f"config:{section}"

        # Check cache first
        if not force_reload:
            cached = self._cache.get(cache_key)
            if cached is not None:
                self._config_data[section] = cached
                return

        # Determine file paths to try
        possible_files = [
            self.config_dir / f"{section}.yaml",
            self.config_dir / f"{section}.yml",
            self.config_dir / f"{section}.json"
        ]

        config_data = {}
        loaded_file = None

        for file_path in possible_files:
            if file_path.exists():
                try:
                    config_data = self._load_file(file_path)
                    loaded_file = file_path
                    break
                except Exception as e:
                    self._logger.warning(f"Failed to load {file_path}: {e}")
                    continue

        if loaded_file:
            # Track file timestamp for change detection
            self._file_timestamps[section] = datetime.fromtimestamp(loaded_file.stat().st_mtime)

        # Apply environment variable overrides
        config_data = self._apply_env_overrides(section, config_data)

        # Validate configuration
        validation_errors = self._validator.validate(section, config_data)
        if validation_errors:
            error_msg = f"Configuration validation errors in section '{section}': {'; '.join(validation_errors)}"
            self._logger.error(error_msg)
            if self._config_data.get(section):
                self._logger.warning(f"Using previous configuration for section '{section}'")
                return
            else:
                raise ConfigurationError(error_msg, config_section=section)

        # Cache and store
        self._cache.set(cache_key, config_data)
        self._config_data[section] = config_data

        # Notify watchers
        self._notify_watchers(section, config_data)

    def _load_file(self, file_path: Path) -> Dict[str, Any]:
        """Load configuration from file."""
        try:
            with file_path.open('r', encoding='utf-8') as f:
                if file_path.suffix.lower() in ['.yaml', '.yml']:
                    return yaml.safe_load(f) or {}
                elif file_path.suffix.lower() == '.json':
                    return json.load(f) or {}
                else:
                    raise ConfigurationError(f"Unsupported config file format: {file_path.suffix}")
        except Exception as e:
            raise ConfigurationError(f"Failed to load config file {file_path}: {str(e)}", config_path=str(file_path)) from e

    def _apply_env_overrides(self, section: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply environment variable overrides to configuration."""
        env_prefix = f"{self._env_prefix}{section.upper()}_"

        # Create a copy to avoid modifying original
        result = config.copy()

        for env_key, env_value in os.environ.items():
            if env_key.startswith(env_prefix):
                # Convert environment key to config key
                config_key = env_key[len(env_prefix):].lower()

                # Try to parse the value
                try:
                    # Try JSON parsing first for complex values
                    parsed_value = json.loads(env_value)
                except json.JSONDecodeError:
                    # Fall back to string value
                    parsed_value = env_value

                result[config_key] = parsed_value
                self._logger.debug(f"Applied env override {env_key} -> {config_key}")

        return result

    def _notify_watchers(self, section: str, config: Dict[str, Any]):
        """Notify configuration change watchers."""
        for watcher in self._watchers:
            try:
                watcher(section, config)
            except Exception as e:
                self._logger.error(f"Configuration watcher error: {e}")

    def get(self, section: str, key: Optional[str] = None, default: Any = None) -> Any:
        """
        Get configuration value.

        Args:
            section: Configuration section
            key: Optional specific key within section
            default: Default value if not found

        Returns:
            Configuration value or default
        """
        if section not in self._config_data:
            return default

        section_data = self._config_data[section]

        if key is None:
            return section_data

        return section_data.get(key, default)

    def set(self, section: str, key: str, value: Any):
        """
        Set configuration value (runtime only, not persisted).

        Args:
            section: Configuration section
            key: Configuration key
            value: Value to set
        """
        with self._lock:
            if section not in self._config_data:
                self._config_data[section] = {}

            self._config_data[section][key] = value

            # Update cache
            cache_key = f"config:{section}"
            self._cache.set(cache_key, self._config_data[section])

            # Notify watchers
            self._notify_watchers(section, self._config_data[section])

    def reload(self, section: Optional[str] = None):
        """
        Reload configuration from files.

        Args:
            section: Specific section to reload (all if None)
        """
        if section:
            self._load_section(section, force_reload=True)
        else:
            self._load_all_configs()

    def add_watcher(self, watcher: Callable[[str, Dict[str, Any]], None]):
        """Add configuration change watcher."""
        self._watchers.append(watcher)

    def remove_watcher(self, watcher: Callable[[str, Dict[str, Any]], None]):
        """Remove configuration change watcher."""
        if watcher in self._watchers:
            self._watchers.remove(watcher)

    def register_schema(self, section: str, schema: Dict[str, Any]):
        """Register validation schema for configuration section."""
        self._validator.register_schema(section, schema)

    def check_for_changes(self) -> List[str]:
        """
        Check for configuration file changes.

        Returns:
            List of changed sections
        """
        changed_sections = []

        with self._lock:
            for section in self._sections:
                if section not in self._file_timestamps:
                    continue

                file_paths = [
                    self.config_dir / f"{section}.yaml",
                    self.config_dir / f"{section}.yml",
                    self.config_dir / f"{section}.json"
                ]

                current_file = None
                for file_path in file_paths:
                    if file_path.exists():
                        current_file = file_path
                        break

                if current_file:
                    file_mtime = datetime.fromtimestamp(current_file.stat().st_mtime)
                    if file_mtime > self._file_timestamps[section]:
                        changed_sections.append(section)

        return changed_sections

    def auto_reload_changed(self) -> List[str]:
        """
        Automatically reload changed configuration files.

        Returns:
            List of reloaded sections
        """
        changed_sections = self.check_for_changes()
        for section in changed_sections:
            try:
                self._load_section(section, force_reload=True)
                self._logger.info(f"Auto-reloaded configuration section: {section}")
            except Exception as e:
                self._logger.error(f"Failed to auto-reload section '{section}': {e}")

        return changed_sections

    # IConfigurable implementation
    def configure(self, config: Dict[str, Any]) -> None:
        """Configure the configuration manager itself."""
        if 'cache_ttl' in config:
            self._cache._default_ttl = config['cache_ttl']
        if 'env_prefix' in config:
            self._env_prefix = config['env_prefix']

    def get_config(self) -> Dict[str, Any]:
        """Get configuration manager configuration."""
        return {
            'cache_ttl': self._cache._default_ttl,
            'env_prefix': self._env_prefix,
            'config_dir': str(self.config_dir)
        }

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate configuration manager configuration."""
        try:
            if 'cache_ttl' in config:
                ttl = config['cache_ttl']
                if not isinstance(ttl, int) or ttl < 30:
                    return False
            return True
        except Exception:
            return False

    # IHealthCheck implementation
    def check_health(self) -> Dict[str, Any]:
        """Check configuration system health."""
        cache_stats = self._cache.get_stats()
        expired_count = self._cache.cleanup_expired()

        return {
            'status': 'healthy',
            'config_sections': len(self._config_data),
            'cache_stats': cache_stats,
            'expired_cleaned': expired_count,
            'watchers': len(self._watchers),
            'config_dir_exists': self.config_dir.exists()
        }

    def get_metrics(self) -> Dict[str, Union[int, float, str]]:
        """Get configuration system metrics."""
        cache_stats = self._cache.get_stats()
        hit_ratio = cache_stats['hits'] / max(cache_stats['hits'] + cache_stats['misses'], 1)

        return {
            'cache_hit_ratio': hit_ratio,
            'cache_entries': cache_stats['entries'],
            'config_sections': len(self._config_data),
            'watchers': len(self._watchers)
        }

    # Convenience properties for common configurations
    @property
    def main(self) -> Dict[str, Any]:
        """Get main configuration."""
        return self.get('main', default={})

    @property
    def messages(self) -> Dict[str, Any]:
        """Get messages configuration."""
        return self.get('messages', default={})

    @property
    def validators(self) -> Dict[str, Any]:
        """Get validators configuration."""
        return self.get('validators', default={})

    @property
    def processors(self) -> Dict[str, Any]:
        """Get processors configuration."""
        return self.get('processors', default={})

    @property
    def hint_providers(self) -> Dict[str, Any]:
        """Get hint providers configuration."""
        return self.get('hint_providers', default={})

    @property
    def features(self) -> Dict[str, Any]:
        """Get features configuration."""
        return self.get('features', default={})