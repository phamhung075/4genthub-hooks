#!/usr/bin/env python3
"""
Status Line MCP Integration
Provides status line display for Claude Code with MCP task tracking integration.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Add hooks directory to path for imports
hooks_dir = Path(__file__).parent
sys.path.insert(0, str(hooks_dir))

try:
    from utils.task_tracker import get_task_tracker
    from utils.config_factory import ConfigFactory
except ImportError as e:
    # Fallback for minimal status line
    print(f"⚠️ Import error: {e}", file=sys.stderr)
    get_task_tracker = None
    ConfigFactory = None


class StatusLineMCP:
    """Status line provider for Claude Code with MCP integration."""

    def __init__(self):
        """Initialize status line provider."""
        self.config_factory = ConfigFactory() if ConfigFactory else None

    def get_mcp_task_status(self) -> Dict[str, Any]:
        """Get status from MCP task tracking."""
        if not get_task_tracker:
            return {}

        try:
            tracker = get_task_tracker()
            summary = tracker.get_task_summary()

            # Format for status line display
            status_parts = []

            # Show current task if active
            if summary.get('current_task'):
                current = summary['current_task']
                title = current.get('title', 'Untitled')
                # Truncate long titles
                if len(title) > 30:
                    title = title[:27] + "..."
                status_parts.append(f"🔄 {title}")

            # Show task counts
            counts = summary.get('status_counts', {})
            count_parts = []

            if counts.get('in_progress', 0) > 0:
                count_parts.append(f"{counts['in_progress']}▶")
            if counts.get('pending', 0) > 0:
                count_parts.append(f"{counts['pending']}⏸")
            if counts.get('blocked', 0) > 0:
                count_parts.append(f"{counts['blocked']}⚠")
            if counts.get('review', 0) > 0:
                count_parts.append(f"{counts['review']}🔍")

            if count_parts:
                status_parts.append(f"[{' '.join(count_parts)}]")

            # Warning if tasks are blocked
            if summary.get('has_blocked'):
                status_parts.append("⚠️ BLOCKED")

            return {
                'status_text': ' '.join(status_parts) if status_parts else '',
                'task_count': summary.get('total', 0),
                'session_count': summary.get('session_count', 0),
                'has_issues': summary.get('has_blocked', False)
            }

        except Exception as e:
            return {'error': f"Task tracking error: {str(e)}"}

    def get_git_status(self) -> Dict[str, Any]:
        """Get basic git status information."""
        try:
            import subprocess

            # Get current branch
            result = subprocess.run(
                ['git', 'branch', '--show-current'],
                capture_output=True, text=True, cwd=Path.cwd()
            )
            branch = result.stdout.strip() if result.returncode == 0 else "unknown"

            # Check for uncommitted changes
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                capture_output=True, text=True, cwd=Path.cwd()
            )
            has_changes = bool(result.stdout.strip()) if result.returncode == 0 else False

            return {
                'branch': branch,
                'has_changes': has_changes,
                'changes_indicator': "●" if has_changes else ""
            }

        except Exception as e:
            return {'error': f"Git status error: {str(e)}"}

    def get_status_line_config(self) -> Dict[str, Any]:
        """Get status line configuration."""
        if self.config_factory:
            try:
                return self.config_factory.get_status_line_messages()
            except Exception:
                pass
        return {}

    def generate_status_line(self) -> str:
        """Generate the complete status line text."""
        parts = []

        # Add git information
        git_info = self.get_git_status()
        if 'error' not in git_info:
            git_part = f"⎇ {git_info.get('branch', 'main')}"
            if git_info.get('has_changes'):
                git_part += git_info.get('changes_indicator', '')
            parts.append(git_part)

        # Add MCP task information
        mcp_info = self.get_mcp_task_status()
        if 'error' not in mcp_info and mcp_info.get('status_text'):
            parts.append(mcp_info['status_text'])

        # Add timestamp
        timestamp = datetime.now().strftime("%H:%M")
        parts.append(f"🕒 {timestamp}")

        return " | ".join(parts) if parts else f"Claude Code {timestamp}"

    def generate_json_status(self) -> Dict[str, Any]:
        """Generate status information as JSON."""
        return {
            'timestamp': datetime.now().isoformat(),
            'git': self.get_git_status(),
            'mcp_tasks': self.get_mcp_task_status(),
            'config': self.get_status_line_config(),
            'status_line': self.generate_status_line()
        }


def main():
    """Main entry point for status line generation."""
    try:
        status_provider = StatusLineMCP()

        # Check command line arguments
        if len(sys.argv) > 1:
            if sys.argv[1] == '--json':
                # Output JSON format
                status_data = status_provider.generate_json_status()
                print(json.dumps(status_data, indent=2))
                return
            elif sys.argv[1] == '--help':
                print("Usage: status_line_mcp.py [--json|--help]")
                print("  --json    Output status information as JSON")
                print("  --help    Show this help message")
                return

        # Default: output status line text
        status_line = status_provider.generate_status_line()
        print(status_line)

    except Exception as e:
        # Fallback status line
        timestamp = datetime.now().strftime("%H:%M")
        print(f"Claude Code {timestamp} (status error: {str(e)})")
        sys.exit(1)


if __name__ == "__main__":
    main()