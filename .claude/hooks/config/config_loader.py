"""
Configuration loader for Claude hooks.
Provides centralized access to all configuration files in the config directory.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ConfigLoader:
    """Centralized configuration loader for hook system."""

    def __init__(self):
        """Initialize the config loader."""
        self.config_dir = Path(__file__).parent
        self._cache = {}

    def load_config(self, config_name: str, use_cache: bool = True) -> Optional[Dict[str, Any]]:
        """
        Load a configuration file from the config directory.

        Args:
            config_name: Name of the config file (without .yaml extension)
            use_cache: Whether to use cached version if available

        Returns:
            Dictionary containing configuration data or None if file doesn't exist
        """
        if use_cache and config_name in self._cache:
            return self._cache[config_name]

        config_path = self.config_dir / f"{config_name}.yaml"

        if not config_path.exists():
            logger.warning(f"Configuration file not found: {config_path}")
            return None

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)

            if use_cache:
                self._cache[config_name] = config_data

            logger.debug(f"Loaded configuration: {config_name}")
            return config_data

        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML file {config_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error loading configuration {config_path}: {e}")
            return None

    def get_mcp_post_hints_config(self) -> Optional[Dict[str, Any]]:
        """Get MCP post-action hints configuration."""
        return self.load_config("mcp_post_action_hints")

    def get_session_start_config(self) -> Optional[Dict[str, Any]]:
        """Get session start messages configuration."""
        return self.load_config("session_start_messages")

    def get_hint_message_config(self, message_type: str) -> Optional[Dict[str, Any]]:
        """
        Get hint message configuration for a specific type.

        Args:
            message_type: Type of hint messages (e.g., 'pre_tool_use', 'post_tool_use')

        Returns:
            Configuration dictionary or None
        """
        return self.load_config(f"__hint_message__{message_type}")

    def clear_cache(self):
        """Clear the configuration cache."""
        self._cache.clear()
        logger.debug("Configuration cache cleared")

    def reload_config(self, config_name: str) -> Optional[Dict[str, Any]]:
        """
        Force reload a configuration file, bypassing cache.

        Args:
            config_name: Name of the config file to reload

        Returns:
            Reloaded configuration data
        """
        return self.load_config(config_name, use_cache=False)

# Global instance
_config_loader = None

def get_config_loader() -> ConfigLoader:
    """Get the global configuration loader instance."""
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader()
    return _config_loader

def load_mcp_hints_config() -> Optional[Dict[str, Any]]:
    """Convenience function to load MCP post-action hints configuration."""
    loader = get_config_loader()
    return loader.get_mcp_post_hints_config()

def load_session_messages_config() -> Optional[Dict[str, Any]]:
    """Convenience function to load session start messages configuration."""
    loader = get_config_loader()
    return loader.get_session_start_config()

def load_hint_messages_config(message_type: str) -> Optional[Dict[str, Any]]:
    """Convenience function to load hint message configuration."""
    loader = get_config_loader()
    return loader.get_hint_message_config(message_type)