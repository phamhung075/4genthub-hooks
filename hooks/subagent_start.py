#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# ///

"""
SubagentStart hook - automatically sets agent state when a sub-agent starts.

When a sub-agent is spawned (via Task tool), Claude Code fires SubagentStart
with agent_type (e.g., "coding-agent"). This hook updates the agent state
so the status line shows the correct agent name instead of "master-orchestrator-agent".
"""

import json
import sys
from pathlib import Path

# Add hooks directory to path
sys.path.insert(0, str(Path(__file__).parent))


def main():
    try:
        input_data = json.load(sys.stdin)

        session_id = input_data.get("session_id", "")
        agent_type = input_data.get("agent_type", "")

        if session_id and agent_type:
            from utils.agent_state_manager import set_current_agent

            set_current_agent(session_id, agent_type)

    except Exception:
        pass  # Never block agent startup

    sys.exit(0)


if __name__ == "__main__":
    main()
