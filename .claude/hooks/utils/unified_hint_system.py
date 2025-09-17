#!/usr/bin/env python3
"""
Unified Hint System - Consolidated hint generation and management.

This module consolidates all hint-related functionality into a single,
maintainable factory pattern system that handles:

1. Post-action hints (after MCP operations)
2. Pre-action hints (before tool usage)
3. Hint analysis and pattern matching
4. Hint bridging and communication
5. Matrix-based hint generation

Replaces multiple separate hint files with a unified architecture.
"""

import json
import yaml
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Any, List, Tuple
from abc import ABC, abstractmethod
import re

# Import configuration factory
try:
    from .config_factory import get_config_factory
except ImportError:
    get_config_factory = None

# Import other utilities with fallbacks
try:
    from .task_tracker import get_task_tracker
except ImportError:
    get_task_tracker = None

try:
    from .session_tracker import is_file_in_session
except ImportError:
    is_file_in_session = None

try:
    from .agent_state_manager import get_current_agent
except ImportError:
    get_current_agent = None


class HintProvider(ABC):
    """Abstract base class for hint providers."""

    @abstractmethod
    def generate_hints(self, context: Dict[str, Any]) -> List[str]:
        """Generate hints based on provided context."""
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Get the name of this hint provider."""
        pass


class PostActionHintProvider(HintProvider):
    """Provides hints after MCP operations are completed."""

    def __init__(self, config_loader=None):
        self.config_loader = config_loader or (get_config_factory() if get_config_factory else None)
        self.load_config()

    def load_config(self):
        """Load post-action hint configuration."""
        self.config = {}
        if self.config_loader:
            try:
                self.config = self.config_loader.load_config('mcp_post_action_hints') or {}
            except Exception:
                pass

        # Default configuration if loading fails
        if not self.config:
            self.config = {
                'task_operations': {
                    'create': ['Remember to track progress', 'Consider breaking into subtasks'],
                    'update': ['Document changes made', 'Update status if needed'],
                    'complete': ['Verify all requirements met', 'Update related tasks']
                },
                'general_reminders': ['Keep documentation updated', 'Test changes thoroughly']
            }

    def generate_hints(self, context: Dict[str, Any]) -> List[str]:
        """Generate post-action hints based on context."""
        hints = []

        # Extract operation details
        tool_name = context.get('tool_name', '')
        tool_input = context.get('tool_input', {})

        # MCP task operation hints
        if 'manage_task' in tool_name:
            action = tool_input.get('action', '')
            hints.extend(self.config.get('task_operations', {}).get(action, []))

        # File operation hints
        if tool_name in ['Write', 'Edit', 'MultiEdit']:
            hints.append('Consider updating related documentation')

        # Add general reminders
        hints.extend(self.config.get('general_reminders', []))

        return hints[:3]  # Limit to 3 most relevant hints

    def get_provider_name(self) -> str:
        return "PostActionHints"


class PreActionHintProvider(HintProvider):
    """Provides hints before tool usage."""

    def __init__(self, config_loader=None):
        self.config_loader = config_loader or (get_config_factory() if get_config_factory else None)
        self.load_config()

    def load_config(self):
        """Load pre-action hint configuration."""
        self.config = {}
        if self.config_loader:
            try:
                self.config = self.config_loader.load_config('mcp_hint_matrix_config') or {}
            except Exception:
                pass

        # Default configuration
        if not self.config:
            self.config = {
                'tool_patterns': {
                    'Write': ['Check if file already exists', 'Consider using Edit instead'],
                    'Edit': ['Ensure file has been read first', 'Backup important changes'],
                    'Bash': ['Verify command safety', 'Check current directory']
                }
            }

    def generate_hints(self, context: Dict[str, Any]) -> List[str]:
        """Generate pre-action hints based on context."""
        hints = []

        tool_name = context.get('tool_name', '')
        tool_input = context.get('tool_input', {})

        # Tool-specific hints
        hints.extend(self.config.get('tool_patterns', {}).get(tool_name, []))

        # Agent role-specific hints
        agent_role = context.get('agent_role', 'unknown')
        if agent_role == 'master-orchestrator-agent':
            hints.append('Consider delegating to specialized agent')
        elif agent_role in ['coding-agent', 'debugger-agent']:
            hints.append('Test changes after implementation')

        return hints[:2]  # Limit to 2 most relevant hints

    def get_provider_name(self) -> str:
        return "PreActionHints"


class PatternAnalysisHintProvider(HintProvider):
    """Provides hints based on pattern analysis."""

    def __init__(self):
        self.patterns = {
            'mcp_task_creation': r'manage_task.*action.*create',
            'file_modification': r'(Write|Edit|MultiEdit)',
            'batch_operations': r'(parallel|multiple|batch)',
            'testing_operations': r'(test|pytest|coverage)'
        }

    def generate_hints(self, context: Dict[str, Any]) -> List[str]:
        """Generate hints based on pattern analysis."""
        hints = []

        # Analyze recent tool usage
        recent_tools = context.get('recent_tools', [])
        text_context = ' '.join(str(tool) for tool in recent_tools)

        # Pattern-based hints
        if re.search(self.patterns['mcp_task_creation'], text_context, re.IGNORECASE):
            hints.append('Consider creating subtasks for complex work')

        if re.search(self.patterns['file_modification'], text_context, re.IGNORECASE):
            hints.append('Update relevant tests and documentation')

        if re.search(self.patterns['batch_operations'], text_context, re.IGNORECASE):
            hints.append('Monitor performance for batch operations')

        return hints

    def get_provider_name(self) -> str:
        return "PatternAnalysis"


class HintBridge:
    """Manages hint communication between different hooks."""

    def __init__(self):
        self.hint_storage_file = Path.cwd() / '.claude' / 'hooks' / 'data' / 'pending_hints.json'
        self.hint_storage_file.parent.mkdir(parents=True, exist_ok=True)
        self.time_window = 300  # 5 minutes

    def store_hint(self, hint: str, category: str = 'general') -> None:
        """Store a hint for later retrieval."""
        try:
            # Load existing hints
            hints = self.load_stored_hints()

            # Add new hint
            new_hint = {
                'content': hint,
                'category': category,
                'timestamp': datetime.now().isoformat(),
                'retrieved': False
            }

            hints.append(new_hint)

            # Clean old hints (older than time window)
            cutoff_time = datetime.now() - timedelta(seconds=self.time_window)
            hints = [h for h in hints if datetime.fromisoformat(h['timestamp']) > cutoff_time]

            # Save hints
            with open(self.hint_storage_file, 'w') as f:
                json.dump(hints, f, indent=2)

        except Exception:
            pass  # Fail silently to not disrupt workflow

    def retrieve_hints(self, category: Optional[str] = None) -> List[str]:
        """Retrieve stored hints."""
        try:
            hints = self.load_stored_hints()

            # Filter by category if specified
            if category:
                hints = [h for h in hints if h['category'] == category]

            # Get unread hints
            unread_hints = [h['content'] for h in hints if not h.get('retrieved', False)]

            # Mark as retrieved
            for hint in hints:
                hint['retrieved'] = True

            # Save updated hints
            with open(self.hint_storage_file, 'w') as f:
                json.dump(hints, f, indent=2)

            return unread_hints

        except Exception:
            return []

    def load_stored_hints(self) -> List[Dict]:
        """Load hints from storage."""
        if not self.hint_storage_file.exists():
            return []

        try:
            with open(self.hint_storage_file, 'r') as f:
                return json.load(f)
        except Exception:
            return []


class UnifiedHintSystem:
    """Main factory class that coordinates all hint providers."""

    def __init__(self):
        self.providers = [
            PostActionHintProvider(),
            PreActionHintProvider(),
            PatternAnalysisHintProvider()
        ]
        self.hint_bridge = HintBridge()

    def generate_post_action_hints(self, tool_name: str, tool_input: Dict, tool_result: Any = None) -> List[str]:
        """Generate hints after a tool action."""
        context = {
            'tool_name': tool_name,
            'tool_input': tool_input,
            'tool_result': tool_result,
            'timestamp': datetime.now().isoformat(),
            'agent_role': self._get_current_agent_role()
        }

        all_hints = []

        # Get hints from post-action provider
        post_provider = next((p for p in self.providers if isinstance(p, PostActionHintProvider)), None)
        if post_provider:
            all_hints.extend(post_provider.generate_hints(context))

        # Get pattern-based hints
        pattern_provider = next((p for p in self.providers if isinstance(p, PatternAnalysisHintProvider)), None)
        if pattern_provider:
            all_hints.extend(pattern_provider.generate_hints(context))

        # Store hints for potential retrieval
        for hint in all_hints[:2]:  # Store top 2 hints
            self.hint_bridge.store_hint(hint, 'post_action')

        return self._deduplicate_hints(all_hints)

    def generate_pre_action_hints(self, tool_name: str, tool_input: Dict) -> List[str]:
        """Generate hints before a tool action."""
        context = {
            'tool_name': tool_name,
            'tool_input': tool_input,
            'timestamp': datetime.now().isoformat(),
            'agent_role': self._get_current_agent_role(),
            'recent_tools': self._get_recent_tool_usage()
        }

        all_hints = []

        # Get hints from pre-action provider
        pre_provider = next((p for p in self.providers if isinstance(p, PreActionHintProvider)), None)
        if pre_provider:
            all_hints.extend(pre_provider.generate_hints(context))

        # Retrieve any stored hints
        stored_hints = self.hint_bridge.retrieve_hints('pre_action')
        all_hints.extend(stored_hints)

        return self._deduplicate_hints(all_hints)

    def _get_current_agent_role(self) -> str:
        """Get current agent role if available."""
        if get_current_agent:
            try:
                return get_current_agent()
            except Exception:
                pass
        return 'unknown'

    def _get_recent_tool_usage(self) -> List[str]:
        """Get recent tool usage for pattern analysis."""
        # This would typically come from a tool usage tracker
        # For now, return empty list
        return []

    def _deduplicate_hints(self, hints: List[str]) -> List[str]:
        """Remove duplicate hints while preserving order."""
        seen = set()
        deduplicated = []
        for hint in hints:
            if hint not in seen:
                seen.add(hint)
                deduplicated.append(hint)
        return deduplicated[:3]  # Limit to 3 hints maximum

    def add_provider(self, provider: HintProvider) -> None:
        """Add a new hint provider."""
        self.providers.append(provider)

    def remove_provider(self, provider_name: str) -> None:
        """Remove a hint provider by name."""
        self.providers = [p for p in self.providers if p.get_provider_name() != provider_name]


# Global instance
_hint_system = None

def get_hint_system() -> UnifiedHintSystem:
    """Get the global hint system instance."""
    global _hint_system
    if _hint_system is None:
        _hint_system = UnifiedHintSystem()
    return _hint_system


# Convenience functions for backward compatibility
def generate_post_action_hints(tool_name: str, tool_input: Dict, tool_result: Any = None) -> List[str]:
    """Generate post-action hints (backward compatibility)."""
    return get_hint_system().generate_post_action_hints(tool_name, tool_input, tool_result)


def generate_pre_action_hints(tool_name: str, tool_input: Dict) -> List[str]:
    """Generate pre-action hints (backward compatibility)."""
    return get_hint_system().generate_pre_action_hints(tool_name, tool_input)


def store_hint_for_later(hint: str, category: str = 'general') -> None:
    """Store a hint for later retrieval (backward compatibility)."""
    get_hint_system().hint_bridge.store_hint(hint, category)


if __name__ == "__main__":
    # Test the unified hint system
    system = get_hint_system()

    # Test post-action hints
    post_hints = system.generate_post_action_hints(
        'manage_task',
        {'action': 'create', 'title': 'Test task'}
    )
    print("Post-action hints:", post_hints)

    # Test pre-action hints
    pre_hints = system.generate_pre_action_hints(
        'Write',
        {'file_path': '/test/file.py'}
    )
    print("Pre-action hints:", pre_hints)