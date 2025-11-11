#!/usr/bin/env python3
"""
Script to generate correct .claude/settings.json with absolute paths.
This prevents the nested ./.claude/hooks/ path issue.
"""

import json
import sys
from pathlib import Path

# Add hooks directory to path
sys.path.insert(0, str(Path(__file__).parent))

from find_project_root import ProjectRootFinder


def generate_settings():
    """Generate settings.json with relative paths for portability."""
    finder = ProjectRootFinder()

    # Find project root
    project_root = finder.find_project_root()
    if not project_root:
        print("Error: Could not find project root", file=sys.stderr)
        sys.exit(1)

    # Get hooks directory
    hooks_dir = project_root / ".claude" / "hooks"
    status_dir = project_root / ".claude" / "status_lines"

    if not hooks_dir.exists():
        print(f"Error: Hooks directory not found: {hooks_dir}", file=sys.stderr)
        sys.exit(1)

    # Generate settings with relative paths for portability
    settings = {
        "permissions": {
            "allow": [
                "Bash(mkdir:*)",
                "Bash(uv:*)",
                "Bash(find:*)",
                "Bash(mv:*)",
                "Bash(grep:*)",
                "Bash(npm:*)",
                "Bash(ls:*)",
                "Bash(cp:*)",
                "Write",
                "Edit",
                "Bash(chmod:*)",
                "Bash(touch:*)",
            ],
            "deny": [],
        },
        "statusLine": {
            "type": "command",
            "command": f"python3 {hooks_dir / 'execute_hook.py'} status_line_mcp.py",
            "padding": 0,
        },
        "includeCoAuthoredBy": False,
        "hooks": {
            "PreToolUse": [
                {
                    "matcher": "",
                    "hooks": [
                        {
                            "type": "command",
                            "command": f"python3 {hooks_dir / 'execute_hook.py'} pre_tool_use.py",
                        }
                    ],
                }
            ],
            "PostToolUse": [
                {
                    "matcher": "",
                    "hooks": [
                        {
                            "type": "command",
                            "command": f"python3 {hooks_dir / 'execute_hook.py'} post_tool_use.py",
                        }
                    ],
                }
            ],
            "Notification": [
                {
                    "matcher": "",
                    "hooks": [
                        {
                            "type": "command",
                            "command": f"python3 {hooks_dir / 'execute_hook.py'} notification.py --notify",
                        }
                    ],
                }
            ],
            "Stop": [
                {
                    "matcher": "",
                    "hooks": [
                        {
                            "type": "command",
                            "command": f"python3 {hooks_dir / 'execute_hook.py'} stop.py --chat",
                        }
                    ],
                }
            ],
            "SubagentStop": [
                {
                    "matcher": "",
                    "hooks": [
                        {
                            "type": "command",
                            "command": f"python3 {hooks_dir / 'execute_hook.py'} subagent_stop.py --notify",
                        }
                    ],
                }
            ],
            "UserPromptSubmit": [
                {
                    "hooks": [
                        {
                            "type": "command",
                            "command": f"python3 {hooks_dir / 'execute_hook.py'} user_prompt_submit.py --log-only --store-last-prompt --name-agent",
                        }
                    ]
                }
            ],
            "PreCompact": [
                {
                    "matcher": "",
                    "hooks": [
                        {
                            "type": "command",
                            "command": f"python3 {hooks_dir / 'execute_hook.py'} pre_compact.py",
                        }
                    ],
                }
            ],
            "SessionStart": [
                {
                    "matcher": "",
                    "hooks": [
                        {
                            "type": "command",
                            "command": f"python3 {hooks_dir / 'execute_hook.py'} session_start.py",
                        }
                    ],
                }
            ],
        },
    }

    return settings, project_root


def main():
    """Main entry point."""
    try:
        # Generate settings
        settings, project_root = generate_settings()

        # Determine output path
        if "--stdout" in sys.argv:
            # Print to stdout
            print(json.dumps(settings, indent=2))
        else:
            # Write to settings.json
            settings_path = project_root / ".claude" / "settings.json"

            # Backup existing settings
            if settings_path.exists():
                backup_path = settings_path.with_suffix(".json.backup")
                backup_path.write_text(settings_path.read_text())
                print(f"Backed up existing settings to: {backup_path}")

            # Write new settings
            with open(settings_path, "w") as f:
                json.dump(settings, f, indent=2)

            print(f"Generated new settings.json with wrapper approach: {settings_path}")
            print(
                "Settings.json now uses execute_hook.py wrapper for robust path resolution!"
            )

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
