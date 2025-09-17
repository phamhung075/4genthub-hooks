#!/usr/bin/env python3
"""
Agent Helper Functions - Simple functions for runtime agent management
"""

from .agent_context_manager import switch_to_agent, clear_agent_context, get_current_agent


def switch_to_debugger():
    """Quick switch to debugger agent."""
    return switch_to_agent("debugger-agent")


def switch_to_coding():
    """Quick switch to coding agent."""  
    return switch_to_agent("coding-agent")


def switch_to_tester():
    """Quick switch to test orchestrator agent."""
    return switch_to_agent("test-orchestrator-agent")


def switch_to_security():
    """Quick switch to security auditor agent."""
    return switch_to_agent("security-auditor-agent")


def switch_to_docs():
    """Quick switch to documentation agent."""
    return switch_to_agent("documentation-agent")


def switch_to_ui():
    """Quick switch to UI specialist agent."""
    return switch_to_agent("ui-specialist-agent")


def switch_to_devops():
    """Quick switch to DevOps agent."""
    return switch_to_agent("devops-agent")


def back_to_orchestrator():
    """Return to master orchestrator mode."""
    return clear_agent_context()


def current_agent():
    """Get current agent name."""
    agent = get_current_agent()
    return agent or "master-orchestrator-agent"


def agent_status():
    """Get current agent status."""
    agent = get_current_agent()
    if agent:
        return f"🤖 Current Agent: {agent} (runtime-switched)"
    else:
        return "🎯 Current Mode: Master Orchestrator"


# Aliases for convenience
switch_back = back_to_orchestrator
who_am_i = current_agent
status = agent_status