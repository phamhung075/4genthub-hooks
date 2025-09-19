"""
Core interfaces for the Claude hooks system.

This module defines the abstract base classes that establish contracts for all
hook components including validators, processors, loggers, and hint providers.
Following SOLID principles for maintainable and extensible architecture.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
import logging


class IComponent(ABC):
    """Base component interface for all hook components."""

    @abstractmethod
    def process(self, tool_name: str, tool_input: Dict, tool_result: Any) -> Optional[Any]:
        """
        Process hook data and return optional result.

        Args:
            tool_name: Name of the tool being executed
            tool_input: Input parameters for the tool
            tool_result: Result returned by the tool

        Returns:
            Optional processed result
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Get component name for identification."""
        pass

    @abstractmethod
    def is_enabled(self) -> bool:
        """Check if component is enabled."""
        pass


class IValidator(ABC):
    """Validation interface for data validation components."""

    @abstractmethod
    def validate(self, data: Dict[str, Any]) -> bool:
        """
        Validate input data according to specific rules.

        Args:
            data: Data dictionary to validate

        Returns:
            True if validation passes, False otherwise
        """
        pass

    @abstractmethod
    def get_error(self) -> str:
        """
        Get validation error message.

        Returns:
            Human-readable error message
        """
        pass

    @abstractmethod
    def get_severity(self) -> str:
        """
        Get error severity level.

        Returns:
            Severity level: 'error', 'warning', 'info'
        """
        pass


class IProcessor(ABC):
    """Processing interface for data transformation components."""

    @abstractmethod
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process and potentially transform data.

        Args:
            data: Input data dictionary

        Returns:
            Processed data dictionary
        """
        pass

    @abstractmethod
    def get_priority(self) -> int:
        """
        Get processing priority (lower number = higher priority).

        Returns:
            Priority value for execution ordering
        """
        pass

    @abstractmethod
    def can_process(self, data: Dict[str, Any]) -> bool:
        """
        Check if processor can handle the given data.

        Args:
            data: Input data to check

        Returns:
            True if processor can handle the data
        """
        pass


class ILogger(ABC):
    """Logging interface for consistent logging across components."""

    @abstractmethod
    def log(self, level: str, message: str, data: Optional[Dict] = None, context: Optional[Dict] = None):
        """
        Log message with optional data and context.

        Args:
            level: Log level ('debug', 'info', 'warning', 'error', 'critical')
            message: Log message
            data: Optional structured data to include
            context: Optional context information
        """
        pass

    @abstractmethod
    def set_context(self, context: Dict[str, Any]) -> None:
        """
        Set logging context for subsequent log entries.

        Args:
            context: Context information to include in logs
        """
        pass

    @abstractmethod
    def get_log_level(self) -> str:
        """
        Get current log level.

        Returns:
            Current log level string
        """
        pass


class IHintProvider(ABC):
    """Hint generation interface for contextual assistance."""

    @abstractmethod
    def generate_hints(self, context: Dict[str, Any]) -> List[str]:
        """
        Generate contextual hints based on current state.

        Args:
            context: Current context information

        Returns:
            List of hint messages
        """
        pass

    @abstractmethod
    def get_hint_types(self) -> List[str]:
        """
        Get types of hints this provider can generate.

        Returns:
            List of hint type identifiers
        """
        pass

    @abstractmethod
    def should_trigger(self, context: Dict[str, Any]) -> bool:
        """
        Determine if hints should be generated for current context.

        Args:
            context: Current context to evaluate

        Returns:
            True if hints should be generated
        """
        pass


class IConfigurable(ABC):
    """Configuration interface for components that accept configuration."""

    @abstractmethod
    def configure(self, config: Dict[str, Any]) -> None:
        """
        Configure component with provided settings.

        Args:
            config: Configuration dictionary
        """
        pass

    @abstractmethod
    def get_config(self) -> Dict[str, Any]:
        """
        Get current configuration.

        Returns:
            Current configuration dictionary
        """
        pass

    @abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate configuration before applying.

        Args:
            config: Configuration to validate

        Returns:
            True if configuration is valid
        """
        pass


class IRegistrable(ABC):
    """Interface for components that can be registered with the factory."""

    @abstractmethod
    def get_registration_key(self) -> str:
        """
        Get unique key for factory registration.

        Returns:
            Unique registration identifier
        """
        pass

    @abstractmethod
    def get_dependencies(self) -> List[str]:
        """
        Get list of component dependencies.

        Returns:
            List of dependency registration keys
        """
        pass


class IHealthCheck(ABC):
    """Health check interface for system monitoring."""

    @abstractmethod
    def check_health(self) -> Dict[str, Any]:
        """
        Perform health check and return status.

        Returns:
            Health status dictionary with status, message, and metrics
        """
        pass

    @abstractmethod
    def get_metrics(self) -> Dict[str, Union[int, float, str]]:
        """
        Get component performance metrics.

        Returns:
            Dictionary of metrics
        """
        pass


class IHookExecutor(ABC):
    """Interface for hook execution orchestration."""

    @abstractmethod
    def execute_pre_hook(self, tool_name: str, tool_input: Dict) -> Optional[Dict]:
        """
        Execute pre-tool hooks.

        Args:
            tool_name: Name of the tool about to be executed
            tool_input: Input parameters for the tool

        Returns:
            Optional modified input or execution control data
        """
        pass

    @abstractmethod
    def execute_post_hook(self, tool_name: str, tool_input: Dict, tool_result: Any) -> Optional[Any]:
        """
        Execute post-tool hooks.

        Args:
            tool_name: Name of the executed tool
            tool_input: Original input parameters
            tool_result: Tool execution result

        Returns:
            Optional modified result or additional data
        """
        pass

    @abstractmethod
    def register_hook(self, hook_type: str, component: IComponent) -> None:
        """
        Register a hook component.

        Args:
            hook_type: Type of hook ('pre' or 'post')
            component: Hook component to register
        """
        pass


class ICache(ABC):
    """Cache interface for performance optimization."""

    @abstractmethod
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get value from cache.

        Args:
            key: Cache key
            default: Default value if key not found

        Returns:
            Cached value or default
        """
        pass

    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (None for no expiration)
        """
        pass

    @abstractmethod
    def invalidate(self, pattern: Optional[str] = None) -> None:
        """
        Invalidate cache entries.

        Args:
            pattern: Optional pattern to match keys (None invalidates all)
        """
        pass

    @abstractmethod
    def get_stats(self) -> Dict[str, int]:
        """
        Get cache statistics.

        Returns:
            Dictionary with hits, misses, evictions, etc.
        """
        pass