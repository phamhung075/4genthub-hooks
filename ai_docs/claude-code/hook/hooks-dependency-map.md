# Hooks System Dependency Map

## Current Main Hooks (2024-09-17)

### pre_tool_use.py (528 lines)
**Refactored architecture with factory pattern and clean separation:**
- Standard library: `json`, `sys`, `re`, `datetime`, `pathlib.Path`, `typing`, `abc`
- Utils dependencies (dynamic imports in factory methods):
  - `utils.config_factory`: `get_error_message`, `get_warning_message`
  - `utils.docs_indexer`: `check_documentation_requirement`
  - `utils.session_tracker`: `is_file_in_session`
  - `utils.role_enforcer`: `check_tool_permission`
  - `utils.context_injector`: `inject_context_sync`
  - `utils.unified_hint_system`: `get_hint_system`
  - `utils.mcp_task_interceptor`: `get_mcp_interceptor`
  - `utils.env_loader`: `get_ai_data_path`

### post_tool_use.py (361 lines)
**Refactored with component-based architecture:**
- Standard library: `json`, `sys`, `pathlib.Path`, `datetime`, `typing`, `abc`
- Utils dependencies (dynamic imports):
  - `utils.docs_indexer`: `update_index`
  - `utils.unified_hint_system`: `generate_post_action_hints`, `store_hint_for_later`, `get_hint_system`
  - `utils.agent_state_manager`: `update_agent_state_from_call_agent`
  - `utils.context_updater`: `update_context_sync`
  - `utils.env_loader`: `get_ai_data_path`

### session_start.py (991 lines)
**Comprehensive session initialization:**
- Standard library: `json`, `sys`, `subprocess`, `os`, `argparse`, `yaml`, `pathlib.Path`, `datetime`, `typing`, `abc`
- Utils dependencies (factory-based):
  - `utils.env_loader`: Environment configuration
  - `utils.cache_manager`: Session management
  - `utils.config_factory`: Configuration handling
  - `utils.mcp_client`: MCP connection management

### user_prompt_submit.py (529 lines)
**Prompt processing and validation:**
- Standard library: Similar to other hooks
- Utils dependencies: Pattern matches other hooks

### Additional Hook Files:
- **migrate_data.py** (163 lines) - Data migration utilities
- **notification.py** (134 lines) - Notification system
- **pre_compact.py** (128 lines) - Pre-compaction hook
- **stop.py** (235 lines) - Shutdown handling
- **subagent_stop.py** (156 lines) - Subagent termination

## Current Utils Module Organization (2024-09-17)

### Core Infrastructure (22 modules, ~6K lines total)
**No circular dependencies - Clean architecture maintained**

#### System Core (No dependencies)
- `env_loader.py` (116 lines) - Environment variable loading and validation
- `config_factory.py` (309 lines) - Configuration and message management

#### Context Management (Major refactoring completed)
- `context_injector.py` (740 lines) - Context injection with sync capabilities
- `context_synchronizer.py` (603 lines) - Multi-tier context synchronization
- `context_updater.py` (619 lines) - Context update operations

#### Unified Hint System (Consolidation completed)
- `unified_hint_system.py` (410 lines) - **Consolidated from multiple hint modules**
- `hint_bridge.py` (47 lines) - Lightweight hint bridging
- `mcp_post_action_hints.py` (27 lines) - **Simplified, backup available (329 lines)**
- `post_action_display.py` (65 lines) - Display formatting

#### Agent Management
- `agent_context_manager.py` (213 lines) - Agent context handling
- `agent_delegator.py` (239 lines) - Agent delegation logic
- `agent_helpers.py` (66 lines) - Agent utility functions
- `agent_state_manager.py` (182 lines) - Agent state tracking

#### MCP Integration
- `mcp_client.py` (603 lines) - MCP client connection management
- `mcp_task_interceptor.py` (228 lines) - Task interception and validation

#### Session & Cache Management
- `cache_manager.py` (302 lines) - Session caching with persistence
- `session_tracker.py` (96 lines) - File modification tracking

#### Security & Validation
- `role_enforcer.py` (298 lines) - Tool permission enforcement
- `task_tracker.py` (316 lines) - Task validation and tracking

#### Documentation System
- `docs_indexer.py` (185 lines) - Automatic documentation indexing

## External Package Requirements

### Python Standard Library (Current Usage)
- **Core modules**: `json`, `os`, `sys`, `re`, `pathlib`
- **Time & Date**: `datetime`, `time`
- **System info**: `socket`, `platform`, `subprocess`, `argparse`
- **Utilities**: `shutil`, `logging`, `hashlib`, `uuid`
- **Type system**: `typing`, `abc`, `collections`

### Third-Party Packages
- `yaml` - Configuration file loading (session_start.py)
- **No external dependencies** for core hook functionality

### Python Version Requirements
- **Minimum**: Python >= 3.8 (script shebangs specify this)
- **Tested with**: Python 3.12.3 (current environment)
- **Architecture**: Leverages modern Python features (typing, abc, pathlib)

## Current Architecture Dependency Graph

### Visual Dependency Structure

```
🎯 MAIN HOOKS (Refactored 2024)
├── 📁 pre_tool_use.py (528 lines) - Factory Pattern
├── 📁 post_tool_use.py (361 lines) - Component-based
├── 📁 session_start.py (991 lines) - Comprehensive Init
├── 📁 user_prompt_submit.py (529 lines)
├── 📁 migrate_data.py (163 lines)
├── 📁 notification.py (134 lines)
└── 📁 stop.py (235 lines)

🔧 CORE UTILS (Foundation - No Dependencies)
├── 🏗️ env_loader.py (116 lines) ← Used by ALL hooks
└── 🏗️ config_factory.py (309 lines) ← Used by ALL hooks

🔄 CONTEXT MANAGEMENT (1,962 lines total)
├── 📋 context_injector.py (740 lines)
├── 📋 context_synchronizer.py (603 lines)
└── 📋 context_updater.py (619 lines)

💡 UNIFIED HINT SYSTEM (549 lines total - Consolidated)
├── 🎯 unified_hint_system.py (410 lines) ← CONSOLIDATED
├── 🔗 hint_bridge.py (47 lines)
├── 📝 mcp_post_action_hints.py (27 lines) ← SIMPLIFIED
└── 🖼️ post_action_display.py (65 lines)

🤖 AGENT & MCP INTEGRATION (1,265 lines total)
├── 👤 agent_context_manager.py (213 lines)
├── 🔄 agent_delegator.py (239 lines)
├── 📊 agent_state_manager.py (182 lines)
├── 🌐 mcp_client.py (603 lines)
└── 🛡️ mcp_task_interceptor.py (228 lines)

🔐 SECURITY & SESSION (1,295 lines total)
├── 🛡️ role_enforcer.py (298 lines)
├── 📋 task_tracker.py (316 lines)
├── ⏱️ session_tracker.py (96 lines)
├── 💾 cache_manager.py (302 lines)
└── 📚 docs_indexer.py (185 lines)
```

### Dependency Flow Chart

```
CORE DEPENDENCIES (Required):
ALL HOOKS ──────► env_loader.py
     │
     └───────────► config_factory.py

DYNAMIC IMPORTS (Optional):
pre_tool_use.py ──┬──► context_injector.py
                  ├──► unified_hint_system.py
                  ├──► role_enforcer.py
                  ├──► mcp_task_interceptor.py
                  ├──► docs_indexer.py
                  └──► session_tracker.py

post_tool_use.py ─┬──► context_updater.py
                  ├──► unified_hint_system.py
                  ├──► agent_state_manager.py
                  └──► docs_indexer.py

session_start.py ─┬──► cache_manager.py
                  └──► mcp_client.py

INTERNAL RELATIONS:
context_injector.py ────► context_synchronizer.py
context_updater.py ─────► context_synchronizer.py
unified_hint_system.py ─► hint_bridge.py
agent_context_manager.py ► agent_delegator.py
```

## Key Findings (Updated Analysis 2024-09-17)

### 1. ✅ Clean Architecture Achieved
- **No circular dependencies** - Utils modules maintain clean separation
- **Factory pattern implemented** - Dynamic imports with proper error handling
- **ABC-based interfaces** - Clear contracts and dependency injection
- **Consolidated hint system** - Multiple modules merged into unified_hint_system.py

### 2. ✅ Successful Refactoring Completed
- **Pre/post hooks refactored** - From 845/345 lines to 528/361 lines
- **Hint system consolidated** - Multiple hint_* modules → unified_hint_system.py
- **Dynamic imports maintained** - Graceful degradation when components missing
- **Modern Python patterns** - Leveraging typing, abc, pathlib throughout

### 3. ✅ Core Infrastructure Solidified
- **env_loader.py** (116 lines) - Environment variable management
- **config_factory.py** (309 lines) - Configuration and messaging
- **All hooks depend on these two** - Stable foundation established

### 4. ✅ Modular Architecture Benefits
- **22 focused modules** - Each with clear, single responsibility
- **Component-based design** - Easy to test and maintain individual pieces
- **Backup preservation** - Original files maintained for rollback (mcp_post_action_hints_backup.py)
- **Test coverage** - Comprehensive test suite in place

## Current Architecture Strengths

### 1. **Maintainable Codebase**
   - Clean separation of concerns
   - Factory patterns enable easy testing
   - Abstract base classes provide clear contracts
   - Comprehensive documentation and tests

### 2. **Resilient Design**
   - Dynamic imports allow graceful degradation
   - Core functionality always available
   - Optional features fail safely
   - Session tracking prevents work disruption

### 3. **Modern Python Practices**
   - Type hints throughout (typing module)
   - Abstract base classes (abc module)
   - Path handling (pathlib)
   - Context managers and proper resource handling

### 4. **Successful Consolidation Examples**
   - **Hint system**: Multiple modules → unified_hint_system.py (410 lines)
   - **MCP integration**: Focused on client + task interceptor
   - **Context management**: Three distinct but coordinated modules
   - **Agent management**: Clear delegation and state handling

## Recommendations Status

### ✅ Completed Successfully
1. **Core infrastructure maintained** - env_loader.py and config_factory.py stable
2. **Hint system consolidated** - unified_hint_system.py created from multiple modules
3. **Factory patterns implemented** - Dynamic imports with proper error handling
4. **Abstract interfaces defined** - ABC-based design throughout

### 🔄 Ongoing Optimizations
1. **Documentation alignment** - This document now reflects actual state
2. **Test coverage expansion** - Comprehensive test suite maintained
3. **Performance monitoring** - Session tracking and caching optimized
4. **Configuration management** - YAML-based config with environment fallbacks

The hooks system has been successfully refactored and is now in a mature, maintainable state.