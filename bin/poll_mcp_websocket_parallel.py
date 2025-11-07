#!/usr/bin/env python3
"""
MCP WebSocket Multiplexer - Parallel Subtask Monitoring with Pydantic Validation

Connects to MCP WebSocket server and monitors multiple subtasks simultaneously.
Displays aggregated live progress updates and waits for all completions.
Includes comprehensive validation using Pydantic models and detailed debugging.

Usage:
    python poll_mcp_websocket_parallel.py <task_id> --subtask-ids="uuid1 uuid2 uuid3" [--timeout=3600] [--debug]

Features:
    - Type-safe validation using Pydantic models from WebSocket Protocol v2.0
    - Detailed error reporting when data doesn't match expected structure
    - Color-coded validation feedback
    - Debug mode showing full message structure
    - Live progress table for all subtasks

Architecture:
    - Single WebSocket connection to ws://localhost:8000/ws/task-polling
    - Subscribes to multiple subtask events simultaneously
    - Displays live progress updates as they arrive
    - Tracks completion status for each subtask
    - Waits until all subtasks complete
    - Returns aggregated JSON results

This approach replicates Task tool's parallel execution with live output visibility.
"""

import sys
import json
import argparse
import os
import time
from typing import Optional, Dict, Any, List, Set
from datetime import datetime

# Add path to include agenthub_main for Pydantic models
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(project_root, 'agenthub_main/src'))

try:
    from fastmcp.task_management.domain.websocket_protocol import SubtaskCompletePayload
    from pydantic import ValidationError
except ImportError as e:
    # Gracefully handle import errors (e.g., when running outside project)
    print(f"Warning: Could not import Pydantic models: {e}", file=sys.stderr)
    SubtaskCompletePayload = None
    ValidationError = Exception

# Import rich for console (output to stderr)
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.live import Live
    from rich.layout import Layout
except ImportError:
    print("Installing rich library...", file=sys.stderr)
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "rich", "-q"])
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.live import Live
    from rich.layout import Layout

# CRITICAL: All rich UI to stderr, stdout for JSON only
console = Console(stderr=True)

try:
    import websocket
except ImportError:
    console.print("[red]ERROR: websocket-client library not installed[/red]")
    console.print("Install with: pip install websocket-client")
    sys.exit(1)


def validate_subtask_completion_payload(
    data: Dict[str, Any],
    metadata: Dict[str, Any],
    subtask_id: str,
    task_id: str,
    debug: bool = False
) -> tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
    """
    Validate subtask completion payload using Pydantic models.

    Args:
        data: Primary payload data from WebSocket message
        metadata: Metadata from WebSocket message
        subtask_id: Expected subtask ID
        task_id: Parent task ID
        debug: Whether to show detailed debug output

    Returns:
        (is_valid, error_message, validated_data)
    """
    if SubtaskCompletePayload is None:
        if debug:
            console.print("[yellow]⚠️  Pydantic validation skipped (models not available)[/yellow]")
        return True, None, data

    try:
        if debug:
            console.print(f"[cyan]🔍 Validating SubtaskCompletePayload for {subtask_id[:8]}...[/cyan]")
            console.print(f"[dim]Input data keys: {list(data.keys())}[/dim]")
            console.print(f"[dim]Metadata keys: {list(metadata.keys())}[/dim]")

        # Prepare validation data (merge data and metadata for complete picture)
        validation_input = {
            "id": data.get("id") or metadata.get("entity_id") or subtask_id,
            "title": data.get("title") or metadata.get("title") or metadata.get("subtask_title", "Unknown"),
            "status": data.get("status", "done"),
            "task_id": data.get("task_id") or metadata.get("task_id") or task_id,
            "completion_summary": data.get("completion_summary") or metadata.get("completion_summary"),
            "progress_percentage": data.get("progress_percentage", 100),
            "completed_at": data.get("completed_at") or metadata.get("timestamp")
        }

        if debug:
            console.print("[dim]Validation input:[/dim]")
            for key, value in validation_input.items():
                console.print(f"[dim]  {key}: {value}[/dim]")

        # Validate with Pydantic
        validated = SubtaskCompletePayload(**validation_input)

        if debug:
            console.print(f"[green]✅ Validation passed for SubtaskCompletePayload[/green]")

        # Return validated data as dict
        return True, None, validated.model_dump()

    except ValidationError as e:
        # Detailed error reporting
        error_msg = f"Validation failed for SubtaskCompletePayload"

        if debug:
            console.print(f"[red]❌ {error_msg}[/red]")

            # Show detailed errors
            table = Table(title=f"Validation Errors - {subtask_id[:8]}...", show_header=True, header_style="bold red")
            table.add_column("Field", style="cyan")
            table.add_column("Error", style="white")
            table.add_column("Received Value", style="yellow")

            for error in e.errors():
                field = ".".join(str(loc) for loc in error['loc'])
                error_type = error['type']
                received = validation_input.get(field, "MISSING")
                table.add_row(field, f"{error_type}: {error['msg']}", str(received))

            console.print(table)

        return False, error_msg, None

    except Exception as e:
        error_msg = f"Unexpected validation error: {e}"
        if debug:
            console.print(f"[red]❌ {error_msg}[/red]")
        return False, error_msg, None


class SubtaskTracker:
    """Tracks status and progress of individual subtasks"""

    def __init__(self, subtask_id: str, task_id: str):
        self.subtask_id = subtask_id
        self.task_id = task_id
        self.status = "pending"
        self.progress_percentage = 0
        self.title = "Loading..."
        self.last_update = datetime.now()
        self.completion_data = None
        self.is_complete = False
        self.validation_passed = None
        self.validation_error = None

    def update(self, data: Dict[str, Any]):
        """Update tracker with new WebSocket data"""
        self.last_update = datetime.now()

        # Extract status and progress
        self.status = data.get("status", self.status)
        self.progress_percentage = data.get("progress_percentage", self.progress_percentage)
        self.title = data.get("title", self.title)

        # Check if completed
        if self.status in ["done", "completed", "cancelled"]:
            self.is_complete = True
            self.completion_data = data

    def get_status_emoji(self) -> str:
        """Get emoji representation of status"""
        if self.is_complete:
            if self.validation_passed == False:
                return "⚠️"  # Warning if validation failed
            return "✅" if self.status == "done" else "❌"
        elif self.status == "in_progress":
            return "⏳"
        else:
            return "⏸️"

    def get_progress_bar(self, width: int = 20) -> str:
        """Generate progress bar visualization"""
        filled = int(width * (self.progress_percentage / 100))
        bar = "█" * filled + "░" * (width - filled)
        return f"{bar} {self.progress_percentage}%"


def get_mcp_token_from_config() -> Optional[str]:
    """
    Get MCP API token from .mcp.json configuration file.
    This uses the same authentication mechanism as MCP tools and cclaude-wait.

    Tries in order:
    1. ./.mcp.json (current directory)
    2. ~/.config/claude/mcp.json
    3. MCP_JWT_TOKEN environment variable (fallback)

    Returns:
        JWT token string or None if not found
    """
    # Try local .mcp.json first
    local_mcp_path = './.mcp.json'
    if os.path.exists(local_mcp_path):
        try:
            with open(local_mcp_path, 'r') as f:
                mcp_config = json.load(f)
                # Look for agenthub_http server configuration
                if 'mcpServers' in mcp_config:
                    agenthub_config = mcp_config['mcpServers'].get('agenthub_http', {})
                    headers = agenthub_config.get('headers', {})
                    auth_header = headers.get('Authorization', '')

                    # Parse "Bearer <token>" format
                    if auth_header.startswith('Bearer '):
                        token = auth_header[7:].strip()  # Remove "Bearer " prefix
                        return token
        except Exception as e:
            pass  # Silent fail, try next location

    # Try user config directory
    config_mcp_path = os.path.expanduser('~/.config/claude/mcp.json')
    if os.path.exists(config_mcp_path):
        try:
            with open(config_mcp_path, 'r') as f:
                mcp_config = json.load(f)
                if 'mcpServers' in mcp_config:
                    agenthub_config = mcp_config['mcpServers'].get('agenthub_http', {})
                    headers = agenthub_config.get('headers', {})
                    auth_header = headers.get('Authorization', '')

                    if auth_header.startswith('Bearer '):
                        token = auth_header[7:].strip()
                        return token
        except Exception as e:
            pass  # Silent fail, try next location

    # Fallback to environment variable
    token = os.getenv('MCP_JWT_TOKEN')
    if token:
        return token.strip()

    console.print("[red]Error: No MCP token found[/red]")
    console.print(f"Checked: {local_mcp_path}, {config_mcp_path}, MCP_JWT_TOKEN env")
    return None


def create_progress_table(trackers: List[SubtaskTracker]) -> Table:
    """Create rich table showing all subtask progress"""
    table = Table(title="📊 Parallel Subtask Progress", show_header=True, header_style="bold cyan")

    table.add_column("#", style="dim", width=3)
    table.add_column("Status", width=4)
    table.add_column("Subtask ID", style="cyan", width=12)
    table.add_column("Progress", width=25)
    table.add_column("Title", style="white")

    for i, tracker in enumerate(trackers, 1):
        # Truncate subtask ID for display
        short_id = tracker.subtask_id[:8] + "..."

        table.add_row(
            str(i),
            tracker.get_status_emoji(),
            short_id,
            tracker.get_progress_bar(),
            tracker.title
        )

    return table


def monitor_parallel_subtasks(
    task_id: str,
    subtask_ids: List[str],
    timeout: int = 3600,
    server_url: str = "http://localhost:8000",
    debug: bool = False
) -> Dict[str, Any]:
    """
    Monitor multiple subtasks in parallel via WebSocket.

    Returns aggregated results when all subtasks complete.
    """
    # Initialize trackers
    trackers = [SubtaskTracker(sid, task_id) for sid in subtask_ids]
    tracker_map = {t.subtask_id: t for t in trackers}

    # Get MCP token from .mcp.json (same as cclaude-wait)
    mcp_token = get_mcp_token_from_config()
    if not mcp_token:
        error_result = {
            "success": False,
            "error": "No MCP token found",
            "hint": "Configure token in .mcp.json",
            "task_id": task_id
        }
        print(json.dumps(error_result, indent=2))
        sys.exit(1)

    # Build WebSocket endpoint with token in URL (required for WebSocket auth)
    ws_url = server_url.replace("http://", "ws://").replace("https://", "wss://")
    ws_endpoint = f"{ws_url}/ws/task-polling?token={mcp_token}"

    # Display URL without token for security
    console.print(f"[cyan]🔌 Connecting to WebSocket: {ws_url}/ws/task-polling[/cyan]")

    try:
        # Connect to WebSocket (token is in URL, no header needed)
        ws = websocket.create_connection(
            ws_endpoint,
            timeout=10
        )

        console.print("[green]✅ Connected[/green]")

        # Subscribe to all subtask events
        for subtask_id in subtask_ids:
            subscribe_message = {
                "type": "subscribe",
                "scope": "subtask",
                "entity_id": subtask_id
            }
            ws.send(json.dumps(subscribe_message))

        console.print(f"[green]✅ Subscribed to {len(subtask_ids)} subtasks[/green]")
        console.print("")
        console.print("[yellow]⏳ Starting WebSocket monitoring loop...[/yellow]")

        # Start monitoring with live display
        start_time = time.time()
        completed_count = 0

        with Live(create_progress_table(trackers), refresh_per_second=4, console=console) as live:
            while True:
                # Check timeout
                elapsed = time.time() - start_time
                if elapsed > timeout:
                    console.print(f"[red]⏰ Timeout after {timeout}s[/red]")
                    break

                # Check if all complete
                if all(t.is_complete for t in trackers):
                    console.print("[green]🎉 All subtasks completed![/green]")
                    break

                # Receive WebSocket message (with timeout)
                ws.settimeout(1.0)
                try:
                    message_str = ws.recv()
                    message = json.loads(message_str)

                    # Parse message based on v2.0 format (same as cclaude-wait)
                    if message.get("version") == "2.0":
                        payload = message.get("payload", {})
                        entity = payload.get("entity")
                        action = payload.get("action")
                        # primary can be None for progress events, fallback to empty dict
                        data = payload.get("data", {}).get("primary") or {}
                        metadata = message.get("metadata", {})

                        # Check if this is a subtask event
                        if entity == "subtask":
                            event_subtask_id = metadata.get("entity_id")

                            # DEBUG: Log received message
                            console.print(f"[dim]📨 Message: entity={entity}, action={action}, id={event_subtask_id[:8] if event_subtask_id else 'none'}..., status={metadata.get('status', 'unknown')}[/dim]")

                            if event_subtask_id and event_subtask_id in tracker_map:
                                tracker = tracker_map[event_subtask_id]
                                old_status = tracker.is_complete

                                # Update tracker with data and metadata
                                update_data = {
                                    "status": data.get("status", metadata.get("status", tracker.status)),
                                    "progress_percentage": data.get("progress_percentage", metadata.get("progress_percentage", tracker.progress_percentage)),
                                    "title": metadata.get("title", data.get("title", tracker.title))
                                }
                                tracker.update(update_data)

                                # Store full completion data when subtask completes
                                if action == "completed" or update_data["status"] in ["done", "completed"]:
                                    # VALIDATE COMPLETION PAYLOAD using Pydantic
                                    is_valid, error_msg, validated_data = validate_subtask_completion_payload(
                                        data, metadata, event_subtask_id, tracker.task_id, debug
                                    )

                                    # Store validation result
                                    tracker.validation_passed = is_valid
                                    tracker.validation_error = error_msg

                                    if not is_valid and debug:
                                        console.print(f"[yellow]⚠️  Subtask {event_subtask_id[:8]}... validation failed: {error_msg}[/yellow]")
                                        console.print(f"[yellow]Proceeding with best-effort data extraction[/yellow]")

                                    # Use validated data if available, otherwise fallback to metadata
                                    final_data = validated_data if validated_data else data

                                    # Build complete tracker data (with validation metadata)
                                    tracker.completion_data = {
                                        "id": final_data.get("id", event_subtask_id),
                                        "status": final_data.get("status", update_data["status"]),
                                        "progress_percentage": final_data.get("progress_percentage", 100),
                                        "title": final_data.get("title", tracker.title),
                                        "task_id": final_data.get("task_id", tracker.task_id),
                                        "completion_summary": final_data.get("completion_summary", metadata.get("completion_summary", "")),
                                        "completed_at": final_data.get("completed_at", metadata.get("timestamp")),
                                        # Additional metadata fields (not in Pydantic model but useful for CLI)
                                        "testing_notes": metadata.get("testing_notes", ""),
                                        "assignees": metadata.get("assignees", []),
                                        "progress_history": metadata.get("progress_history", {}),
                                        "progress_count": metadata.get("progress_count", 0),
                                        "insights_found": metadata.get("insights_found", []),
                                        "blockers": metadata.get("blockers", []),
                                        "description": metadata.get("description", ""),
                                        "impact_on_parent": metadata.get("impact_on_parent", ""),
                                        "challenges_overcome": metadata.get("challenges_overcome", []),
                                        "deliverables": metadata.get("deliverables", []),
                                        # Validation metadata
                                        "validation_passed": is_valid,
                                        "validation_error": error_msg if not is_valid else None
                                    }

                                # Track completion
                                if not old_status and tracker.is_complete:
                                    completed_count += 1
                                    console.print(f"[green]✅ Subtask {event_subtask_id[:8]}... completed! ({completed_count}/{len(trackers)})[/green]")

                                # Update live display
                                live.update(create_progress_table(trackers))

                except websocket.WebSocketTimeoutException:
                    # Timeout is expected, just refresh display
                    live.update(create_progress_table(trackers))
                    continue

        # Close WebSocket
        ws.close()

        # Build aggregated results
        results = {
            "success": all(t.is_complete and t.status == "done" for t in trackers),
            "task_id": task_id,
            "subtask_count": len(trackers),
            "completed_count": completed_count,
            "subtasks": []
        }

        for tracker in trackers:
            subtask_result = {
                "subtask_id": tracker.subtask_id,
                "status": tracker.status,
                "progress_percentage": tracker.progress_percentage,
                "title": tracker.title,
                "is_complete": tracker.is_complete
            }

            if tracker.completion_data:
                subtask_result["completion_data"] = tracker.completion_data

            results["subtasks"].append(subtask_result)

        # Output JSON to stdout for cclaude-wait-parallel parsing
        print(json.dumps(results, indent=2))

        return results

    except websocket.WebSocketException as e:
        console.print(f"[red]❌ WebSocket error: {e}[/red]")
        error_result = {
            "success": False,
            "error": str(e),
            "task_id": task_id
        }
        print(json.dumps(error_result, indent=2))
        sys.exit(1)

    except Exception as e:
        console.print(f"[red]❌ Unexpected error: {e}[/red]")
        error_result = {
            "success": False,
            "error": str(e),
            "task_id": task_id
        }
        print(json.dumps(error_result, indent=2))
        sys.exit(1)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Monitor multiple MCP subtasks in parallel via WebSocket"
    )
    parser.add_argument("task_id", help="Parent task UUID")
    parser.add_argument(
        "--subtask-ids",
        required=True,
        help="Space-separated subtask UUIDs (e.g., 'uuid1 uuid2 uuid3')"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=3600,
        help="Maximum wait time in seconds (default: 3600)"
    )
    parser.add_argument(
        "--server-url",
        default="http://localhost:8000",
        help="MCP server URL (default: http://localhost:8000)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="Enable debug logging with detailed validation feedback"
    )

    args = parser.parse_args()

    # Parse subtask IDs
    subtask_ids = args.subtask_ids.strip().split()

    if not subtask_ids:
        console.print("[red]ERROR: No subtask IDs provided[/red]")
        sys.exit(1)

    # Show header
    header_text = (
        f"[bold cyan]MCP WebSocket Multiplexer[/bold cyan]\n\n"
        f"📋 Task ID: {args.task_id}\n"
        f"📝 Monitoring {len(subtask_ids)} subtasks\n"
        f"⏱️  Timeout: {args.timeout}s"
    )

    if args.debug:
        pydantic_status = "✅ Available" if SubtaskCompletePayload is not None else "❌ Not available"
        header_text += f"\n🐛 Debug: Enabled\n🔍 Pydantic validation: {pydantic_status}"

    console.print(Panel.fit(header_text, border_style="cyan"))
    console.print("")

    # Monitor subtasks
    monitor_parallel_subtasks(
        task_id=args.task_id,
        subtask_ids=subtask_ids,
        timeout=args.timeout,
        server_url=args.server_url,
        debug=args.debug
    )


if __name__ == "__main__":
    main()
