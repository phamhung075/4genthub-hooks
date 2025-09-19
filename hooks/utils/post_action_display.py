#!/usr/bin/env python3
"""
Post-Action Display - Formats hints for display in Claude's interface.

This module attempts to format hints in a way that Claude will display,
similar to how session-start-hook is displayed.
"""

import json
import sys
from datetime import datetime
from typing import Optional

def format_for_claude_display(hints: str, tool_name: str = None, action: str = None) -> str:
    """
    Format hints for display in Claude's interface.
    
    Uses system-reminder format which Claude recognizes.
    """
    
    # Extract the content without wrapper if present
    content = hints
    if '<system-reminder>' in content:
        content = content.replace('<system-reminder>', '').replace('</system-reminder>', '').strip()
    
    # Use system-reminder format that Claude recognizes
    system_reminder_format = f"<system-reminder>\n{content}\n</system-reminder>"
    
    # Method 2: Try JSON structure that Claude might recognize
    json_format = {
        "type": "post_action_hints",
        "content": content,
        "timestamp": datetime.now().isoformat(),
        "from_tool": tool_name,
        "from_action": action
    }
    
    # Method 3: Try plain output with special marker
    plain_format = f"\n{'='*60}\n📌 POST-ACTION REMINDERS:\n{content}\n{'='*60}\n"
    
    # Return system-reminder format (Claude recognizes this)
    return system_reminder_format


def output_to_claude(message: str, output_format: str = "hook"):
    """
    Output message to Claude in the specified format.
    
    Args:
        message: The message to output
        output_format: Format to use - "hook", "json", or "plain"
    """
    if output_format == "json":
        output = {
            "type": "post_action_hints",
            "content": message,
            "timestamp": datetime.now().isoformat()
        }
        print(json.dumps(output))
    elif output_format == "hook":
        # Use system-reminder format instead of custom post-action-hook
        print(f"<system-reminder>\n{message}\n</system-reminder>")
    else:
        print(message)
    
    sys.stdout.flush()