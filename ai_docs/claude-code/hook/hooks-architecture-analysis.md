# Claude Hooks System Architecture Analysis

## Overview
The `.claude/hooks` directory contains a complex hook system with both legacy and clean architecture implementations running in parallel. This creates maintenance challenges and confusion.

## Current Structure

### Main Hook Files (Active)
- **pre_tool_use.py** (345 lines) - Validates tool usage before execution
- **post_tool_use.py** (345 lines) - Processes results after tool execution
- **session_start.py** - Initializes session context
- **user_prompt_submit.py** - Processes user prompts

### Directory Structure
```
.claude/hooks/
├── config/                    # YAML configuration files (24 files)
├── core_clean_arch/           # Clean architecture attempt (unused)
├── hints_clean_arch/          # Clean hint providers (unused)
├── processors_clean_arch/     # Clean processors (unused)
├── validators_clean_arch/     # Clean validators (unused)
├── utils/                     # Active utility modules (23 files)
├── backup_20250912_121713/    # Previous version backup
└── data/                      # Runtime data storage
```

## Architecture Problems

### 1. Duplicate Architecture Patterns
- **Active System**: Traditional monolithic hooks using `utils/` modules
- **Clean Architecture**: Incomplete SOLID-based system in `*_clean_arch/` directories
- **Result**: Two parallel systems, only one working

### 2. Module Proliferation
The `utils/` directory has 23 modules with overlapping responsibilities:
- Multiple hint systems: `hint_analyzer.py`, `hint_bridge.py`, `mcp_hint_matrix.py`
- Multiple MCP handlers: `mcp_client.py`, `mcp_task_interceptor.py`, `mcp_task_validator.py`
- Multiple context managers: `context_injector.py`, `context_synchronizer.py`, `context_updater.py`

### 3. Configuration Complexity
24 YAML configuration files in `config/` directory:
- Separate files for each message type
- No clear hierarchy or inheritance
- Redundant configuration across files

### 4. Import Dependencies
Complex import chains make the system fragile:
```python
pre_tool_use.py → utils/env_loader.py
                → utils/config_factory.py
                → utils/docs_indexer.py
                → utils/session_tracker.py
                → utils/context_injector.py (optional)
                → utils/mcp_task_interceptor.py (optional)
                → utils/agent_delegator.py (optional)
                → utils/hint_analyzer.py (optional)
                → utils/hint_bridge.py (optional)
```

## Key Components Analysis

### pre_tool_use.py
**Purpose**: Validates tool usage before execution
**Key Functions**:
- File system protection
- Documentation enforcement
- Dangerous command prevention
- MCP task validation
- Agent context injection

**Problems**:
- 800+ lines of procedural code
- Multiple try/except blocks for optional imports
- Mixed responsibilities (validation + hints + logging)

### post_tool_use.py
**Purpose**: Post-processes tool execution results
**Key Functions**:
- Documentation index updates
- Context synchronization
- Agent state tracking
- Hint generation and storage
- Logging

**Problems**:
- Duplicate logging logic
- Complex conditional imports
- Mixed concerns

### utils/config_factory.py
**Purpose**: Centralized configuration loading
**Good**: Single factory for configuration
**Problems**:
- Tries to handle too many message types
- Complex caching logic
- No type safety

## Maintenance Recommendations

### 1. Remove Incomplete Clean Architecture
Delete these unused directories to reduce confusion:
- `core_clean_arch/`
- `hints_clean_arch/`
- `processors_clean_arch/`
- `validators_clean_arch/`
- `post_tool_use_clean.py` (already removed)
- `pre_tool_use_clean.py` (if exists)

### 2. Consolidate Utils Modules
Merge related functionality:
- **Hint System**: Combine hint_analyzer, hint_bridge, mcp_hint_matrix into single `hint_manager.py`
- **Context System**: Merge context_injector, context_synchronizer, context_updater into `context_manager.py`
- **MCP System**: Combine MCP-related modules into `mcp_manager.py`

### 3. Implement Factory Pattern
Create a single factory for component initialization:
```python
class HookComponentFactory:
    @staticmethod
    def create_validator(config): ...
    @staticmethod
    def create_hint_manager(config): ...
    @staticmethod
    def create_logger(config): ...
    @staticmethod
    def create_context_manager(config): ...
```

### 4. Simplify Configuration
- Consolidate 24 YAML files into 3-4 main configs
- Use inheritance for message types
- Implement type-safe configuration classes

### 5. Refactor Hook Structure
Transform monolithic hooks into modular components:
```python
class PreToolUseHook:
    def __init__(self):
        self.validator = factory.create_validator()
        self.hint_manager = factory.create_hint_manager()
        self.logger = factory.create_logger()

    def execute(self, tool_name, tool_input):
        # Clean, single-responsibility execution
        if not self.validator.validate(tool_name, tool_input):
            return self.validator.get_error()
        # ...
```

## Priority Actions

1. **Immediate**: Remove unused clean architecture directories
2. **Short-term**: Consolidate duplicate utils modules
3. **Medium-term**: Implement factory pattern for component creation
4. **Long-term**: Refactor hooks into class-based architecture

## Complexity Metrics

- **Total Python files**: 45+
- **Total YAML configs**: 24
- **Lines of code**: ~5000+
- **Import dependencies**: 50+
- **Duplicate functionality**: ~40%

## Conclusion

The current hook system works but is overly complex with duplicate architectures, redundant modules, and mixed responsibilities. A systematic refactoring using factory patterns and SOLID principles would significantly improve maintainability while preserving all functionality.