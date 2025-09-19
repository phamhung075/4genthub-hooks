"""
Claude Hooks Core Factory System

This module provides the foundation for the Claude hooks system with a comprehensive
factory pattern, dependency injection, configuration management, and extensible
component architecture.

Key Features:
- Factory pattern for component creation with dependency injection
- Comprehensive interface definitions following SOLID principles
- Hierarchical configuration management with caching and validation
- Custom exception hierarchy for clear error handling
- Registry system for component registration and discovery
- Health checking and metrics collection
- Thread-safe operations with proper error handling

Usage:
    from claude.hooks.core import ComponentFactory, Config

    # Initialize configuration and factory
    config = Config()
    factory = ComponentFactory(config)

    # Register and create components
    factory.register_validator('my_validator', MyValidatorClass)
    validator = factory.create_validator('my_validator', config={'enabled': True})

    # Use factory for all component creation
    processors = factory.create_all_processors()
    hint_providers = factory.create_hint_providers()
"""

from .interfaces import (
    # Core interfaces
    IComponent,
    IValidator,
    IProcessor,
    ILogger,
    IHintProvider,

    # Utility interfaces
    IConfigurable,
    IRegistrable,
    IHealthCheck,
    IHookExecutor,
    ICache
)

from .factory import (
    # Factory classes
    ComponentFactory,
    ComponentRegistry,

    # Registration decorator
    register_component,

    # Global factory access
    get_default_factory,
    set_default_factory
)

from .config import (
    # Configuration management
    Config,
    ConfigCache,
    ConfigValidator
)

from .exceptions import (
    # Base exception
    HookException,

    # Specific exceptions
    ValidationError,
    ConfigurationError,
    ComponentError,
    RegistrationError,
    DependencyError,
    FactoryError,
    CacheError,
    SecurityError,
    TimeoutError,
    HookSystemError,

    # Utility functions
    create_exception,
    is_hook_exception,
    get_exception_context,

    # Exception registry
    EXCEPTION_REGISTRY
)

# Version information
__version__ = '1.0.0'
__author__ = 'Claude Hooks System'

# Public API
__all__ = [
    # Version
    '__version__',

    # Core interfaces
    'IComponent',
    'IValidator',
    'IProcessor',
    'ILogger',
    'IHintProvider',
    'IConfigurable',
    'IRegistrable',
    'IHealthCheck',
    'IHookExecutor',
    'ICache',

    # Factory system
    'ComponentFactory',
    'ComponentRegistry',
    'register_component',
    'get_default_factory',
    'set_default_factory',

    # Configuration system
    'Config',
    'ConfigCache',
    'ConfigValidator',

    # Exception system
    'HookException',
    'ValidationError',
    'ConfigurationError',
    'ComponentError',
    'RegistrationError',
    'DependencyError',
    'FactoryError',
    'CacheError',
    'SecurityError',
    'TimeoutError',
    'HookSystemError',
    'create_exception',
    'is_hook_exception',
    'get_exception_context',
    'EXCEPTION_REGISTRY'
]

# Module-level convenience functions
def create_factory_with_config(config_dir=None, cache_ttl=300):
    """
    Create a ComponentFactory with a Config instance.

    Args:
        config_dir: Optional configuration directory
        cache_ttl: Cache time-to-live in seconds

    Returns:
        Tuple of (factory, config)
    """
    config = Config(config_dir=config_dir, cache_ttl=cache_ttl)
    factory = ComponentFactory(config)
    return factory, config

def setup_default_factory(config_dir=None, cache_ttl=300):
    """
    Setup the default global factory with configuration.

    Args:
        config_dir: Optional configuration directory
        cache_ttl: Cache time-to-live in seconds

    Returns:
        The configured default factory
    """
    factory, config = create_factory_with_config(config_dir, cache_ttl)
    set_default_factory(factory)
    return factory

# Health check function for the entire core system
def check_core_system_health():
    """
    Check health of the entire core factory system.

    Returns:
        Dictionary with system health information
    """
    try:
        factory = get_default_factory()
        factory_health = factory.get_health_status()

        config_health = {}
        if hasattr(factory, 'config_manager') and factory.config_manager:
            config_health = factory.config_manager.check_health()

        return {
            'status': 'healthy',
            'factory_health': factory_health,
            'config_health': config_health,
            'core_version': __version__
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'core_version': __version__
        }

# Initialize logging for the core module
import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())