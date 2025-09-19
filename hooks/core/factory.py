"""
Component factory for creating and managing hook system components.

This module implements the factory pattern for creating validators, processors,
loggers, hint providers, and other hook components with proper registration,
dependency injection, and lifecycle management.
"""

import inspect
from typing import Dict, Any, List, Type, Optional, Callable, Union
from pathlib import Path
import logging
from functools import wraps

from .interfaces import (
    IComponent, IValidator, IProcessor, ILogger, IHintProvider,
    IConfigurable, IRegistrable, IHealthCheck, IHookExecutor, ICache
)
from .exceptions import (
    HookException, ValidationError, ConfigurationError, ComponentError,
    RegistrationError, DependencyError, FactoryError
)


class ComponentRegistry:
    """Registry for managing component classes and instances."""

    def __init__(self):
        self._validators: Dict[str, Type[IValidator]] = {}
        self._processors: Dict[str, Type[IProcessor]] = {}
        self._loggers: Dict[str, Type[ILogger]] = {}
        self._hint_providers: Dict[str, Type[IHintProvider]] = {}
        self._components: Dict[str, Type[IComponent]] = {}
        self._instances: Dict[str, Any] = {}
        self._dependencies: Dict[str, List[str]] = {}
        self._registration_order: List[str] = []

    def register(self, component_type: str, name: str, component_class: Type, dependencies: Optional[List[str]] = None):
        """
        Register a component class.

        Args:
            component_type: Type category ('validator', 'processor', 'logger', etc.)
            name: Unique component name
            component_class: Component class to register
            dependencies: Optional list of dependency names

        Raises:
            RegistrationError: If component cannot be registered
        """
        if not inspect.isclass(component_class):
            raise RegistrationError(f"Component {name} must be a class, got {type(component_class)}")

        dependencies = dependencies or []

        # Store in appropriate registry
        registry_map = {
            'validator': self._validators,
            'processor': self._processors,
            'logger': self._loggers,
            'hint_provider': self._hint_providers,
            'component': self._components
        }

        if component_type not in registry_map:
            raise RegistrationError(f"Unknown component type: {component_type}")

        registry = registry_map[component_type]

        if name in registry:
            raise RegistrationError(f"Component {name} already registered for type {component_type}")

        registry[name] = component_class
        self._dependencies[name] = dependencies
        self._registration_order.append(name)

        logging.debug(f"Registered {component_type} '{name}' with dependencies: {dependencies}")

    def get_class(self, component_type: str, name: str) -> Type:
        """
        Get registered component class.

        Args:
            component_type: Component type category
            name: Component name

        Returns:
            Component class

        Raises:
            ComponentError: If component not found
        """
        registry_map = {
            'validator': self._validators,
            'processor': self._processors,
            'logger': self._loggers,
            'hint_provider': self._hint_providers,
            'component': self._components
        }

        if component_type not in registry_map:
            raise ComponentError(f"Unknown component type: {component_type}")

        registry = registry_map[component_type]

        if name not in registry:
            raise ComponentError(f"Component '{name}' not found for type '{component_type}'")

        return registry[name]

    def list_components(self, component_type: Optional[str] = None) -> Dict[str, List[str]]:
        """
        List all registered components.

        Args:
            component_type: Optional filter by component type

        Returns:
            Dictionary mapping component types to lists of names
        """
        all_components = {
            'validator': list(self._validators.keys()),
            'processor': list(self._processors.keys()),
            'logger': list(self._loggers.keys()),
            'hint_provider': list(self._hint_providers.keys()),
            'component': list(self._components.keys())
        }

        if component_type:
            return {component_type: all_components.get(component_type, [])}

        return all_components

    def get_dependencies(self, name: str) -> List[str]:
        """Get component dependencies."""
        return self._dependencies.get(name, [])

    def resolve_dependency_order(self, names: List[str]) -> List[str]:
        """
        Resolve dependency order for component creation.

        Args:
            names: List of component names to resolve

        Returns:
            List of component names in dependency order

        Raises:
            DependencyError: If circular dependencies detected
        """
        ordered = []
        visited = set()
        visiting = set()

        def visit(name: str):
            if name in visiting:
                raise DependencyError(f"Circular dependency detected involving '{name}'")

            if name in visited:
                return

            visiting.add(name)

            for dep in self._dependencies.get(name, []):
                if dep in names:  # Only resolve dependencies that are in our target list
                    visit(dep)

            visiting.remove(name)
            visited.add(name)
            ordered.append(name)

        for name in names:
            visit(name)

        return ordered


class ComponentFactory:
    """Factory for creating hook components with dependency injection."""

    def __init__(self, config_manager=None):
        self.registry = ComponentRegistry()
        self.config_manager = config_manager
        self._singletons: Dict[str, Any] = {}
        self._cache: Optional[ICache] = None
        self._logger = logging.getLogger(__name__)

    def set_cache(self, cache: ICache):
        """Set cache instance for factory operations."""
        self._cache = cache

    def register_validator(self, name: str, validator_class: Type[IValidator], dependencies: Optional[List[str]] = None):
        """Register a validator class."""
        self._validate_interface(validator_class, IValidator, "validator")
        self.registry.register('validator', name, validator_class, dependencies)

    def register_processor(self, name: str, processor_class: Type[IProcessor], dependencies: Optional[List[str]] = None):
        """Register a processor class."""
        self._validate_interface(processor_class, IProcessor, "processor")
        self.registry.register('processor', name, processor_class, dependencies)

    def register_logger(self, name: str, logger_class: Type[ILogger], dependencies: Optional[List[str]] = None):
        """Register a logger class."""
        self._validate_interface(logger_class, ILogger, "logger")
        self.registry.register('logger', name, logger_class, dependencies)

    def register_hint_provider(self, name: str, provider_class: Type[IHintProvider], dependencies: Optional[List[str]] = None):
        """Register a hint provider class."""
        self._validate_interface(provider_class, IHintProvider, "hint provider")
        self.registry.register('hint_provider', name, provider_class, dependencies)

    def register_component(self, name: str, component_class: Type[IComponent], dependencies: Optional[List[str]] = None):
        """Register a generic component class."""
        self._validate_interface(component_class, IComponent, "component")
        self.registry.register('component', name, component_class, dependencies)

    def create_validator(self, name: str, config: Optional[Dict] = None, singleton: bool = False) -> IValidator:
        """Create validator instance."""
        return self._create_component('validator', name, config, singleton)

    def create_processor(self, name: str, config: Optional[Dict] = None, singleton: bool = False) -> IProcessor:
        """Create processor instance."""
        return self._create_component('processor', name, config, singleton)

    def create_logger(self, name: str, config: Optional[Dict] = None, singleton: bool = False) -> ILogger:
        """Create logger instance."""
        return self._create_component('logger', name, config, singleton)

    def create_hint_provider(self, name: str, config: Optional[Dict] = None, singleton: bool = False) -> IHintProvider:
        """Create hint provider instance."""
        return self._create_component('hint_provider', name, config, singleton)

    def create_component(self, name: str, config: Optional[Dict] = None, singleton: bool = False) -> IComponent:
        """Create generic component instance."""
        return self._create_component('component', name, config, singleton)

    def create_all_validators(self, config: Optional[Dict] = None) -> List[IValidator]:
        """Create all enabled validators."""
        validators = []
        config = config or (self.config_manager.validators if self.config_manager else {})

        for name, settings in config.items():
            if settings.get('enabled', True):
                try:
                    validator = self.create_validator(name, settings, settings.get('singleton', False))
                    validators.append(validator)
                except ComponentError as e:
                    self._logger.warning(f"Failed to create validator '{name}': {e}")
                    continue

        # Sort by priority if available
        validators.sort(key=lambda v: getattr(v, 'get_priority', lambda: 100)())
        return validators

    def create_all_processors(self, config: Optional[Dict] = None) -> List[IProcessor]:
        """Create all enabled processors."""
        processors = []
        config = config or (self.config_manager.processors if self.config_manager else {})

        for name, settings in config.items():
            if settings.get('enabled', True):
                try:
                    processor = self.create_processor(name, settings, settings.get('singleton', False))
                    processors.append(processor)
                except ComponentError as e:
                    self._logger.warning(f"Failed to create processor '{name}': {e}")
                    continue

        # Sort by priority
        processors.sort(key=lambda p: p.get_priority())
        return processors

    def create_hint_providers(self, config: Optional[Dict] = None) -> List[IHintProvider]:
        """Create all enabled hint providers."""
        providers = []
        config = config or (self.config_manager.hint_providers if self.config_manager else {})

        for name, settings in config.items():
            if settings.get('enabled', True):
                try:
                    provider = self.create_hint_provider(name, settings, settings.get('singleton', False))
                    providers.append(provider)
                except ComponentError as e:
                    self._logger.warning(f"Failed to create hint provider '{name}': {e}")
                    continue

        return providers

    def _create_component(self, component_type: str, name: str, config: Optional[Dict], singleton: bool) -> Any:
        """
        Internal component creation with dependency injection.

        Args:
            component_type: Type of component to create
            name: Component name
            config: Configuration dictionary
            singleton: Whether to create as singleton

        Returns:
            Component instance

        Raises:
            ComponentError: If component creation fails
        """
        cache_key = f"{component_type}:{name}"

        # Check singleton cache
        if singleton and cache_key in self._singletons:
            return self._singletons[cache_key]

        # Check external cache
        if self._cache and not singleton:
            cached = self._cache.get(cache_key)
            if cached is not None:
                return cached

        try:
            # Get component class
            component_class = self.registry.get_class(component_type, name)

            # Resolve dependencies
            dependencies = self._resolve_dependencies(name)

            # Create instance
            instance = self._instantiate_component(component_class, config, dependencies)

            # Cache if needed
            if singleton:
                self._singletons[cache_key] = instance
            elif self._cache:
                self._cache.set(cache_key, instance, ttl=3600)  # 1 hour TTL

            self._logger.debug(f"Created {component_type} '{name}'")
            return instance

        except Exception as e:
            raise ComponentError(f"Failed to create {component_type} '{name}': {str(e)}") from e

    def _resolve_dependencies(self, name: str) -> Dict[str, Any]:
        """Resolve component dependencies."""
        dependencies = {}
        for dep_name in self.registry.get_dependencies(name):
            # Try to find dependency in any component type
            for comp_type in ['validator', 'processor', 'logger', 'hint_provider', 'component']:
                try:
                    dependencies[dep_name] = self._create_component(comp_type, dep_name, None, True)
                    break
                except ComponentError:
                    continue
            else:
                raise DependencyError(f"Dependency '{dep_name}' not found for component '{name}'")

        return dependencies

    def _instantiate_component(self, component_class: Type, config: Optional[Dict], dependencies: Dict[str, Any]) -> Any:
        """Instantiate component with proper configuration and dependencies."""
        # Get constructor signature
        sig = inspect.signature(component_class.__init__)
        init_params = {}

        # Handle constructor parameters
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue

            if param_name == 'config' and config is not None:
                init_params['config'] = config
            elif param_name in dependencies:
                init_params[param_name] = dependencies[param_name]
            elif param.default is not inspect.Parameter.empty:
                continue  # Use default value
            else:
                self._logger.warning(f"No value provided for required parameter '{param_name}'")

        # Create instance
        instance = component_class(**init_params)

        # Configure if configurable
        if isinstance(instance, IConfigurable) and config is not None:
            if instance.validate_config(config):
                instance.configure(config)
            else:
                raise ConfigurationError(f"Invalid configuration for component {component_class.__name__}")

        return instance

    def _validate_interface(self, component_class: Type, interface: Type, component_type: str):
        """Validate that component class implements required interface."""
        if not issubclass(component_class, interface):
            raise RegistrationError(
                f"{component_type.title()} class {component_class.__name__} must implement {interface.__name__}"
            )

    def get_health_status(self) -> Dict[str, Any]:
        """Get factory and component health status."""
        status = {
            'factory_status': 'healthy',
            'registered_components': self.registry.list_components(),
            'singleton_count': len(self._singletons),
            'component_health': {}
        }

        # Check health of singleton components
        for key, instance in self._singletons.items():
            if isinstance(instance, IHealthCheck):
                try:
                    comp_health = instance.check_health()
                    status['component_health'][key] = comp_health
                except Exception as e:
                    status['component_health'][key] = {'status': 'error', 'error': str(e)}

        return status

    def cleanup(self):
        """Cleanup factory resources."""
        self._singletons.clear()
        if self._cache:
            self._cache.invalidate("validator:*")
            self._cache.invalidate("processor:*")
            self._cache.invalidate("logger:*")
            self._cache.invalidate("hint_provider:*")
            self._cache.invalidate("component:*")


# Decorator for automatic component registration
def register_component(component_type: str, name: str, dependencies: Optional[List[str]] = None, factory: Optional[ComponentFactory] = None):
    """Decorator for automatic component registration."""
    def decorator(cls):
        if factory:
            register_method = getattr(factory, f'register_{component_type}', None)
            if register_method:
                register_method(name, cls, dependencies)
            else:
                raise RegistrationError(f"Unknown component type for registration: {component_type}")

        # Add metadata to class
        cls._component_type = component_type
        cls._component_name = name
        cls._component_dependencies = dependencies or []

        return cls
    return decorator


# Global factory instance
_default_factory = ComponentFactory()

def get_default_factory() -> ComponentFactory:
    """Get the default global factory instance."""
    return _default_factory

def set_default_factory(factory: ComponentFactory):
    """Set the default global factory instance."""
    global _default_factory
    _default_factory = factory