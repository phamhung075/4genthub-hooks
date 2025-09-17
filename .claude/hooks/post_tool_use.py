#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# ///

"""
Refactored Post-tool use hook with factory pattern and clean architecture.

This hook runs after tool execution and provides:
1. Documentation index updates
2. Context synchronization
3. Agent state tracking
4. Hint generation and storage
5. Comprehensive logging

Refactored with:
- Factory pattern for component creation
- Single Responsibility Principle
- Dependency injection
- Clean error handling
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod

# Add hooks directory to path
sys.path.insert(0, str(Path(__file__).parent))


# ============================================================================
# Abstract Base Classes
# ============================================================================

class Component(ABC):
    """Base component interface."""

    @abstractmethod
    def process(self, tool_name: str, tool_input: Dict, tool_result: Any) -> Optional[Any]:
        """Process the tool execution data."""
        pass


class Logger(ABC):
    """Abstract logger interface."""

    @abstractmethod
    def log(self, level: str, message: str, data: Optional[Dict] = None):
        """Log a message with optional data."""
        pass


# ============================================================================
# Component Implementations
# ============================================================================

class FileLogger(Logger):
    """File-based logger implementation."""

    def __init__(self, log_dir: Path, log_name: str):
        self.log_dir = log_dir
        self.log_name = log_name
        self.log_path = log_dir / f"{log_name}.json"
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def log(self, level: str, message: str, data: Optional[Dict] = None):
        """Log to JSON file."""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message,
            'data': data
        }

        # Load existing log
        log_data = []
        if self.log_path.exists():
            try:
                with open(self.log_path, 'r') as f:
                    log_data = json.load(f)
            except:
                pass

        # Append and save
        log_data.append(entry)

        # Keep only last 100 entries
        if len(log_data) > 100:
            log_data = log_data[-100:]

        with open(self.log_path, 'w') as f:
            json.dump(log_data, f, indent=2)


class DocumentationUpdater(Component):
    """Updates documentation index when ai_docs is modified."""

    def __init__(self, ai_docs_path: Path):
        self.ai_docs_path = ai_docs_path

    def process(self, tool_name: str, tool_input: Dict, tool_result: Any) -> Optional[Any]:
        """Update documentation index if needed."""
        modified_file = self._get_modified_file(tool_name, tool_input)

        if modified_file and 'ai_docs' in Path(modified_file).parts:
            try:
                # Import docs indexer dynamically
                from utils.docs_indexer import update_index
                update_index(self.ai_docs_path)
                return {'updated': True, 'path': modified_file}
            except Exception as e:
                return {'updated': False, 'error': str(e)}

        return None

    def _get_modified_file(self, tool_name: str, tool_input: Dict) -> Optional[str]:
        """Extract the file path that was modified."""
        if tool_name in ['Write', 'Edit', 'MultiEdit']:
            return tool_input.get('file_path')
        elif tool_name == 'NotebookEdit':
            return tool_input.get('notebook_path')
        elif tool_name == 'Bash':
            command = tool_input.get('command', '')
            if 'mv ' in command or 'rm ' in command or 'touch ' in command:
                parts = command.split()
                for i, part in enumerate(parts):
                    if part in ['mv', 'rm', 'touch'] and i + 1 < len(parts):
                        return parts[i + 1]
        return None


class HintGenerator(Component):
    """Generates and stores hints for next tool use."""

    def __init__(self, logger: Logger):
        self.logger = logger

    def process(self, tool_name: str, tool_input: Dict, tool_result: Any) -> Optional[Any]:
        """Generate hints based on tool execution."""
        if not tool_name.startswith('mcp__agenthub_http'):
            return None

        try:
            # Import hint generator dynamically
            from utils.unified_hint_system import generate_post_action_hints, store_hint_for_later as store_hint

            hints = generate_post_action_hints(tool_name, tool_input, tool_result)

            if hints:
                action = tool_input.get('action', 'default')
                store_hint(hints, tool_name, action)

                self.logger.log('info', 'Hints generated', {
                    'tool': tool_name,
                    'action': action,
                    'hint_preview': hints[:100] if hints else None
                })

                return {'hints_generated': True, 'hints': hints}

        except Exception as e:
            self.logger.log('error', f'Hint generation failed: {e}')

        return None


class AgentStateTracker(Component):
    """Tracks agent state changes."""

    def __init__(self, logger: Logger):
        self.logger = logger

    def process(self, tool_name: str, tool_input: Dict, tool_result: Any) -> Optional[Any]:
        """Update agent state if call_agent was used."""
        if tool_name != 'mcp__agenthub_http__call_agent':
            return None

        agent_name = tool_input.get('name_agent', '')
        if not agent_name:
            return None

        try:
            # Import agent state manager dynamically
            from utils.agent_state_manager import update_agent_state_from_call_agent

            # Use default session if not provided
            session_id = 'default_session'
            update_agent_state_from_call_agent(session_id, tool_input)

            self.logger.log('info', f'Agent state updated: {agent_name}')
            return {'agent_state_updated': True, 'agent': agent_name}

        except Exception as e:
            self.logger.log('error', f'Agent state update failed: {e}')

        return None


class ContextSynchronizer(Component):
    """Synchronizes context with MCP."""

    def __init__(self, logger: Logger):
        self.logger = logger

    def process(self, tool_name: str, tool_input: Dict, tool_result: Any) -> Optional[Any]:
        """Synchronize context if needed."""
        try:
            # Import context updater dynamically
            from utils.context_updater import update_context_sync

            if update_context_sync(tool_name, tool_input):
                self.logger.log('info', 'Context synchronized')
                return {'context_synced': True}

        except Exception as e:
            self.logger.log('error', f'Context sync failed: {e}')

        return None


# ============================================================================
# Component Factory
# ============================================================================

class ComponentFactory:
    """Factory for creating hook components."""

    @staticmethod
    def create_logger(log_dir: Path, log_name: str = 'post_tool_use') -> Logger:
        """Create a logger instance."""
        return FileLogger(log_dir, log_name)

    @staticmethod
    def create_documentation_updater(ai_docs_path: Path) -> DocumentationUpdater:
        """Create documentation updater."""
        return DocumentationUpdater(ai_docs_path)

    @staticmethod
    def create_hint_generator(logger: Logger) -> HintGenerator:
        """Create hint generator."""
        return HintGenerator(logger)

    @staticmethod
    def create_agent_tracker(logger: Logger) -> AgentStateTracker:
        """Create agent state tracker."""
        return AgentStateTracker(logger)

    @staticmethod
    def create_context_synchronizer(logger: Logger) -> ContextSynchronizer:
        """Create context synchronizer."""
        return ContextSynchronizer(logger)


# ============================================================================
# Main Hook Class
# ============================================================================

class PostToolUseHook:
    """Main post-tool use hook with clean architecture."""

    def __init__(self):
        """Initialize the hook with all components."""
        # Get paths
        from utils.env_loader import get_ai_data_path

        self.log_dir = get_ai_data_path()
        self.ai_docs_path = Path.cwd() / 'ai_docs'

        # Create components using factory
        self.factory = ComponentFactory()
        self.logger = self.factory.create_logger(self.log_dir)

        # Initialize components
        self.components: List[Component] = [
            self.factory.create_documentation_updater(self.ai_docs_path),
            self.factory.create_hint_generator(self.logger),
            self.factory.create_agent_tracker(self.logger),
            self.factory.create_context_synchronizer(self.logger)
        ]

    def execute(self, data: Dict[str, Any]) -> int:
        """Execute the post-tool use hook."""
        tool_name = data.get('tool_name', '')
        tool_input = data.get('tool_input', {})
        tool_result = data.get('tool_result', None)

        # Log the execution
        self.logger.log('info', f'Post-processing: {tool_name}')

        # Check for MCP post-action hints
        output_parts = []
        if tool_name.startswith('mcp__agenthub_http') and tool_result:
            try:
                from utils.unified_hint_system import get_hint_system
                hint_system = get_hint_system()
                # Generate post-action contextual hints based on result
                hints = hint_system.generate_post_action_hints(tool_name, tool_input, tool_result)
                if hints:
                    # hints is a list of strings, extend output_parts instead of append
                    output_parts.extend(hints)
            except Exception as e:
                self.logger.log('error', f'MCP post-action hint matrix failed: {e}')

        # Process through all components
        results = {}
        for component in self.components:
            try:
                result = component.process(tool_name, tool_input, tool_result)
                if result:
                    results[component.__class__.__name__] = result
            except Exception as e:
                self.logger.log('error', f'{component.__class__.__name__} failed: {e}')

        # Output any post-action hints
        if output_parts:
            combined_output = "\n\n".join(output_parts)
            print(combined_output)

        # Log overall results
        if results:
            self.logger.log('info', 'Post-processing completed', results)

        return 0


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Main entry point for the hook."""
    try:
        # Read JSON input from stdin
        input_data = json.load(sys.stdin)

        # Create and execute hook
        hook = PostToolUseHook()
        exit_code = hook.execute(input_data)

        sys.exit(exit_code)

    except json.JSONDecodeError:
        # Handle JSON decode errors gracefully
        sys.exit(0)
    except Exception as e:
        # Log error but exit cleanly
        try:
            from utils.env_loader import get_ai_data_path
            log_dir = get_ai_data_path()
            error_log = log_dir / 'post_tool_use_errors.log'
            with open(error_log, 'a') as f:
                f.write(f"{datetime.now().isoformat()} - Fatal error: {e}\n")
        except:
            pass
        sys.exit(0)


if __name__ == '__main__':
    main()