#!/usr/bin/env python3
"""
Agent Delegation Utility - Bypass Task Tool Limitations

This utility provides direct agent delegation that bypasses the Task tool's
hardcoded master-orchestrator-agent routing.

Usage:
    from utils.agent_delegator import delegate_to_agent
    delegate_to_agent("debugger-agent", "Fix this critical bug")
"""

import json
import sys
from typing import Optional, Dict, Any


class AgentDelegator:
    """Helper class for direct agent delegation without Task tool limitations."""
    
    AVAILABLE_AGENTS = [
        "analytics-setup-agent",
        "branding-agent", 
        "code-reviewer-agent",
        "coding-agent",
        "community-strategy-agent",
        "compliance-scope-agent",
        "core-concept-agent",
        "creative-ideation-agent",
        "debugger-agent",
        "deep-research-agent",
        "design-system-agent",
        "devops-agent",
        "documentation-agent",
        "efficiency-optimization-agent",
        "elicitation-agent",
        "ethical-review-agent",
        "health-monitor-agent",
        "llm-ai-agents-research",
        "marketing-strategy-orchestrator-agent",
        "master-orchestrator-agent",
        "ml-specialist-agent",
        "performance-load-tester-agent",
        "project-initiator-agent",
        "prototyping-agent",
        "root-cause-analysis-agent",
        "security-auditor-agent",
        "system-architect-agent",
        "task-planning-agent",
        "technology-advisor-agent",
        "test-orchestrator-agent",
        "uat-coordinator-agent",
        "ui-specialist-agent"
    ]
    
    def __init__(self):
        self.current_agent = None
    
    def delegate_to_agent(self, agent_name: str, context: str = "") -> Dict[str, Any]:
        """
        Delegate directly to a specific agent, bypassing Task tool limitations.
        
        Args:
            agent_name: Name of the agent to call (without @ prefix)
            context: Optional context or task description
            
        Returns:
            Dict with delegation results
        """
        
        # Validate agent name
        if agent_name not in self.AVAILABLE_AGENTS:
            return {
                "success": False,
                "error": f"Agent '{agent_name}' not available",
                "available_agents": self.AVAILABLE_AGENTS
            }
        
        # For now, return instructions since we can't directly call MCP from here
        return {
            "success": True,
            "agent": agent_name,
            "context": context,
            "delegation_method": "direct_call",
            "instruction": f"Use: mcp__agenthub_http__call_agent('{agent_name}')",
            "note": "This bypasses the Task tool's master-orchestrator routing"
        }
    
    def get_agent_by_specialization(self, task_type: str) -> Optional[str]:
        """
        Get the best agent for a specific task type.
        
        Args:
            task_type: Type of work needed
            
        Returns:
            Agent name or None if no match
        """
        
        specializations = {
            "debug": "debugger-agent",
            "fix": "debugger-agent", 
            "troubleshoot": "debugger-agent",
            "code": "coding-agent",
            "implement": "coding-agent",
            "develop": "coding-agent",
            "test": "test-orchestrator-agent",
            "qa": "test-orchestrator-agent",
            "security": "security-auditor-agent",
            "audit": "security-auditor-agent",
            "docs": "documentation-agent",
            "document": "documentation-agent",
            "deploy": "devops-agent",
            "infrastructure": "devops-agent",
            "ui": "ui-specialist-agent",
            "frontend": "ui-specialist-agent",
            "design": "design-system-agent",
            "architecture": "system-architect-agent",
            "research": "deep-research-agent",
            "analyze": "deep-research-agent"
        }
        
        return specializations.get(task_type.lower())


# Convenience functions for direct use
def delegate_to_agent(agent_name: str, context: str = "") -> Dict[str, Any]:
    """Quick delegation function."""
    delegator = AgentDelegator()
    return delegator.delegate_to_agent(agent_name, context)


def get_agent_for_task(task_type: str) -> Optional[str]:
    """Get best agent for task type."""
    delegator = AgentDelegator()
    return delegator.get_agent_by_specialization(task_type)


def call_direct_agent(agent_name: str) -> str:
    """
    Generate the direct agent calling command.

    Args:
        agent_name: Name of agent to call (without @ prefix)

    Returns:
        The MCP command string to call the agent directly
    """
    # Remove @ prefix if present
    clean_name = agent_name.replace('@', '').replace('-agent', '') + '-agent'
    if clean_name not in AgentDelegator.AVAILABLE_AGENTS:
        available = ', '.join(AgentDelegator.AVAILABLE_AGENTS)
        return f"❌ ERROR: '{clean_name}' not found. Available: {available}"

    return f"mcp__agenthub_http__call_agent('{clean_name}')"


def quick_agent_help(task_description: str) -> str:
    """
    Get agent recommendation and calling command for a task.

    Args:
        task_description: Description of what needs to be done

    Returns:
        Recommended agent and calling command
    """
    task_lower = task_description.lower()

    # Enhanced task type detection
    if any(word in task_lower for word in ['debug', 'fix', 'error', 'bug', 'crash', 'fail']):
        agent = 'debugger-agent'
    elif any(word in task_lower for word in ['code', 'implement', 'build', 'create', 'develop']):
        agent = 'coding-agent'
    elif any(word in task_lower for word in ['test', 'qa', 'verify', 'validate']):
        agent = 'test-orchestrator-agent'
    elif any(word in task_lower for word in ['security', 'audit', 'vulnerability', 'secure']):
        agent = 'security-auditor-agent'
    elif any(word in task_lower for word in ['ui', 'frontend', 'interface', 'design']):
        agent = 'ui-specialist-agent'
    elif any(word in task_lower for word in ['deploy', 'infrastructure', 'devops', 'ci/cd']):
        agent = 'devops-agent'
    elif any(word in task_lower for word in ['document', 'docs', 'guide', 'readme']):
        agent = 'documentation-agent'
    elif any(word in task_lower for word in ['research', 'analyze', 'investigate']):
        agent = 'deep-research-agent'
    else:
        agent = 'master-orchestrator-agent'

    command = call_direct_agent(agent)
    return f"💡 Recommended: {agent}\n📞 Command: {command}"


def print_delegation_guide():
    """Print comprehensive usage guide for agent delegation."""
    print("🤖 AGENT DELEGATION GUIDE")
    print("=" * 50)
    print()
    print("❌ BROKEN: Task tool always calls master-orchestrator-agent")
    print("   Task(subagent_type='coding-agent', prompt='Fix bug')")
    print("   → Routes through master-orchestrator first")
    print()
    print("✅ WORKING: Direct agent calling")
    print("   mcp__agenthub_http__call_agent('debugger-agent')")
    print("   → Calls agent directly, bypasses master-orchestrator")
    print()
    print("🔄 COMPARISON:")
    print("   Task(subagent_type='X') → master-orchestrator → agent X")
    print("   call_agent('X')        → agent X directly")
    print()
    print("📋 AVAILABLE AGENTS:")
    delegator = AgentDelegator()
    for agent in sorted(delegator.AVAILABLE_AGENTS):
        print(f"   • {agent}")
    print()
    print("🎯 QUICK REFERENCE:")
    print("   • Debug/Fix bugs → debugger-agent")
    print("   • Write code → coding-agent")
    print("   • Testing → test-orchestrator-agent")
    print("   • Security → security-auditor-agent")
    print("   • Documentation → documentation-agent")
    print("   • UI/Frontend → ui-specialist-agent")
    print("   • DevOps → devops-agent")
    print()
    print("📝 USAGE EXAMPLES:")
    print("   # Direct debugging:")
    print("   mcp__agenthub_http__call_agent('debugger-agent')")
    print()
    print("   # Direct coding:")
    print("   mcp__agenthub_http__call_agent('coding-agent')")
    print()
    print("   # Direct testing:")
    print("   mcp__agenthub_http__call_agent('test-orchestrator-agent')")
    print()
    print("⚠️  IMPORTANT: Load agent capabilities first, then work directly")
    print("   The call_agent response contains full system_prompt and tools")


if __name__ == "__main__":
    print_delegation_guide()