#!/usr/bin/env python3
"""
Agent Context Manager - Runtime Agent Role Switching

This module manages agent context switching within the same Claude session,
allowing the master orchestrator to switch to sub-agent mode and back.
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any


class AgentContextManager:
    """Manages runtime agent context switching within Claude sessions."""
    
    def __init__(self):
        self.context_file = Path(".claude/runtime_agent_context.json")
        self.context_file.parent.mkdir(exist_ok=True)
        
    def set_agent_context(self, agent_name: str, context_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Set the current agent context for runtime switching.
        
        Args:
            agent_name: Name of the agent to switch to
            context_data: Additional context data from agent loading
            
        Returns:
            Context instructions for the agent
        """
        
        # Create agent context
        agent_context = {
            "current_agent": agent_name,
            "timestamp": datetime.now().isoformat(),
            "context_data": context_data or {},
            "session_type": "runtime_switched"
        }
        
        # Save to runtime context file
        try:
            with open(self.context_file, 'w') as f:
                json.dump(agent_context, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save agent context: {e}")
        
        # Return appropriate context instructions
        return self._get_agent_instructions(agent_name)
    
    def get_current_agent_context(self) -> Optional[Dict[str, Any]]:
        """Get the current agent context if any."""
        try:
            if self.context_file.exists():
                with open(self.context_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return None
    
    def clear_agent_context(self):
        """Clear the current agent context (return to master orchestrator)."""
        try:
            if self.context_file.exists():
                self.context_file.unlink()
        except Exception:
            pass
    
    def _get_agent_instructions(self, agent_name: str) -> Dict[str, Any]:
        """Get specific instructions for an agent."""
        
        # Base instructions for all sub-agents
        base_instructions = {
            "session_type": "sub-agent",
            "role": agent_name,
            "instructions": [
                f"🤖 **RUNTIME AGENT SWITCH**: You are now operating as {agent_name}",
                "",
                "**IMPORTANT CONTEXT CHANGE**:",
                f"- You are now a specialized {agent_name}, NOT the master orchestrator",
                "- Focus on your specialized work",
                "- Use your loaded agent capabilities",
                "- Do NOT call master-orchestrator-agent again",
                "- Do NOT delegate to other agents",
                "- Complete the specific task assigned to you",
                "",
                f"**Agent Role**: {agent_name}",
                f"**Session Mode**: Runtime-switched sub-agent",
                ""
            ]
        }
        
        # Agent-specific instructions
        agent_specific = {
            "debugger-agent": [
                "🐛 **DEBUGGING SPECIALIST**:",
                "- Analyze bugs and errors systematically",
                "- Use debugging tools and techniques",
                "- Fix issues and create tests",
                "- Document your findings"
            ],
            "coding-agent": [
                "💻 **CODING SPECIALIST**:",
                "- Implement features and functionality",
                "- Write clean, efficient code",
                "- Follow best practices and patterns",
                "- Create comprehensive tests"
            ],
            "test-orchestrator-agent": [
                "🧪 **TESTING SPECIALIST**:",
                "- Design and implement test strategies",
                "- Create unit, integration, and E2E tests",
                "- Ensure code quality and coverage",
                "- Validate functionality thoroughly"
            ],
            "security-auditor-agent": [
                "🔒 **SECURITY SPECIALIST**:",
                "- Conduct security audits and reviews",
                "- Identify vulnerabilities and risks",
                "- Implement security best practices",
                "- Ensure compliance with standards"
            ],
            "documentation-agent": [
                "📚 **DOCUMENTATION SPECIALIST**:",
                "- Create comprehensive documentation",
                "- Write clear technical guides",
                "- Update API documentation",
                "- Maintain knowledge bases"
            ],
            "ui-specialist-agent": [
                "🎨 **UI/UX SPECIALIST**:",
                "- Design user interfaces and experiences",
                "- Implement frontend components",
                "- Ensure responsive and accessible design",
                "- Optimize user interactions"
            ],
            "devops-agent": [
                "⚙️ **DEVOPS SPECIALIST**:",
                "- Manage deployment and infrastructure",
                "- Configure CI/CD pipelines",
                "- Monitor system performance",
                "- Handle operational concerns"
            ]
        }
        
        # Add agent-specific instructions
        if agent_name in agent_specific:
            base_instructions["instructions"].extend(agent_specific[agent_name])
        
        base_instructions["instructions"].extend([
            "",
            "**To return to master orchestrator mode**:",
            "Use: clear_agent_context() or switch back manually"
        ])
        
        return base_instructions
    
    def format_context_for_claude(self, agent_context: Dict[str, Any]) -> str:
        """Format agent context for Claude's consumption."""
        instructions = agent_context.get("instructions", [])
        return "\n".join(instructions)


# Convenience functions for easy use
def switch_to_agent(agent_name: str, context_data: Dict[str, Any] = None) -> str:
    """Switch to a specific agent and return context instructions."""
    manager = AgentContextManager()
    context = manager.set_agent_context(agent_name, context_data)
    return manager.format_context_for_claude(context)


def get_current_agent() -> Optional[str]:
    """Get the currently active agent name."""
    manager = AgentContextManager()
    context = manager.get_current_agent_context()
    return context.get("current_agent") if context else None


def clear_agent_context():
    """Clear agent context and return to master orchestrator mode."""
    manager = AgentContextManager()
    manager.clear_agent_context()
    return "🎯 **RETURNED TO MASTER ORCHESTRATOR MODE**\n\nYou are now back to being the master orchestrator."


def get_agent_context_instructions() -> Optional[str]:
    """Get current agent context instructions if any."""
    manager = AgentContextManager()
    context = manager.get_current_agent_context()
    if context:
        return manager.format_context_for_claude(context)
    return None


if __name__ == "__main__":
    # Test the agent context manager
    print("🤖 Agent Context Manager Test")
    print("=" * 40)
    
    # Test switching to debugger agent
    print("\n1. Switching to debugger-agent:")
    context = switch_to_agent("debugger-agent")
    print(context)
    
    # Test getting current agent
    print(f"\n2. Current agent: {get_current_agent()}")
    
    # Test clearing context
    print("\n3. Clearing context:")
    print(clear_agent_context())
    
    print(f"\n4. Current agent after clear: {get_current_agent()}")