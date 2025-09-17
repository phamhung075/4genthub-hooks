"""
Custom exception hierarchy for the Claude hooks system.

This module defines all custom exceptions used throughout the hook system,
providing clear error handling and debugging information with proper
exception chaining and context preservation.
"""

from typing import Optional, Dict, Any, List


class HookException(Exception):
    """
    Base exception for all hook system errors.

    Provides common functionality for all hook-related exceptions including
    error context preservation and structured error reporting.
    """

    def __init__(self, message: str, error_code: Optional[str] = None, context: Optional[Dict[str, Any]] = None, cause: Optional[Exception] = None):
        """
        Initialize hook exception.

        Args:
            message: Error description
            error_code: Optional error code for programmatic handling
            context: Optional context information
            cause: Optional underlying cause exception
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__.upper()
        self.context = context or {}
        self.cause = cause

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for serialization."""
        return {
            'exception_type': self.__class__.__name__,
            'message': self.message,
            'error_code': self.error_code,
            'context': self.context,
            'cause': str(self.cause) if self.cause else None
        }

    def __str__(self) -> str:
        """String representation with context."""
        parts = [self.message]
        if self.error_code and self.error_code != self.__class__.__name__.upper():
            parts.append(f"[{self.error_code}]")
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            parts.append(f"Context: {context_str}")
        return " | ".join(parts)


class ValidationError(HookException):
    """
    Validation failed exception.

    Raised when data validation fails, providing detailed information
    about what validation rules were violated.
    """

    def __init__(self, message: str, validator_name: Optional[str] = None,
                 validation_rules: Optional[List[str]] = None,
                 invalid_data: Optional[Dict[str, Any]] = None,
                 severity: str = "error", **kwargs):
        """
        Initialize validation error.

        Args:
            message: Validation error description
            validator_name: Name of the validator that failed
            validation_rules: List of violated validation rules
            invalid_data: Data that failed validation
            severity: Error severity level
            **kwargs: Additional context for base exception
        """
        context = kwargs.get('context', {})
        context.update({
            'validator_name': validator_name,
            'validation_rules': validation_rules or [],
            'invalid_data': invalid_data,
            'severity': severity
        })
        kwargs['context'] = context
        super().__init__(message, **kwargs)

        self.validator_name = validator_name
        self.validation_rules = validation_rules or []
        self.invalid_data = invalid_data
        self.severity = severity


class ConfigurationError(HookException):
    """
    Configuration error exception.

    Raised when configuration is invalid, missing, or cannot be loaded.
    """

    def __init__(self, message: str, config_path: Optional[str] = None,
                 config_section: Optional[str] = None,
                 invalid_keys: Optional[List[str]] = None, **kwargs):
        """
        Initialize configuration error.

        Args:
            message: Configuration error description
            config_path: Path to configuration file
            config_section: Configuration section with error
            invalid_keys: List of invalid configuration keys
            **kwargs: Additional context for base exception
        """
        context = kwargs.get('context', {})
        context.update({
            'config_path': config_path,
            'config_section': config_section,
            'invalid_keys': invalid_keys or []
        })
        kwargs['context'] = context
        super().__init__(message, **kwargs)

        self.config_path = config_path
        self.config_section = config_section
        self.invalid_keys = invalid_keys or []


class ComponentError(HookException):
    """
    Component processing error exception.

    Raised when a hook component fails to process data or encounters
    an error during execution.
    """

    def __init__(self, message: str, component_name: Optional[str] = None,
                 component_type: Optional[str] = None,
                 processing_stage: Optional[str] = None, **kwargs):
        """
        Initialize component error.

        Args:
            message: Component error description
            component_name: Name of the failing component
            component_type: Type of component (validator, processor, etc.)
            processing_stage: Stage where error occurred
            **kwargs: Additional context for base exception
        """
        context = kwargs.get('context', {})
        context.update({
            'component_name': component_name,
            'component_type': component_type,
            'processing_stage': processing_stage
        })
        kwargs['context'] = context
        super().__init__(message, **kwargs)

        self.component_name = component_name
        self.component_type = component_type
        self.processing_stage = processing_stage


class RegistrationError(HookException):
    """
    Component registration error exception.

    Raised when component registration fails due to invalid components,
    duplicate names, or registration system errors.
    """

    def __init__(self, message: str, component_name: Optional[str] = None,
                 component_type: Optional[str] = None,
                 registration_conflict: Optional[str] = None, **kwargs):
        """
        Initialize registration error.

        Args:
            message: Registration error description
            component_name: Name of component being registered
            component_type: Type of component being registered
            registration_conflict: Description of registration conflict
            **kwargs: Additional context for base exception
        """
        context = kwargs.get('context', {})
        context.update({
            'component_name': component_name,
            'component_type': component_type,
            'registration_conflict': registration_conflict
        })
        kwargs['context'] = context
        super().__init__(message, **kwargs)

        self.component_name = component_name
        self.component_type = component_type
        self.registration_conflict = registration_conflict


class DependencyError(HookException):
    """
    Dependency resolution error exception.

    Raised when component dependencies cannot be resolved, including
    circular dependencies, missing dependencies, or dependency conflicts.
    """

    def __init__(self, message: str, component_name: Optional[str] = None,
                 missing_dependencies: Optional[List[str]] = None,
                 circular_dependencies: Optional[List[str]] = None, **kwargs):
        """
        Initialize dependency error.

        Args:
            message: Dependency error description
            component_name: Name of component with dependency issues
            missing_dependencies: List of missing dependency names
            circular_dependencies: List of components in circular dependency
            **kwargs: Additional context for base exception
        """
        context = kwargs.get('context', {})
        context.update({
            'component_name': component_name,
            'missing_dependencies': missing_dependencies or [],
            'circular_dependencies': circular_dependencies or []
        })
        kwargs['context'] = context
        super().__init__(message, **kwargs)

        self.component_name = component_name
        self.missing_dependencies = missing_dependencies or []
        self.circular_dependencies = circular_dependencies or []


class FactoryError(HookException):
    """
    Factory system error exception.

    Raised when the component factory encounters errors in component
    creation, management, or lifecycle operations.
    """

    def __init__(self, message: str, operation: Optional[str] = None,
                 component_name: Optional[str] = None,
                 factory_state: Optional[str] = None, **kwargs):
        """
        Initialize factory error.

        Args:
            message: Factory error description
            operation: Factory operation that failed
            component_name: Name of component involved in error
            factory_state: Current state of factory
            **kwargs: Additional context for base exception
        """
        context = kwargs.get('context', {})
        context.update({
            'operation': operation,
            'component_name': component_name,
            'factory_state': factory_state
        })
        kwargs['context'] = context
        super().__init__(message, **kwargs)

        self.operation = operation
        self.component_name = component_name
        self.factory_state = factory_state


class CacheError(HookException):
    """
    Cache system error exception.

    Raised when cache operations fail, including cache connectivity,
    serialization, or storage issues.
    """

    def __init__(self, message: str, cache_operation: Optional[str] = None,
                 cache_key: Optional[str] = None,
                 cache_backend: Optional[str] = None, **kwargs):
        """
        Initialize cache error.

        Args:
            message: Cache error description
            cache_operation: Cache operation that failed
            cache_key: Cache key involved in error
            cache_backend: Type of cache backend
            **kwargs: Additional context for base exception
        """
        context = kwargs.get('context', {})
        context.update({
            'cache_operation': cache_operation,
            'cache_key': cache_key,
            'cache_backend': cache_backend
        })
        kwargs['context'] = context
        super().__init__(message, **kwargs)

        self.cache_operation = cache_operation
        self.cache_key = cache_key
        self.cache_backend = cache_backend


class SecurityError(HookException):
    """
    Security-related error exception.

    Raised when security violations or security-related failures occur
    in the hook system.
    """

    def __init__(self, message: str, security_check: Optional[str] = None,
                 violation_type: Optional[str] = None,
                 security_context: Optional[Dict[str, Any]] = None, **kwargs):
        """
        Initialize security error.

        Args:
            message: Security error description
            security_check: Name of security check that failed
            violation_type: Type of security violation
            security_context: Security-related context information
            **kwargs: Additional context for base exception
        """
        context = kwargs.get('context', {})
        context.update({
            'security_check': security_check,
            'violation_type': violation_type,
            'security_context': security_context or {}
        })
        kwargs['context'] = context
        super().__init__(message, **kwargs)

        self.security_check = security_check
        self.violation_type = violation_type
        self.security_context = security_context or {}


class TimeoutError(HookException):
    """
    Operation timeout error exception.

    Raised when hook operations exceed their configured timeout limits.
    """

    def __init__(self, message: str, operation: Optional[str] = None,
                 timeout_seconds: Optional[float] = None,
                 elapsed_seconds: Optional[float] = None, **kwargs):
        """
        Initialize timeout error.

        Args:
            message: Timeout error description
            operation: Operation that timed out
            timeout_seconds: Configured timeout limit
            elapsed_seconds: Actual elapsed time
            **kwargs: Additional context for base exception
        """
        context = kwargs.get('context', {})
        context.update({
            'operation': operation,
            'timeout_seconds': timeout_seconds,
            'elapsed_seconds': elapsed_seconds
        })
        kwargs['context'] = context
        super().__init__(message, **kwargs)

        self.operation = operation
        self.timeout_seconds = timeout_seconds
        self.elapsed_seconds = elapsed_seconds


class HookSystemError(HookException):
    """
    System-level hook error exception.

    Raised when fundamental hook system failures occur that affect
    the overall operation of the hook system.
    """

    def __init__(self, message: str, system_component: Optional[str] = None,
                 recovery_possible: bool = True,
                 system_state: Optional[Dict[str, Any]] = None, **kwargs):
        """
        Initialize hook system error.

        Args:
            message: System error description
            system_component: Component that failed
            recovery_possible: Whether recovery is possible
            system_state: Current system state information
            **kwargs: Additional context for base exception
        """
        context = kwargs.get('context', {})
        context.update({
            'system_component': system_component,
            'recovery_possible': recovery_possible,
            'system_state': system_state or {}
        })
        kwargs['context'] = context
        super().__init__(message, **kwargs)

        self.system_component = system_component
        self.recovery_possible = recovery_possible
        self.system_state = system_state or {}


# Exception mapping for programmatic access
EXCEPTION_REGISTRY = {
    'hook': HookException,
    'validation': ValidationError,
    'configuration': ConfigurationError,
    'component': ComponentError,
    'registration': RegistrationError,
    'dependency': DependencyError,
    'factory': FactoryError,
    'cache': CacheError,
    'security': SecurityError,
    'timeout': TimeoutError,
    'system': HookSystemError
}


def create_exception(exception_type: str, message: str, **kwargs) -> HookException:
    """
    Factory function to create exceptions by type name.

    Args:
        exception_type: Type of exception to create
        message: Error message
        **kwargs: Additional exception parameters

    Returns:
        Exception instance

    Raises:
        ValueError: If exception type is not recognized
    """
    if exception_type not in EXCEPTION_REGISTRY:
        raise ValueError(f"Unknown exception type: {exception_type}")

    return EXCEPTION_REGISTRY[exception_type](message, **kwargs)


def is_hook_exception(exc: Exception) -> bool:
    """
    Check if exception is a hook system exception.

    Args:
        exc: Exception to check

    Returns:
        True if exception is from hook system
    """
    return isinstance(exc, HookException)


def get_exception_context(exc: Exception) -> Dict[str, Any]:
    """
    Extract context from hook exception.

    Args:
        exc: Exception to extract context from

    Returns:
        Context dictionary (empty if not a hook exception)
    """
    if isinstance(exc, HookException):
        return exc.context.copy()
    return {}