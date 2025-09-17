#!/usr/bin/env python3
"""
Agent State Management System

Tracks the current AI agent role per session for dynamic status line display.
Provides session-aware agent state management with persistent storage.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

try:
    from .env_loader import get_ai_data_path
except ImportError:
    # Fallback if imported directly
    sys.path.insert(0, str(Path(__file__).parent))
    from env_loader import get_ai_data_path


class AgentStateManager:
    """Manages agent state per session with persistent storage."""
    
    def __init__(self):
        self.state_file = get_ai_data_path() / 'agent_state.json'
    
    def get_current_agent(self, session_id: str) -> str:
        """Get the current agent for a session, defaulting to master-orchestrator-agent."""
        state_data = self._load_state()
        
        session_state = state_data.get(session_id, {})
        return session_state.get('current_agent', 'master-orchestrator-agent')
    
    def set_current_agent(self, session_id: str, agent_name: str) -> None:
        """Set the current agent for a session."""
        state_data = self._load_state()
        
        # Clean agent name (remove @ prefix if present)
        clean_agent_name = agent_name.lstrip('@')
        
        # Update or create session state
        if session_id not in state_data:
            state_data[session_id] = {}
        
        state_data[session_id]['current_agent'] = clean_agent_name
        state_data[session_id]['last_updated'] = datetime.now().isoformat()
        
        self._save_state(state_data)
    
    def get_all_sessions(self) -> dict:
        """Get all session states for debugging/monitoring."""
        return self._load_state()
    
    def cleanup_old_sessions(self, max_sessions: int = 50) -> None:
        """Remove old sessions to prevent state file from growing too large."""
        state_data = self._load_state()
        
        if len(state_data) > max_sessions:
            # Sort by last_updated timestamp and keep only the most recent
            sorted_sessions = sorted(
                state_data.items(),
                key=lambda x: x[1].get('last_updated', ''),
                reverse=True
            )
            
            # Keep only the most recent sessions
            state_data = dict(sorted_sessions[:max_sessions])
            self._save_state(state_data)
    
    def _load_state(self) -> dict:
        """Load agent state from persistent storage."""
        try:
            if not self.state_file.exists():
                return {}

            with open(self.state_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, ValueError, IOError, PermissionError, OSError):
            # Return empty state if file is corrupted, unreadable, or permission denied
            return {}
    
    def _save_state(self, state_data: dict) -> None:
        """Save agent state to persistent storage."""
        try:
            # Ensure directory exists
            self.state_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.state_file, 'w') as f:
                json.dump(state_data, f, indent=2)
        except (IOError, PermissionError, OSError):
            # Fail silently - don't block operations if we can't save state
            pass


# Global instance for easy import
agent_state_manager = AgentStateManager()


def get_current_agent(session_id: str) -> str:
    """Convenience function to get current agent for a session."""
    return agent_state_manager.get_current_agent(session_id)


def set_current_agent(session_id: str, agent_name: str) -> None:
    """Convenience function to set current agent for a session."""
    return agent_state_manager.set_current_agent(session_id, agent_name)


def get_agent_role_from_session(session_id: str) -> str:
    """Get the current agent role for a session based on agent name mapping."""
    if not session_id:
        return "Assistant"

    agent_name = get_current_agent(session_id)

    # Map agent names to human-readable roles
    role_mapping = {
        'coding-agent': 'Coding',
        'debugger-agent': 'Debugging',
        'test-orchestrator-agent': 'Testing',
        'documentation-agent': 'Documentation',
        'master-orchestrator-agent': 'Orchestrating',
        'ui-specialist-agent': 'UI/UX',
        'security-auditor-agent': 'Security',
        'devops-agent': 'DevOps',
        'deep-research-agent': 'Research',
        'performance-load-tester-agent': 'Performance',
        'system-architect-agent': 'Architecture',
        'project-initiator-agent': 'Planning',
        'task-planning-agent': 'Planning',
        'code-reviewer-agent': 'Review',
        'prototyping-agent': 'Prototyping',
        'ml-specialist-agent': 'ML/AI',
        'analytics-setup-agent': 'Analytics',
        'marketing-strategy-orchestrator-agent': 'Marketing',
        'compliance-scope-agent': 'Compliance',
        'ethical-review-agent': 'Ethics',
        'root-cause-analysis-agent': 'Analysis',
        'efficiency-optimization-agent': 'Optimization',
        'health-monitor-agent': 'Monitoring',
        'branding-agent': 'Branding',
        'community-strategy-agent': 'Community',
        'creative-ideation-agent': 'Creative',
        'technology-advisor-agent': 'Advisory',
        'elicitation-agent': 'Requirements',
        'uat-coordinator-agent': 'QA',
        'design-system-agent': 'Design Systems',
        'core-concept-agent': 'Concepts',
        'llm-ai-agents-research': 'AI Research',
        # Default Claude or unknown agents
        'claude': 'Assistant',
        'Claude': 'Assistant'
    }

    return role_mapping.get(agent_name, 'Assistant')


def update_agent_state_from_call_agent(session_id: str, tool_input: dict) -> None:
    """Update agent state when call_agent tool is executed."""
    agent_name = tool_input.get('name_agent', '')
    if agent_name and session_id:
        # Create a new manager instance to pick up any patched paths in tests
        manager = AgentStateManager()
        manager.set_current_agent(session_id, agent_name)


if __name__ == '__main__':
    # Simple test/demo
    import uuid
    
    # Test with a fake session
    test_session = str(uuid.uuid4())
    
    print(f"Initial agent for session {test_session}: {get_current_agent(test_session)}")
    
    # Update agent
    set_current_agent(test_session, 'coding-agent')
    print(f"Updated agent for session {test_session}: {get_current_agent(test_session)}")
    
    # Test cleanup
    agent_state_manager.cleanup_old_sessions(1)
    print("Cleaned up old sessions")